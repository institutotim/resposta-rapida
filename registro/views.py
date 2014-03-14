#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .tables import MessageTable
from .models import Message
from rapidsms import settings

from django_tables2 import RequestConfig


@csrf_exempt
@login_required
def message_log(request):
    search_identity = None
    if "search_identity" in request.GET:
        search_identity = request.GET.get("search_identity").strip()
        qset = Message.objects.filter(
            Q(connection__identity__startswith=search_identity) | Q(connection__identity__endswith=search_identity)
        )
    else:
        qset = Message.objects.all()

    qset = qset.select_related('contact', 'connection__backend')
    template = "django_tables2/bootstrap-tables.html"

    messages_table = MessageTable(qset, template=template)

    paginate = {"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}
    RequestConfig(request, paginate=paginate).configure(messages_table)

    return render(request, "registro/index.html", {
        "messages_table": messages_table,
        "search_identity": search_identity
    })
