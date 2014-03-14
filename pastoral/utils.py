from functools import wraps
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson
from registro.models import Message


def dj_encode(obj):
    if isinstance(obj, QuerySet):
        if obj.model.__class__ == Message.__class__:
            result = []
            for item in obj:
                result.append({
                    "pk": item.pk,
                    "direction": item.direction,
                    "identity": item.connection.identity,
                    "text": item.text
                })
            return result
    return None


def ajax_request(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        return HttpResponse(
            content=simplejson.dumps(response, default=dj_encode), mimetype='application/json')

    return wrapper