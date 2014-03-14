# encoding: utf-8
from django.core.exceptions import ValidationError
from django.db import models
from django.template import Template, Context
from annoying.functions import get_object_or_None
from pastoral.models.configuration import Config
from picklefield import PickledObjectField
from condition import Condition
from submission import Submission
from field import InvalidFieldValue, Field
import itertools


class Form(models.Model):
    """Representa um formulário, contém campos, respostas padrões e condições a serem aplicadas ao texto completo"""

    name = models.CharField(max_length=250, blank=False)
    """Nome do formulário (usado para identificação no admin)"""

    keyword = models.CharField(max_length=50, blank=False)
    """Palavra-chave do formulário, usada pelo usuário"""

    separator = models.CharField(max_length=1, default=".")
    """Separador de campos"""

    main = models.BooleanField(default=False)
    """Caso seja verdadeiro, esse formulário é considerado 'principal'"""

    requires_confirmation = models.BooleanField(default=False)
    """Verdadeiro caso o formulário precise de verificação"""

    positive_confirmation_list = PickledObjectField()
    """Array conntendo uma lista de valores que são aceitos para confirmação positiva da submissão"""

    negative_confirmation_list = PickledObjectField()
    """Array conntendo uma lista de valores que são aceitos para confirmação negative (cancelamento) da submissão"""

    ans_incorrect_num_fields = models.CharField(blank=True, max_length=Config.get("max_sms_length"),
                                                default=Config.get("ans_incorrect_num_fields"))
    """Resposta enviado ao usuário caso o número de campos enviados seja diferente ao número de campos do formulario"""

    ans_positive_confirmation = models.CharField(blank=True, max_length=Config.get("max_sms_length"),
                                                 default=Config.get("ans_positive_confirmation"))
    """Resposta enviado ao usuário para confirmações positivas"""

    ans_negative_confirmation = models.CharField(blank=True, max_length=Config.get("max_sms_length"),
                                                 default=Config.get("ans_negative_confirmation"))
    """Resposta enviado ao usuário para confirmações negativas"""

    ans_unknown_confirmation = models.CharField(blank=True, max_length=Config.get("max_sms_length"),
                                                default=Config.get("ans_unknown_confirmation"))
    """Resposta enviado ao usuário caso o código de confirmação não estejam nas listas positivas e negativas"""

    ans_default = models.CharField(blank=True, max_length=Config.get("max_sms_length"),
                                   default=Config.get("ans_confirmed"))
    """Resposta enviada ao usuário caso o formulário não requeira confirmação"""

    ans_waiting_confirmation = models.CharField(blank=True, max_length=Config.get("max_sms_length"),
                                                default=Config.get("ans_waiting_confirmation"))
    """Resposta enviada ao usuário após uma submissão correta que esteja aguardado confirmação"""

    conditions = models.ManyToManyField(Condition)
    """Condições que do formulário, é aplicada ao texto completo do SMS."""

    confirmation_conditions = models.ManyToManyField(Condition, related_name="form_confirmations")
    """Condições do formulário para respostas de confirmação"""

    enable_sms = models.BooleanField(default=True)
    enable_web = models.BooleanField(default=True)
    enable_wap = models.BooleanField(default=True)
    enable_java = models.BooleanField(default=True)

    def process_submission(self, sms, sub_type, return_submission=False):
        """Método que realiza o processamento de submissões novas e retorna uma resposta ao usuário"""

        # Defaults
        submission_status = Submission.NOT_CONFIRMED if self.requires_confirmation else Submission.CONFIRMED

        default_answer = self.ans_default or Config.get("ans_confirmed") \
            if not self.requires_confirmation else self.ans_waiting_confirmation

        # Form conditions
        action, answer, new_value, extra_vars = Condition.process_conditions(self.conditions.all(), sms.text)

        if new_value:
            sms.text = new_value

        if action == Submission.CANCELED and answer:
            self.save_submission(sms, action)
            return answer

        # Fields parsing
        text_fields = self.split_fields(sms.text)

        if len(text_fields) != self.fields.count():
            submission = self.save_submission(sms, Submission.INVALID, text_fields, raw=True)
            processed_answer = self.ans_incorrect_num_fields
        else:

            instance_fields = self.instatiate_fields(text_fields)

            # Fields conditions
            action, answer = self.process_field_conditions(instance_fields)
            if action:
                submission_status = action

            context = self.get_context(instance_fields)
            if context and extra_vars:
                context = dict(context.items() + extra_vars.items())

            submission = self.save_submission(sms, submission_status, instance_fields, sub_type=sub_type,
                                              context=context)

            # Remote server calls
            r_answer = submission.remote_process_submission()

            if r_answer:
                answer = r_answer
            else:
                if not answer:
                    answer = self.process_answer_template(default_answer, context)

            processed_answer = self.process_answer_template(answer, context)

        if return_submission:
            return processed_answer, submission
        else:
            return processed_answer

    def get_context(self, instance_fields):
        """
        Retorna o contexto de uma submissão
        O contexto contém todas as variáveis retornadas em chamadas externas (RPC), além de valores dos campos do
        formulário. Essa variáveis podem ser usadas em todas as mensagens retornadas diretamente pelo RapidSMS, usando
        a notação de variável de template padrão do Django: {{variavel}}.
        """
        context = {}

        for field in instance_fields:
            context[field.name] = field.get_value()
            extra = field.get_extra_context()
            if extra:
                context = dict(context.items() + extra.items())

        return context

    def process_answer_template(self, answer, context):
        """Retorna uma string processada por um template"""

        t = Template(answer)
        c = Context(context)
        var_var_t = Template(t.render(c))
        rtn = var_var_t.render(Context(context))
        return rtn

    def save_submission(self, sms, status, instance_fields=None, raw=False, context=None, sub_type=Submission.TYPE_SMS):
        """Cria a submissão no banco de dados"""

        context = context or {}

        if instance_fields and not raw:
            data = [field.get_value() for field in instance_fields]
        else:
            data = sms.text
        submission = Submission.objects.create(status=status, data=data, form=self, identity=sms.connection.identity,
                                               context=context, sub_type=sub_type)
        if not self.requires_confirmation:
            submission.remote_save_submission()

        return submission

    def save(self, *args, **kwargs):
        """Realiza verificações de campos obrigatórios, além de prover valores padrões onde adequado."""

        if self.main:
            Form.objects.filter(main=True).update(main=False)

        if self.keyword:
            self.keyword = self.keyword.strip().lower()
            if Form.objects.filter(keyword=self.keyword).exclude(pk=self.pk).count() > 0:
                raise ValidationError("Palavra-chave já está sendo usada em outro formulário", params=["keyword"])
        else:
            raise ValidationError("Palavra-chave obrigatória.", params=["keyword"])

        if not self.separator:
            raise ValidationError("Separador obrigatório.", params=["separator"])

        if not self.positive_confirmation_list or not self.negative_confirmation_list:
            self.positive_confirmation_list = Config.get("positive_confirmation_list")
            self.negative_confirmation_list = Config.get("negative_confirmation_list")

        if isinstance(self.positive_confirmation_list, basestring):
            self.positive_confirmation_list = self.parse_list(self.positive_confirmation_list)

        if isinstance(self.negative_confirmation_list, basestring):
            self.negative_confirmation_list = self.parse_list(self.negative_confirmation_list)

        if self.requires_confirmation:
            if not self.ans_waiting_confirmation:
                raise ValidationError("Obrigatório a mensagem a ser enviada em caso de aguardo de confirmação é "
                                      "necessária para formulários que requeiram confirmação.",
                                      params=["ans_waiting_confirmation"])

            if len(set(self.negative_confirmation_list) & set(self.positive_confirmation_list)) > 0:
                raise ValidationError("Não é possível utilizar um valor para confirmação e cancelamento ao mesmo tempo",
                                      params=["positive_confirmation_list", "negative_confirmation_list"])

            if len(self.ans_positive_confirmation) < 1:
                raise ValidationError("Mensagem obrigatória.", params=["ans_positive_confirmation"])

            if len(self.ans_negative_confirmation) < 1:
                raise ValidationError("Mensagem obrigatória.", params=["ans_negative_confirmation"])

            if not self.ans_unknown_confirmation:
                self.ans_unknown_confirmation = unicode(Config.get("ans_unknown_confirmation"), "utf-8") % (
                    self.positive_confirmation_list[0], self.negative_confirmation_list[0])

        super(Form, self).save(*args, **kwargs)

    def process_field_conditions(self, instance_fields):
        """
        Processa as condições de todos os campos, retornando uma ação a ser tomada com a submissão e uma resposta caso
        alguma das condições seja de fato consumadas.
        """

        # A condição de campo de usuário deve ser a primeira a ser chamada para que o contexto seja populado nas
        # condições restantes, alem de melhorar a performance caso de fato o usuário nao possa enviar essa submissão
        for field in instance_fields:
            if field.field_type == Field.TYPE_USER_ID:
                action, answer = field.process_conditions()

                if action or answer:
                    return action, answer

        # Restante de condições
        for field in instance_fields:
            try:
                if field.field_type != Field.TYPE_USER_ID:
                    action, answer = field.process_conditions()
                    if action or answer:
                        return action, answer
            except InvalidFieldValue as error:
                return Submission.INVALID, error
        return None, None

    def process_confirmation_conditions(self, message):
        """Processa as condições em caso de mensagem de confirmação de envio"""
        return Condition.process_conditions(self.confirmation_conditions.all(), message)

    def instatiate_fields(self, fields):
        """Cria uma instância de cada campo usando os textos separados por split_fields"""
        form_fields = self.fields.all()

        instances = []
        for i, field in enumerate(form_fields):
            value = fields[i].replace("\n", " ").strip()
            field.set_value(value)
            instances.append(field)

        return instances

    def parse_list(self, string_list):
        """Realiza a separação de campos de texto separados por virgula para ser usado em listas"""
        splat = string_list.split(",")
        lst = []
        for item in splat:
            if not item.isspace() and len(item) > 0:
                lst.append(item.lower().strip())
        return lst

    # Regex é lento e isso nos da mais controle.
    def split_fields(self, message):
        """
        Separa todos os campos de uma mensagem usando o caracter separador de formulário, levando em conta escaping
        do caracter - realizado adicionando duas vezes o caracter selecionado como separador
        """

        segments = []
        next_segment = ""
        message_length = len(message)
        skip_counter = 0
        for i, char in enumerate(message):
            if skip_counter > 0:
                skip_counter -= 1
                continue

            if char == self.separator:
                if message_length > (i + 1) and len(segments) > 0 and message[i + 1] == self.separator:
                    skip_counter += 1
                    next_segment += self.separator
                else:
                    segments.append(next_segment)
                    next_segment = ""
            else:
                next_segment += char

        if len(next_segment) > 0:
            segments.append(next_segment)
        return segments

    @staticmethod
    def extract_keyword(text):
        """
        Extrai a keyword do formulário inteligentemente, procurando apenas por caracteres separadores
        usados em formulários cadastrados
        """

        form_list = itertools.groupby(Form.objects.exclude(keyword__isnull=True))  # TODO: cache
        keyword, separator_position = None, float("inf")
        last_found_pos, separator = 0, None
        for form, g in form_list:
            pos = text.find(form.separator)
            if pos != -1 and pos < separator_position:
                last_found_pos = pos
                separator = form.separator
                keyword = text[0:pos]

        if keyword:
            return keyword, separator, text[last_found_pos + 1:]
        else:
            return None, None, None

    @staticmethod
    def get_by_keyword_and_separator(keyword, separator):
        """Método auxiliar que retorna um formulário usando um conjunto de palavra-chave + separador"""
        if not keyword or not separator:
            return None

        return get_object_or_None(Form, keyword=keyword.strip().lower(), separator=separator)

    @staticmethod
    def get_main_form():
        """Retorna o formulário marcado como principal, ou nenhum"""
        return get_object_or_None(Form, main=True)

    @staticmethod
    def main_form_exists():
        """Retorna verdadeiro caso exista um formulário marcado principal"""
        return Form.get_main_form() is not None

    class Meta:
        app_label = "forms"