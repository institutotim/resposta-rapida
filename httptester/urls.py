#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from . import views


urlpatterns = patterns('',
    url(r"^$", views.view_form, name='httptester'),
    url(r"^send/$", views.send_message, name='httptester-send-message'),
    url(r"^get-messages/$", views.get_messages, name='httptester-get-messages-after')
)
