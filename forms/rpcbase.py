from urlparse import urlparse
import xmlrpclib
import urllib
import httplib2
from pastoral.models.configuration import Config
import logging
from raven.contrib.django.raven_compat.models import client as raven

logger = logging.getLogger("pastoral")


class PastoralTransport(xmlrpclib.Transport):
    cookie = None
    headers = {"User-agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
               "Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    def login(self, host, username, password):

        url = host + 'user/login/'
        data = {'cookies_enabled': '',
                'login': username,
                'password': password,
                'submit': 'Entrar'}

        data = urllib.urlencode(data)
        http = httplib2.Http(timeout=5)
        response, content = http.request(url, 'POST', body=data, headers=self.headers)

        if response.status == 200:
            return False

        elif response.status == 302:

            if not self.headers.has_key('Cookie'):
                self.headers['Cookie'] = response['set-cookie'].split(';')[0]
                logger.info("RPC login successful: %s" % self.headers['Cookie'])

            return True

    def set_system(self, host, system):

        url = host + 'user/login/set-system/system_id/' + str(system)
        http = self.make_connection()
        response, content = http.request(url, 'GET', headers=self.headers)

        if response.status == 200:
            return True

        elif response.status == 302:
            return True

    def make_connection(self):

        return httplib2.Http(timeout=45, disable_ssl_certificate_validation=True)

    def request(self, host, handler, request_body, verbose=1):

        http = self.make_connection()
        url = 'http://%s%s' % (host, handler)
        response, content = http.request(url, 'POST', body=request_body, headers=self.headers)

        pp, uu = self.getparser()
        pp.feed(content)
        pp.close()

        return uu.close()


class RPCBase(object):
    def __init__(self):
        self.proxy = RPCBase.get_rpc_proxy()

    @staticmethod
    def get_rpc_proxy():
        rpc_server_url = Config.get("rpc_server")

        if Config.get("rpc_authenticate"):
            host_url = urlparse(rpc_server_url)
            host = host_url.scheme + "://" + host_url.hostname + "/"

            transport = PastoralTransport()

            transport.login(host, Config.get("rpc_username"), Config.get("rpc_password"))
            transport.set_system(host, 1)

            proxy = xmlrpclib.ServerProxy(rpc_server_url, transport=transport).sms
        else:
            proxy = xmlrpclib.ServerProxy(rpc_server_url)

        return proxy

    def _secure_call(self, callableFn, *args, **kwargs):
        try:
            return callableFn(*args, **kwargs)
        except:
            raven.captureException()

    def validate_user(self, *args):
        return self._secure_call(self.proxy.validate_user, *args)

    def process_submission(self, *args):
        return self._secure_call(self.proxy.process_submission, *args)

    def save_submission(self, *args):
        return self._secure_call(self.proxy.save_submission, *args)