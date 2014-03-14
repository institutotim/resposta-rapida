# encoding: utf-8
from django.http import HttpResponse
from forms.models import *
from forms.rpcbase import *

SORRY_ONLY_NUMBERS = "Desculpe. Houve um erro. Use apenas numeros para fornecer as informacoes. Escreva novamente. " \
                     "Em caso de duvida consulte seu cartao do lider."

CONF_SORRY_NUMBERS_ONLY = "Houve um erro.Use apenas numeros para responder, 1 para SIM e 2 para NAO. " \
                          "Escreva novamente.Em caso de duvida consulte seu cartao do lider."

CONF_SORRY_JUST_THESE = "Desculpe. Houve um erro. Use 1 para SIM e 2 para NAO. " \
                          "Escreva novamente. Em caso de duvida consulte seu cartao do lider."

SORRY_UNKNOWN_COD = "Desculpe. Houve um erro. Nao entendemos o codigo identificador, confira e escreva novamente. " \
                    "Voce pode consulta-lo no seu cartao do lider."

THANKS_MESSAGE = "{{name}} recebemos sua mensagem corretamente. Obrigado por construir ambientes saudaveis junto as familias" \
                 " e comunidades."

CANCELED_MESSAGE = "{{name}} voce cancelou as informacoes enviadas. Para reiniciar escreva novamente o codigo identificador " \
                   "e seu numero do lider."

WRONG_USER_ID = "Desculpe. Houve um erro. Nao entendemos seu numero do lider, confira e escreva novamente. " \
                "Seu numero deve ter ate 13 digitos."

PROB_3 = "Paz e Bem! {{name}} voce informou que nao ha antibiotico em uma UBS da regiao. Esta correto? Escreva 1 para SIM " \
         "e 2 para NAO."

PROB_4 = "Paz e Bem! {{name}} voce informou que a UBS da regiao nao da a primeira dose do antibiotico. Esta correto? " \
         "Escreva 1 para SIM e 2 para NAO."

PROB_5 = "Paz e Bem! {{name}} voce informou que nao ha vacina para gestante em uma UBS da regiao. Esta correto? " \
         "Escreva 1 para SIM e 2 para NAO."

PROB_6 = "Paz e Bem! {{name}} voce informou que nao ha vacina para crianca em uma UBS da regiao. Esta correto? Escreva " \
         "1 para SIM e 2 para NAO."

PROB_7 = "Paz e Bem! {{name}} voce informou que uma gestante nao foi atendida em uma UBS da regiao. Esta correto? " \
         "Escreva 1 para SIM e 2 para NAO."

PROB_8 = "Paz e Bem! {{name}} voce informou que uma crianca nao foi atendida em uma UBS da regiao. Esta correto? Escreva " \
         "1 para SIM e 2 para NAO."

PROB_10 = "Paz e Bem! {{name}} voce esta participando de uma formacao da Pastoral da Crianca. Esta correto? Use 1 para SIM e 2 para NAO"

SORRY_NO_DOT = "Desculpe. Houve um erro. As informacoes devem ser separadas por PONTO. Escreva novamente. " \
               "Em caso de duvida consulte seu cartao do lider."

REMINDER_1H = "Voce informou que {{desc_problema}}, mas ainda nao recebemos sua confirmacao. " \
              "Esta correto? Use 1 para SIM e 2 para NAO."

REMINDER_4H = "Voce enviou o codigo identificador {{codigo_problema}}, mas nao recebemos SMS de confirmacao. ENVIO CANCELADO. " \
              "Para reiniciar siga a dica 5 do cartao do lider"


def create_form(req):
    frm = Form.objects.create(
        name="Relato de Problemas",
        separator=".",
        requires_confirmation=True,
        keyword="prob",
        main=True,
        positive_confirmation_list="1",
        negative_confirmation_list="2",
        ans_positive_confirmation="{{resposta}}",
        ans_negative_confirmation=CANCELED_MESSAGE,
        ans_waiting_confirmation="Nao usado",
        ans_incorrect_num_fields=WRONG_USER_ID,
        ans_unknown_confirmation=CONF_SORRY_JUST_THESE
    )

    f1 = Field.objects.create(name="codigo_problema", form=frm, field_type=Field.TYPE_STRING)
    f2 = Field.objects.create(name="nome_de_usuario", form=frm, field_type=Field.TYPE_USER_ID, answer=WRONG_USER_ID)

    # Form cond
    cond_has_dot = Condition.objects.create(answer=SORRY_NO_DOT, logic=Condition.LOGIC_DOESNT_CONTAIN, param=".",
                                            action=Submission.CANCELED)

    frm.conditions.add(cond_has_dot)

    TimedTask.objects.create(form=frm, submission_status=Submission.NOT_CONFIRMED, run_after_min=60, once=True,
                             answer=REMINDER_1H)

    TimedTask.objects.create(form=frm, submission_status=Submission.NOT_CONFIRMED, status_to_change=Submission.CANCELED,
                             run_after_min=240, once=True,
                             answer=REMINDER_4H)

    # Validation
    cond_numbers_only = Condition.objects.create(answer=SORRY_ONLY_NUMBERS, action=Submission.CANCELED,
                                                 logic=Condition.LOGIC_NOT_ALL_NUM)

    cond_unk_prob = Condition.objects.create(answer=SORRY_UNKNOWN_COD, action=Submission.CANCELED,
                                             logic=Condition.LOGIC_NOT_IN_LIST,
                                             param="3, 4, 5, 6, 7, 8, 10")

    f1.conditions.add(cond_numbers_only)
    f1.conditions.add(cond_unk_prob)

    user_id_numbers_only = Condition.objects.create(answer=WRONG_USER_ID, action=Submission.CANCELED,
                                                    logic=Condition.LOGIC_NOT_ALL_NUM)

    cond_numbers_only2 = Condition.objects.create(answer=SORRY_ONLY_NUMBERS, action=Submission.CANCELED,
                                                 logic=Condition.LOGIC_NOT_ALL_NUM)

    f2.conditions.add(cond_numbers_only2)
    f2.conditions.add(user_id_numbers_only)

    # Parsed messages
    cond_prob_3 = Condition.objects.create(answer=PROB_3, logic=Condition.LOGIC_EQUALS, param=3, extra_vars={
        "desc_problema": "nao ha antibiotico em uma UBS",
        "resposta": THANKS_MESSAGE
    })

    cond_prob_4 = Condition.objects.create(answer=PROB_4, logic=Condition.LOGIC_EQUALS, param=4, extra_vars={
        "desc_problema": "a UBS da regiao nao da a primeira dose do antibiotico",
        "resposta": THANKS_MESSAGE
    })

    cond_prob_5 = Condition.objects.create(answer=PROB_5, logic=Condition.LOGIC_EQUALS, param=5, extra_vars={
        "desc_problema": "nao ha vacina para gestante em uma UBS da regiao",
        "resposta": THANKS_MESSAGE
    })

    cond_prob_6 = Condition.objects.create(answer=PROB_6, logic=Condition.LOGIC_EQUALS, param=6, extra_vars={
        "desc_problema": "nao ha vacina para crianca em uma UBS da regiao",
        "resposta": THANKS_MESSAGE
    })

    cond_prob_7 = Condition.objects.create(answer=PROB_7, logic=Condition.LOGIC_EQUALS, param=7, extra_vars={
        "desc_problema": "uma gestante nao foi atendida em uma UBS da regiao",
        "resposta": THANKS_MESSAGE
    })

    cond_prob_8 = Condition.objects.create(answer=PROB_8, logic=Condition.LOGIC_EQUALS, param=8, extra_vars={
        "desc_problema": "uma crianca nao foi atendida em uma UBS da regiao",
        "resposta": THANKS_MESSAGE
    })

    cond_prob_10 = Condition.objects.create(answer=PROB_10, logic=Condition.LOGIC_EQUALS, param=10, extra_vars={
        "desc_problema": "esta participando de uma formacao da Pastoral",
        "resposta": "Recebemos sua mensagem. Voce aprendeu enviar. Quando tiver informacoes na sua comunidade envie usando os codigos identificadores do cartao."
    })

    f1.conditions.add(cond_prob_3)
    f1.conditions.add(cond_prob_4)
    f1.conditions.add(cond_prob_5)
    f1.conditions.add(cond_prob_6)
    f1.conditions.add(cond_prob_7)
    f1.conditions.add(cond_prob_8)
    f1.conditions.add(cond_prob_10)

    # Confirmation conditions
    cond_confirm_numbers_only = Condition.objects.create(answer=CONF_SORRY_NUMBERS_ONLY,
                                                         action=Submission.NOT_CONFIRMED,
                                                         logic=Condition.LOGIC_NOT_ALL_NUM,
                                                         param=frm.separator)

    frm.confirmation_conditions.add(cond_confirm_numbers_only)

    return HttpResponse("Criado formularios")

def test_rpc(req):
    proxy = RPCBase()
    e = proxy.validate_user("123123")
    return HttpResponse("OK: " + str(e))