#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.forms_list, name="web"),
    url(r'^preencher/(?P<form_id>\d+)$', views.view_form, name="web_answer_form"),
    url(r'^enviar/(?P<form_id>\d+)$', views.submit_form, name="web_submit_form"),
    url(r'^processar/$', views.process_submission, name="web_process_submission"),
    url(r'^confirmar/(?P<submission_id>\d+)/(?P<confirmation>\w+)/$', views.confirm_submission, name="web_confirm_submission"),
)
