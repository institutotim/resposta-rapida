# encoding: utf-8

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from pastoral.models.configuration import Configuration, Config
from django.contrib import messages
from django.conf import settings
import collections


@login_required
def list_configuration(req):
    items = collections.OrderedDict()
    configuration = settings.DEFAULT_CONFIGURATION.copy()
    items_db = Configuration.objects.all()
    for item_db in items_db:
        for key, config_items in configuration.iteritems():
            for item_key in config_items.keys():
                if item_key == item_db.key:
                    if not key in items:
                        items[key] = {}
                    items[key][item_db.key] = item_db

    return render_to_response("configuration.html",
                              {"items": items, "breadcrumbs": (('Configurações', ''),), "heading": "Configurações",
                               "heading_icon": "cog", "config": settings.DEFAULT_CONFIGURATION},
                              context_instance=RequestContext(req))


@csrf_exempt
@login_required
def save_configuration(req):
    for key, val in req.POST.iteritems():
        Config.set(key, val)

    messages.success(req, "Configurações atualizadas com sucesso.")

    return redirect(reverse("list_configuration"))