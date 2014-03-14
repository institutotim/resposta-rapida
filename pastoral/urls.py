from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from purebros.views import PurebrosBackendView
from tastypie.api import Api
from forms.api import MessageLogResource

v1_api = Api(api_name="v1")
v1_api.register(MessageLogResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'pastoral.views.dashboard', {}, name="rapidsms-dashboard"),
    # RapidSMS core URLs
    (r'^accounts/', include('rapidsms.urls.login_logout')),
    # RapidSMS contrib app URLs
    (r'^httptester/', include('httptester.urls')),
    (r'^websend/', include('websend.urls')),
    (r'^locations/', include('rapidsms.contrib.locations.urls')),
    (r'^registro/', include('registro.urls')),
    (r'^web/', include('web.urls')),
    (r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    (r'^registration/', include('rapidsms.contrib.registration.urls')),
    (r'^sms/ep/receive[^?]*$', PurebrosBackendView.as_view()),
    (r'^sms/ep/notify$', 'purebros.views.process_notification'),
    url(r'^configuration/view', 'pastoral.views.configuration.list_configuration', name="list_configuration"),
    url(r'^configuration/save', 'pastoral.views.configuration.save_configuration', name="save_configuration"),
    url(r'^test/create_form$', 'pastoral.views.test.create_form', name='create_form'),
    url(r'^test/test_rpc', 'pastoral.views.test.test_rpc', name='test_rpc'),
    url(r'^formularios/$', 'pastoral.views.form.list_forms', name='list_forms'),
    url(r'^formularios/excluir/(?P<form_id>\d+)$', 'pastoral.views.form.delete_form', name='del_form'),
    url(r'^formularios/visualizar/(?P<form_id>\d+)$', 'pastoral.views.form.view_form', name='view_form'),
    url(r'^formularios/editar$', 'pastoral.views.form.field_update', name="form_field_update"),
    url(r'^formularios/criar$', 'pastoral.views.form.new_form', name="new_form"),
    url(r'^formularios/salvar$', 'pastoral.views.form.save_form', name="save_form"),
    url(r'^formularios/campos/adicionar$', 'pastoral.views.field.add', name="add_field"),
    url(r'^formularios/campos/excluir$', 'pastoral.views.field.remove', name="remove_field"),
    url(r'^formularios/campos/alterar$', 'pastoral.views.field.update', name="update_field"),
    url(r'^formularios/condicoes/listar/(?P<cond_type>(confirmation|form|field))/(?P<id>\d+)$', 'pastoral.views.condition.lst', name="list_conditions"),
    url(r'^formularios/condicoes/novo/(?P<cond_type>(confirmation|form|field))/(?P<id>\d+)$', 'pastoral.views.condition.show_new_form', name="new_condition"),
    url(r'^formularios/condicoes/editar/(?P<id>\d+)$', 'pastoral.views.condition.edit', name="edit_condition"),
    url(r'^formularios/condicoes/excluir/(?P<id>\d+)/(?P<cond_type>(confirmation|form|field))/(?P<cond_id>\d+)$', 'pastoral.views.condition.delete', name="delete_condition"),
    url(r'^formularios/condicoes/salvar$', 'pastoral.views.condition.save', name="save_condition"),
    url(r'^formularios/tarefas/salvar$', 'pastoral.views.task.save', name="save_task"),
    url(r'^formularios/tarefas/excluir/(?P<id>\d+)$', 'pastoral.views.task.delete', name="delete_task"),

    (r'^api/', include(v1_api.urls)),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)