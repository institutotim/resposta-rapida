# encoding: utf-8
from rapidsms.apps.base import AppBase
from pastoral.models.configuration import Config
from models import Form, Submission


class FormsApp(AppBase):
    """Classe usada como entrypoint para processamento de mensagens do RapidSMS"""

    def handle(self, sms):
        """Método chamado pelo RapidSMS para processar uma mensagem"""
        sub_type = Submission.TYPE_SMS  # estamos organizando as outras branchs do projeto
        answer = Config.get("message_unknown_format")

        if Submission.has_confirmation_pending(sms.connection.identity):
            submission = Submission.get_unconfirmed(sms.connection.identity)
            answer = submission.confirm(sms.text)
            return self.send_answer(sms, answer)

        if Form.main_form_exists():
            form = Form.get_main_form()

        else:
            keyword, separator, remaining_message = Form.extract_keyword(sms.text)
            sms.text = remaining_message
            form = Form.get_by_keyword_and_separator(keyword, separator)

        if form:
            answer = form.process_submission(sms, sub_type) or answer

        return self.send_answer(sms, answer)

    def send_answer(self, sms, answer):
        """Envia a resposta ao usuário"""
        sms.respond(answer, fields=sms.fields)
        return True