#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import django_tables2 as tables
from . models import Message


class MessageTable(tables.Table):

    class Meta:
        model = Message
        attrs = {'class': 'table table-striped'}
        exclude = ('id', 'contact')
        order_by = ('-date', )
