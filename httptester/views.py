#!/usr/bin/env python
# encoding: utf-8
# vim: ai ts=4 sts=4 et sw=4


from random import randint
from django.template import RequestContext
from django.shortcuts import render_to_response
from . import forms
from pastoral.utils import ajax_request
from django.views.decorators.csrf import csrf_exempt
from registro.models import Message
from rapidsms.router import lookup_connections, receive


def view_form(request):
    if "identity" in request.GET:
        identity = request.GET["identity"]
    else:
        identity = randint(99000000, 99999999)

    form = forms.MessageForm({"identity": identity})

    messages = Message.objects.filter(connection__identity=identity).order_by("-id")

    context = {
        "router_available": True,
        "message_log": messages,
        "message_form": form,
        "breadcrumbs": (('Teste de mensagens', ''),)
    }

    return render_to_response("httptester/index.html", context,
                              context_instance=RequestContext(request))


@ajax_request
def get_messages(request):
    if not "identity" in request.GET:
        return {"error": u"Campos obrigatórios não encontrados"}

    offset = request.GET["offset"] if "offset" in request.GET else None
    identity = request.GET["identity"]

    messages = Message.objects.filter(connection__identity=identity).only('pk', 'direction', 'text').order_by("id")

    if offset:
        offset = int(offset)
        messages = messages.filter(pk__gt=offset)

    return {"success": True, "messages": messages}


@csrf_exempt
@ajax_request
def send_message(request):
    form = forms.MessageForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        identity = cd["identity"]
        connection = lookup_connections("message_tester", [identity])[0]
        receive(cd["text"], connection)
        return {"success": True}
    else:
        return {"error": u"Parâmetros obrigatórios não encontrados"}
