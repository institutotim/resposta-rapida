# encoding: utf-8
import datetime
from django.db import models
from forms.rpcbase import RPCBase
from picklefield import PickledObjectField
from raven.contrib.django.raven_compat.models import client as raven
import logging

logger = logging.getLogger("pastoral")

class SubmissionException(Exception):
    pass


class Submission(models.Model):
    """Representa uma submissão"""

    MAX_IDENTITY_SIZE = 250

    # Status da submissão
    CONFIRMED = 0
    NOT_CONFIRMED = 1
    SENT_TO_REMOTE = 2
    CANCELED = 3
    INVALID = 4

    STATUS_TYPES = ((CONFIRMED, "Confirmado"),
                    (NOT_CONFIRMED, "Não confirmado"),
                    (SENT_TO_REMOTE, "Enviado ao servidor remoto"),
                    (CANCELED, "Cancelado"),
                    (INVALID, "Inválido")
    )

    # Tipos da submissão
    TYPE_SMS = "SMS"
    TYPE_WEB = "WEB"
    TYPE_JAVA = "JAVA"
    TYPE_WAP = "WAP"

    RPC_RESPONSE = {
        "cancel": CANCELED,
        "save": CONFIRMED,
        "wait": NOT_CONFIRMED
    }

    # Estado de processamento remoto
    REMOTE_PROCESSING = 0
    REMOTE_PENDING = 1
    REMOTE_PROCESSED = 2
    REMOTE_SAVED = 3

    identity = models.CharField(max_length=MAX_IDENTITY_SIZE)
    """Contém o valor usado para identificação do usuário. Em caso de SMS por exemplo, o número de telefone."""

    status = models.SmallIntegerField(default=1)
    """O status da submissão."""

    form = models.ForeignKey('Form')
    """O formulário que essa submissão pertence."""

    data = PickledObjectField()
    """Os dados enviados nessa submissão."""

    created = models.DateTimeField(blank=True)
    """Data que essa submissão foi recebida."""

    context = PickledObjectField(blank=True)
    """
    Contexto de variáveis disponíveis durante o processamento dessa submissão,
    pode ser usada em respostas de confirmação.
    """

    sub_type = models.CharField(max_length=4)
    """Tipo de submissão"""

    remote_last_update = models.DateTimeField(null=True)
    """Tempo que o estado de processmento remoto foi alterado"""

    remote_status = models.SmallIntegerField(default=REMOTE_PROCESSING)
    """Estado atual de processamento remoto"""

    def save(self, *args, **kwargs):
        """Adiciona valores padrões"""
        if not self.id:
            self.created = datetime.datetime.now()

        super(Submission, self).save(*args, **kwargs)

    def update_remote_status(self, status):
        """Atualiza o estado remoto, colocando a nova data de atualização"""

        self.remote_last_update = datetime.datetime.now()
        self.remote_status = status
        self.save()

    def set_status(self, status):
        """Método auxiliar para alterar o estado da submissão."""
        self.status = status
        self.save()

    def confirm(self, message):
        """Chamado pelo sistema para processar mensagens de confirmação"""
        if self.status != Submission.NOT_CONFIRMED:
            raise SubmissionException("O status dessa submissão não pode ser confirmado"
                                      " pois não se encontra como NOT_CONFIRMED (1).")

        answer, extra_vars = self.process_confirmation(message)

        if extra_vars:
            self.context = dict(self.context.items() + extra_vars.items())

        return self.form.process_answer_template(answer, self.context)

    def process_confirmation(self, message):
        """Realiza o processamento de mensagens de confirmação, retorna uma resposta ao RapidSMS."""
        message = message.strip().lower()
        action, answer, new_value, extra_vars = self.form.process_confirmation_conditions(message)

        if answer:
            self.status = action or Submission.CONFIRMED
            self.save()

            return answer, extra_vars

        if new_value:  # ?
            message = new_value

        positive_confirmation_list = self.form.positive_confirmation_list
        negative_confirmation_list = self.form.negative_confirmation_list

        if message in positive_confirmation_list:
            self.status = Submission.CONFIRMED
            self.save()
            self.remote_save_submission()
            return self.form.ans_positive_confirmation, extra_vars
        elif message in negative_confirmation_list:
            self.status = Submission.CANCELED
            self.save()
            self.remote_save_submission()
            return self.form.ans_negative_confirmation, extra_vars
        else:
            try:
                return self.form.ans_unknown_confirmation % (
                    self.form.positive_confirmation_list[0], self.form.negative_confirmation_list[0]), extra_vars
            except TypeError:
                return self.form.ans_unknown_confirmation, extra_vars

    def remote_save_submission(self):
        """Tenta salvar a submissão no servidor remoto"""
        try:
            rpc = RPCBase()

            resp = rpc.save_submission(self.id, self.sub_type, self.identity, self.created,
                                       self.id, self.context, self.status)

            if "action" in resp and resp["action"] == "delete":
                self.delete()
            elif resp["success"]:
                self.set_status(Submission.SENT_TO_REMOTE)
                self.update_remote_status(Submission.REMOTE_SAVED)
            else:
                self.update_remote_status(Submission.REMOTE_PENDING)
        except:
            self.update_remote_status(Submission.REMOTE_PENDING)

    def process_external_response(self, resp):
        """Processa a resposta da chamada RPC"""

        if resp["action"] != "continue":
            if resp["action"] == "delete":
                self.delete()
            else:
                self.status = Submission.RPC_RESPONSE[resp["action"]]

        answer = None

        if "answer" in resp:
            answer = resp["answer"]

        self.update_remote_status(Submission.REMOTE_PROCESSED)

        return answer

    def remote_process_submission(self):
        """Realiza a chamada process_submission no servidor RPC e atualiza o status da submissão conforme necessário"""

        try:
            rpc = RPCBase()
            resp = rpc.process_submission(self.id, self.sub_type, self.identity, self.created,
                                          self.form.id, self.context)

            return self.process_external_response(resp)
        except Exception:
            raven.captureException()
            return None


    @staticmethod
    def retry_pending():
        pending_submissions = Submission.objects.filter(remote_status=Submission.REMOTE_PENDING)

        for submission in pending_submissions:
            submission.remote_save_submission()

    @staticmethod
    def get_unconfirmed(identity):
        """Método auxiliar que retorna uma submissão não confirmada atrelada a uma identificação de usuário"""
        return Submission.objects.filter(identity=identity, status=Submission.NOT_CONFIRMED)[0]


    @staticmethod
    def has_confirmation_pending(identity):
        """Verifica se um usuario possui uma submissão pendente que ainda não foi confirmada"""
        return Submission.objects.filter(identity=identity, status=Submission.NOT_CONFIRMED).count() > 0

    class Meta:
        app_label = "forms"