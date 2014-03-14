from django.http import HttpResponse
from purebros.forms import PurebrosForm
from rapidsms.backends.http.views import BaseHttpBackendView
from rapidsms.router.api import receive
import logging

logger = logging.getLogger("pastoral")

class PurebrosBackendView(BaseHttpBackendView):
    """ Backend view for handling inbound SMSes from Kannel """
    backend_name = 'purebros'
    http_method_names = ['get']
    form_class = PurebrosForm

    processed_ids = []

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PurebrosBackendView, self).get_form_kwargs()
        kwargs['data'] = self.request.GET # passes request.GET to the form
        return kwargs

    #
    def form_valid(self, form):
        incoming_data = form.get_incoming_data()
        connection, text, extra_data = incoming_data['connection'], incoming_data['text'], incoming_data['fields']
        logger.info("SMS Received: %s", (incoming_data['text']))

        if not extra_data["pb_id"] in PurebrosBackendView.processed_ids:
            PurebrosBackendView.processed_ids.append(extra_data["pb_id"])
            receive(text, connection, fields=extra_data)

        return HttpResponse('0')

    def form_invalid(self, form):
        return HttpResponse('1-Dados obrigatorios nao encontrados.')


def process_notification(request):
    return HttpResponse("0")
