# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
import gtk
import pickle
import locale
import urllib
import gettext
import httplib2
import settings
import xmlrpclib

from datetime import datetime
from pastoral.rpc import Tools

class AuthFailed(Exception):

    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return self.msg

class Environ(object):
    
    user        = None
    version     = None
    community   = None
    date        = datetime.today()
    last_sync   = None
    server_time = None
    server      = None
    threads     = []

    def i18n(self):

        import gtk.glade

        locale.setlocale(locale.LC_ALL, '')

        DIR = os.path.join(settings.PATH_ROOT, 'locale')
        APP = "pastoral"
        gettext.textdomain(APP)
        gettext.bindtextdomain(APP, DIR)

        gtk.glade.bindtextdomain(APP, DIR) 
        gtk.glade.textdomain(APP)

        return gettext.translation(APP, DIR, languages=['en_US']);

    @property
    def datetime(self):
        t = datetime.now().time()
        d = self.date
        return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)

    def set_date(self, date):
        self.date = date

    def login(self, user, password):
        
        try:
            self.rpc            = Rpc()
            self.rpc.user       = user
            self.rpc.password   = password
            self.server         = self.rpc.connect()
            return self.server.user.get_user()

        except AuthFailed:
            return None

    def save(self):
        f = open(os.path.join(settings.PATH_PASTORAL, 'environ.pck'), 'w')
        environ = {'version':      settings.VERSION,
                   'last_sync':    self.last_sync}
					
        if not self.user is None:
            environ['user'] = self.user.id
		
        pickle.dump(environ, f)
        f.close()
        

class Rpc(object):

    server   = settings.RPC
    user     = None
    password = None

    def get_url(self):
        return '%s://%s/' % (self.server['PROTOCOL'], self.server['URL'])

    def url_rpc(self):
        return '%srpc/' % self.get_url()

    def connect(self):
        if self.user and self.password:
            self.transport = PastoralTransport()
            if not self.transport.login(self.get_url(), self.user, self.password):
                raise AuthFailed('Erro de autenticação') 

            if not self.transport.set_system(self.get_url(), 1):
                raise AuthFailed('Erro ao selecionar o sistema') 

            return xmlrpclib.ServerProxy(self.url_rpc(), transport=self.transport) 
        else:
            return None


class PastoralTransport(xmlrpclib.Transport):

    cookie  = None
    headers =  {"User-agent" : "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"}

    def login(self, host, username, password):

        url  = host + 'user/login/'
        data = {'cookies_enabled': '',
                'login':           username,
                'password':        password,
                'submit':          'Entrar'}

        data              = urllib.urlencode(data)
        http              = httplib2.Http(timeout = 5)
        response, content = http.request(url, 'POST', body=data, headers=self.headers)

        if response.status == 200:
            return False

        elif response.status == 302:

            if not self.headers.has_key('Cookie'):
                self.headers['Cookie'] = response['set-cookie'].split(';')[0]

            return True

    def set_system(self, host, system):

        url               = host + 'user/login/set-system/system_id/' + str(system)
        http              = self.make_connection()
        response, content = http.request(url, 'GET', headers=self.headers)

        if response.status == 200:
            return True

        elif response.status == 302:
            return True

    def make_connection(self):

        return httplib2.Http(timeout = 45)

    def request(self, host, handler, request_body, verbose=1):

        http  = self.make_connection()
        url   = 'https://%s%s' % (host, handler)
        response, content = http.request(url, 'POST', body=request_body, headers=self.headers)

        pp, uu = self.getparser()
        pp.feed(content)
        pp.close()

        return uu.close()
