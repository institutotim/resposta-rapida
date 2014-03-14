# encoding: utf-8
from django.core.exceptions import ValidationError
from annoying.decorators import ajax_request
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from annoying.functions import get_object_or_None
from forms.models import Form, Field


@ajax_request
@csrf_exempt
@login_required()
def add(req):
    form_id, name_internal, name_public, field_type = req.POST["form_id"], req.POST["name_internal"], req.POST[
        "name_public"], req.POST["type"]

    try:
        form = Form.objects.get(pk=form_id)
        fld = Field(name=name_internal, desc=name_public, field_type=field_type, form=form)
        fld.save()

        return {"success": True, "separator": form.separator,
                "fields": list(form.fields.all().values('name', 'field_type', 'id'))}
    except Form.DoesNotExist:
        return {"error": "Formulário não encontrado"}
    except ValidationError as error:
        return {"error": error.messages}


@ajax_request
@csrf_exempt
@login_required()
def remove(req):
    field_id = req.POST["id"]

    fld = get_object_or_None(Field, pk=field_id)

    if not fld:
        return {"error": "Campo não encontrado"}

    fld.delete()

    return {"success": True, "separator": fld.form.separator,
            "fields": list(fld.form.fields.all().values('name', 'field_type', 'id'))}


@ajax_request
@csrf_exempt
@login_required()
def update(req):
    field_id, name_internal, name_public, field_type = req.POST["id"], req.POST["name_internal"], req.POST["name_public"], req.POST["type"]

    fld = get_object_or_None(Field, pk=field_id)

    if not fld:
        return {"error": "Campo não encontrado"}

    try:
        fld.name = name_internal
        fld.desc = name_public
        fld.field_type = int(field_type)
        fld.save()
    except ValidationError as error:
        return {"error": error.messages}
    except TypeError:
        return {"error": "Tipo de campo inválido"}

    return {"success": True, "separator": fld.form.separator,
            "fields": list(fld.form.fields.all().values('name', 'field_type', 'id'))}
