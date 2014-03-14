# encoding: utf-8

from django.core.exceptions import ValidationError
from django.db import models
from condition import Condition
from forms.rpcbase import RPCBase
from pastoral.models.configuration import Config
from submission import Submission
import logging
from raven.contrib.django.raven_compat.models import client as raven

logger = logging.getLogger("pastoral")

class InvalidFieldValue(Exception):
    """Exception chamadas em campo com valor inválido"""
    pass


class Field(models.Model):
    """
    Representa um campo em um formulário, possuí métodos para tratar de valores, condições
    e retirar variáveis de contexto
    """

    # Tipo do campo
    TYPE_INT = 1
    TYPE_STRING = 2
    TYPE_USER_ID = 3
    TYPES = {
        TYPE_INT: {
            "required_conds": [Condition.LOGIC_NOT_ALL_NUM],
            "cast": int
        },

        TYPE_STRING: {
            "required_conds": [],
            "cast": str
        },

        TYPE_USER_ID: {
            "cast": str,
            "required_conds": []
        }
    }

    conditions = models.ManyToManyField(Condition)
    """
    Condições aplicadas ao campo
    Dependendo do tipo do campo, algumas condições são obrigatórias
    """

    form = models.ForeignKey("Form", related_name="fields")
    """O formulário que este campo pertence"""

    desc = models.CharField(max_length=30, null=True)
    """Label usado em clientes graficos (web, java, wap) descritivo do campo"""

    name = models.SlugField(max_length=30, validators=['validate_unique'])
    """Nome do campo. Este nome é usado em contexto de template de mensagens."""

    field_type = models.PositiveSmallIntegerField()
    """Tipo do campo"""

    answer = models.CharField(max_length=Config.get("max_sms_length"), blank=True)
    """Resposta atrelada a alguns tipos de campo que realizem algum tipo de checagem de erro"""

    def save(self, *args, **kwargs):
        """Valida nomes únicos e constraints de campos especiais"""

        if Field.objects.filter(name=self.name).exclude(pk=self.pk).count() > 0:
            raise ValidationError("O nome do campo já está sendo usado neste formulário")

        if not self.id and self.field_type == Field.TYPE_USER_ID and not self.answer:
            raise ValidationError("É necessário preencher a mensagem de usuário incorreto")

        super(Field, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.value = None
        self.extra_context = {}
        super(Field, self).__init__(*args, **kwargs)

    def get_value(self):
        """Retorna o valor de campo, em um contexto de submissão, com tipo de retorno definido pelo tipo de campo"""

        field_type = Field.TYPES[self.field_type]

        try:
            return field_type["cast"](self.value)
        except ValueError:
            return None

    def get_extra_context(self):
        """Retorna variáveis de contexto geradas por campos especiais"""
        return self.extra_context

    def set_value(self, value):
        """Coloca o valor a ser usado nas funções de processamento do campo"""
        self.value = value

    def process_conditions(self):
        """Processa as condições do campo"""

        field_type = Field.TYPES[self.field_type]

        for condition in self.conditions.all():
            action, answer, new_value, extra_vars = condition.process(self.value)
            if action or answer or new_value:
                if new_value:
                    self.value = new_value

                if extra_vars:
                    self.extra_context = dict(self.extra_context.items() + extra_vars.items())

                if condition.logic in field_type["required_conds"]:
                    raise InvalidFieldValue(answer)

                return action, answer

        if self.field_type == Field.TYPE_USER_ID:
            try:
                rpc = RPCBase()
                resp = rpc.validate_user(self.value)

                if not resp["success"]:
                    action = Submission.RPC_RESPONSE[resp["action"]]
                    answer = resp["answer"] if "answer" in resp else self.answer
                    return action, answer
                else:
                    del resp["success"]
                    self.extra_context = dict(resp.items() + self.extra_context.items())
            except Exception:
                raven.captureException()
                return None, None

        return None, None

    class Meta:
        app_label = "forms"
