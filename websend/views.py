#!/usr/bin/env python
# encoding: utf-8
# vim: ai ts=4 sts=4 et sw=4
from rapidsms.router import lookup_connections
import re
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from pastoral.models import Config
from registro.models import Message
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig, tables
from rapidsms import settings
from django.conf import settings as dj_settings
from purebros.outgoing import PurebrosBackend
from raven.contrib.django.raven_compat.models import client as raven
from django.utils import timezone


class SentMessageTable(tables.Table):
    connection = tables.columns.Column(verbose_name="Telefone")

    def render_connection(self, value=None):
        return value.identity

    class Meta:
        model = Message
        attrs = {'class': 'table table-striped'}
        exclude = ('id', 'contact', 'direction')
        order_by = ('-date', )


@login_required
def view_form(request):
    qset = Message.objects.filter(connection__backend__name='envio_direto')
    qset = qset.select_related('contact', 'connection__backend')
    template = "django_tables2/bootstrap-tables.html"

    messages_table = SentMessageTable(qset, template=template)
    paginate = {"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}
    RequestConfig(request, paginate=paginate).configure(messages_table)

    context = {
        "router_available": True,
        "len": len(qset),
        "breadcrumbs": (('Envio direto', ''),),
        "message_table": messages_table
    }

    return render_to_response("websend/index.html", context,
                              context_instance=RequestContext(request))


def send_message(req):
    if not "text" in req.POST or not "identities" in req.POST:
        messages.error(req, "Parâmetros obrigatórios faltando.")
        return redirect(reverse(view_form))

    message = req.POST["text"]

    if len(message) > Config.get("max_sms_length"):
        messages.error(req, "O tamanho da mensagem excede o limite permitido.")
        return redirect(reverse(view_form))

    if len(message) < 1 or len(req.POST["identities"]) < 10:
        messages.error(req,
                       "Você precisa informar ao menos 1 telefone no formato correto. Veja um exemplo após a caixa de texto de mensagem.")
        return redirect(reverse(view_form))

    identities = req.POST["identities"].split(",")

    try:
        backend = PurebrosBackend('envio_direto', 'envio_direto', **dj_settings.INSTALLED_BACKENDS['purebros'])

        for identity in identities:
            identity = '55' + re.sub(r'[^0-9]', '', identity.strip())
            resp = backend.send_message(identity, req.POST["carrier"], message)
            if resp == "0":
                Message.objects.create(
                    date=timezone.now(),
                    direction="O",
                    text=message,
                    contact=None,
                    connection=lookup_connections(backend='envio_direto', identities=[identity])[0],
                )
            else:
                messages.error(req,
                               u"Houve um erro ao enviar a mensagem ao numero %s. Código do erro: %s" % (
                                   identity, resp))
    except Exception as e:
        raven.captureException()
        messages.error(req,
                       "Não foi possível se conectar ao integrador. Por favor tente novamente mais tarde ou se persistir o problema contate o administrador do sistema.")

    return redirect(reverse(view_form))