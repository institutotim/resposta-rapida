# encoding: utf-8
from django.db import models
from django.utils import simplejson
from pastoral.models.configuration import Config
from picklefield import PickledObjectField
from submission import Submission
import re


class Condition(models.Model):
    """
    Condições alteram a resposta enviado ao usuário, valor final de um campo além de ações realizadas sobre submissões
    através de condições lógicas aplicadas a uma mensagem do usuário.
    """

    # Tipos de ações que podem ser realizadas em submissões
    ACTION_TYPES = ((Submission.CANCELED, "Cancelar"),
                    (Submission.CONFIRMED, "Confirmar"),
                    (Submission.NOT_CONFIRMED, "Desconfirmar"),
                    (Submission.INVALID, "Inválida"))

    # Lista de condições lógicas
    LOGIC_ALL_NUM = 1
    LOGIC_ALL_ALPHA = 2
    LOGIC_ALPHANUM = 3
    LOGIC_EQUALS = 4
    LOGIC_IN_LIST = 5
    LOGIC_NOT_EQUALS = 6
    LOGIC_NOT_IN_LIST = 7
    LOGIC_LESS_THAN = 8
    LOGIC_GREATER_THAN = 9
    LOGIC_BETWEEN = 10
    LOGIC_CONTAINS = 11
    LOGIC_DOESNT_CONTAIN = 12
    LOGIC_EMPTY = 13
    LOGIC_NOT_NUM = 14
    LOGIC_NOT_EMPTY = 15
    LOGIC_NOT_ALL_NUM = 16
    LOGIC_NOT_DECIMAL = 17
    LOGIC_HAS_VAR = 18
    LOGIC_VAR_EQUALS = 19
    LOGIC_VAR_NOT_EQUALS = 20

    LOGIC_TYPES = ((LOGIC_ALL_NUM, "Todos os caracteres são digitos"),
                   (LOGIC_NOT_ALL_NUM, "Algum dos caracteres não é um número"),
                   (LOGIC_ALL_ALPHA, "Todos os caracteres são letras"),
                   (LOGIC_ALPHANUM, "Contém letras e digitos"),
                   (LOGIC_EQUALS, "É igual a um valor definido"),
                   (LOGIC_NOT_NUM, "Não é um número"),
                   (LOGIC_NOT_DECIMAL, "Não é um decimal"),
                   (LOGIC_IN_LIST, "Consta em uma lista de valores definidos"),
                   (LOGIC_NOT_EQUALS, "É diferente de um valor definido"),
                   (LOGIC_NOT_IN_LIST, "É diferente de uma lista de valores definidos"),
                   (LOGIC_LESS_THAN, "É menor ou igual a um numeral"),
                   (LOGIC_GREATER_THAN, "É maior ou igual a um numeral"),
                   (LOGIC_BETWEEN, "Está entre dois numerais (inclusive)"),
                   (LOGIC_CONTAINS, "Contém uma palavra"),
                   (LOGIC_DOESNT_CONTAIN, "Não contém uma palavra"),
                   (LOGIC_EMPTY, "Está vazio"),
                   (LOGIC_NOT_EMPTY, "Não está vazio"))

    answer = models.CharField(max_length=Config.get("max_sms_length"))
    """Resposta que é enviada ao usuário caso esta condição seja cumprida"""

    action = models.SmallIntegerField(choices=ACTION_TYPES, null=True)
    """Ação tomada com a submissão em contexto caso a condição seja cumprida"""

    param = PickledObjectField()
    """Valor usado como parâmetro para condições lógicas comparativas"""

    logic = models.SmallIntegerField(choices=LOGIC_TYPES)
    """A condição lógica usada para processar essa condição"""

    order = models.PositiveSmallIntegerField(default=0)
    """Ordem da condição, apenas a primeira condição a ser cumprida é leavada em conta"""

    new_value = models.CharField(max_length=Config.get("max_sms_length"), blank=True)
    """Valor que deverá ser substituido pelo valor enviado pelo usuário caso seja aplicável"""

    extra_vars = PickledObjectField(null=True)
    """Variáveis extras a serem adicionadas no contexto de submissão caso a condição seja estabelecida"""

    def process(self, text):
        """Processa a condição"""

        if self.logic in (Condition.LOGIC_EQUALS, Condition.LOGIC_IN_LIST, Condition.LOGIC_NOT_IN_LIST):
            text = self.coerse_to_int(text)
            if isinstance(self.param, list):
                self.param = [self.coerse_to_int(param) for param in self.param]
            else:
                self.param = self.coerse_to_int(self.param)

        matches = False
        if self.logic == Condition.LOGIC_ALL_NUM:
            matches = text.replace(self.param, "").isdigit()

        elif self.logic == Condition.LOGIC_NOT_ALL_NUM:
            matches = not text.replace(self.param, "").isdigit()

        elif self.logic == Condition.LOGIC_NOT_DECIMAL:
            try:
                n = float(text)
                matches = False if not n.is_integer() else True
            except ValueError:
                matches = True

        elif self.logic == Condition.LOGIC_NOT_NUM:
            matches = not text.isdigit()

        elif self.logic == Condition.LOGIC_ALL_ALPHA:
            matches = text.replace(self.param, "").isalpha()

        elif self.logic == Condition.LOGIC_ALPHANUM:
            matches = re.match(r'[a-zA-Z]+', text) and re.match(r'[0-9]+', text)

        elif self.logic == Condition.LOGIC_EQUALS:
            matches = text == self.param

        elif self.logic == Condition.LOGIC_IN_LIST:
            matches = text in self.param

        elif self.logic == Condition.LOGIC_NOT_EQUALS:
            matches = text != self.param

        elif self.logic == Condition.LOGIC_NOT_IN_LIST:
            matches = not text in self.param

        elif self.logic == Condition.LOGIC_LESS_THAN:
            matches = text <= self.param

        elif self.logic == Condition.LOGIC_GREATER_THAN:
            matches = text >= self.param

        elif self.logic == Condition.LOGIC_BETWEEN:
            matches = self.param[0] <= text <= self.param[1]

        elif self.logic == Condition.LOGIC_CONTAINS:
            matches = self.param in text

        elif self.logic == Condition.LOGIC_DOESNT_CONTAIN:
            matches = not self.param in text

        elif self.logic == Condition.LOGIC_EMPTY:
            matches = len(text) == 0

        elif self.logic == Condition.LOGIC_NOT_EMPTY:
            matches = len(text) > 0

        if matches:
            return self.action, self.answer, self.new_value, self.extra_vars
        else:
            return None, None, None, None

    def save(self, *args, **kwargs):
        """Valida campos e prepara valores especiais"""

        self.logic = int(self.logic)

        if self.logic in (Condition.LOGIC_IN_LIST, Condition.LOGIC_NOT_IN_LIST):
            if isinstance(self.param, basestring):
                self.param = self.param.split(",")
                self.param = [item.strip() for item in self.param]
                self.param = [int(item) for item in self.param if item.isdigit()]
        elif self.logic in (Condition.LOGIC_LESS_THAN, Condition.LOGIC_GREATER_THAN):
            self.param = int(self.param)
        elif self.logic == Condition.LOGIC_BETWEEN:
            self.param = [int(param) for param in self.param]

        if isinstance(self.param, list) and len(self.param) == 1:
            self.param = self.param[0]

        super(Condition, self).save(*args, **kwargs)

    def readable_logic(self):
        for logic in Condition.LOGIC_TYPES:
            if logic[0] == self.logic:
                return logic[1]

    def readable_param(self):
        if hasattr(self.param, '__iter__'):
            return ", ".join([str(param) for param in self.param])

        return self.param

    def readable_action(self):
        for status in Submission.STATUS_TYPES:
            if self.action == status[0]:
                return status[1]

        return "Manter atual"

    def get_related(self):
        if self.form_set.count() > 0:
            form = self.form_set.all()[0]
            return 'form', form
        elif self.form_confirmations.count() > 0:
            form = self.form_confirmations.all()[0]
            return 'confirmation', form
        elif self.field_set.count() > 0:
            field = self.field_set.all()[0]
            return 'field', field

    def get_params_for_js(self):
        if self.logic in (Condition.LOGIC_NOT_IN_LIST, Condition.LOGIC_IN_LIST):
            self.param = [str(param) for param in self.param]
            self.param = ", ".join(self.param)

        if not isinstance(self.param, list):
            self.param = [self.param]

        return simplejson.dumps(self.param)

    @staticmethod
    def process_conditions(conditions, value):
        """Método auxiliar que executa o processamento de condições na lista de condições passada"""
        for condition in conditions:
            action, answer, new_value, extra_vars = condition.process(value)
            if action or answer or new_value:
                return action, answer, new_value, extra_vars

        return None, None, None, None

    def coerse_to_int(self, val):
        try:
            if val.isdigit():
                return int(val)
            else:
                return val
        except (AttributeError, ValueError):
            return val

    class Meta:
        app_label = "forms"
        ordering = ["order"]