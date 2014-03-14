import urllib2
from unidecode import unidecode
import uuid
from django.utils.http import urlencode
import logging
from raven.contrib.django.raven_compat.models import client as raven
from rapidsms.backends.base import BackendBase
from retry import Retry

delivery_retry = Retry()
logger = logging.getLogger("pastoral")


class PurebrosBackend(BackendBase):
    """Backend para uso com o integrador Purebros."""
    __module__ = "purebros"

    def configure(self, sendsms_url='http://127.0.0.1:8081/testsend', username='PROVIDER', password='PASSWORD',
                  short_number='999999', mt_servtype='?', carrier_id=130, **kwargs):
        self.sendsms_url = sendsms_url
        self.username = username
        self.password = password
        self.short_number = short_number
        self.default_carrier_id = carrier_id
        self.mt_servtype = mt_servtype

    def prepare_message(self, identity, carrier, text):
        return {
            'mt_format': 0,
            'mt_udh': 0,
            'mt_id': str(uuid.uuid4()).replace('-', '')[:30],
            'mt_source': self.short_number,
            'mt_target': identity,
            'mt_carrier': carrier,
            'mt_bodycount': 1,
            'mt_body1': unidecode(text),
            'mt_user': self.username,
            'mt_pass': self.password,
            'mt_servtype': self.mt_servtype,
            'mt_reqsource': 'SMS'
        }

    def send_message(self, identity, carrier_id, text):
        params = self.prepare_message(identity, carrier_id, text)

        url = '?'.join([unicode(self.sendsms_url), urlencode(params)])

        response = urllib2.urlopen(url).read()
        return response

    def send(self, id_, text, identities, context={}):
        for identity in identities:
            if '.' in identity:
                carrier_id, identity = identity.split('.')
            else:
                logger.error("Trying to send a message without the carrier prefix") # TODO: Fix this mess
                return False

            try:
                response = self.send_message(identity, carrier_id, text)
                logger.info("SMS Sent [%s]: %s" % (identity, text), extra={'response': response})
                delivery_retry.handle_response(response, text, identity, context)
                return True
            except urllib2.HTTPError, urllib2.URLError:
                logger.error("Falha ao enviar mensagem devido a problema de rede.")
                raven.captureException()
                return False
