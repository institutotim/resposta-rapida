from tastypie.resources import ModelResource
from registro.models import Message


class MessageLogResource(ModelResource):
    class Meta:
        queryset = Message.objects.all()