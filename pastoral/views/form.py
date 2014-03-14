# encoding: utf-8
from django.core import serializers
from django.core.exceptions import ValidationError
from django.utils import simplejson
import types
from annoying.decorators import ajax_request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from forms.models import Form, TimedTask, Submission


@login_required()
def app(req):
    return render_to_response("forms/app.html", {"breadcrumbs": (
        ('Formulários', reverse("list_forms")), ('Editar Formulário', '')), "heading": "Editar Formulário",
                                                 "heading_icon": "list-alt"}, context_instance=RequestContext(req))


@login_required()
def list_forms(req):
    forms = Form.objects.all()
    return render_to_response("forms/list.html",
                              {"forms": forms, "breadcrumbs": (('Formulários', ''),), "heading": "Formulários",
                               "heading_icon": "list-alt"},
                              context_instance=RequestContext(req))


@login_required()
def delete_form(req, form_id):
    try:
        Form.objects.get(pk=form_id).delete()
        messages.success(req, "Formulário excluir com sucesso!")
    except Form.DoesNotExist:
        messages.error(req, "Formulário não existe.")

    return redirect(reverse("list_forms"))


@login_required()
def view_form(req, form_id):
    try:
        form = Form.objects.get(pk=form_id)

        form.positive_confirmation_list = ", ".join(form.positive_confirmation_list)
        form.negative_confirmation_list = ", ".join(form.negative_confirmation_list)

        req.session["last_view_form"] = form.pk

        return render_to_response("forms/view.html", {"status_lookup": simplejson.dumps(dict(Submission.STATUS_TYPES)),
                                                      "tasks": serializers.serialize('json', TimedTask.objects.filter(
                                                          form=form)),
                                                      "form": form,
                                                      "status_types": Submission.STATUS_TYPES,
                                                      "breadcrumbs": (
                                                          ('Formulários', reverse("list_forms")), (form.name, '')
                                                      ),
                                                      "heading": "Editar Formulário",
                                                      "heading_icon": "list-alt"}, context_instance=RequestContext(req))
    except Form.DoesNotExist:
        messages.error(req, "Formulário não encontrado.")
        return redirect(reverse("list_forms"))


@login_required()
def new_form(req):
    form = Form(name="Novo Formulário")

    return render_to_response("forms/view.html",
                              {"status_lookup": simplejson.dumps(dict(Submission.STATUS_TYPES)), "form": form,
                               "breadcrumbs": ( # TODO: Fix breadcrumbs and button navigation between lists and forms
                                   ('Formulários', reverse("list_forms")), ('Criar Formulário', '')),
                               "heading": "Criar Formulário",
                               "heading_icon": "list-alt"}, context_instance=RequestContext(req))


@ajax_request
@csrf_exempt
@login_required()
def save_form(req):
    data = req.POST.dict()
    data["main"], data["requires_confirmation"] = str_to_bool((data["main"], data["requires_confirmation"]))

    try:
        form = Form(**data)
        form.save()
    except ValidationError as error:
        return {"error": error.messages, "params": error.params}

    return {"success": True, "view_form_url": reverse("view_form", kwargs={"form_id": form.pk})}


@ajax_request
@csrf_exempt
@login_required()
def field_update(req):
    try:
        field_name = req.POST.get("name")
        pk = req.POST.get("pk")
        frm = Form.objects.get(pk=pk)
        val = req.POST.get("value")
        bool_val = None

        if field_name in ["main", "requires_confirmation", "enable_sms", "enable_web", "enable_wap", "enable_java"]:
            if val == "Sim":
                val = True
                bool_val = "Sim"
            else:
                val = False
                bool_val = "Não"

        if hasattr(frm, field_name):
            setattr(frm, field_name, val)

        frm.save()

        current_value = bool_val or getattr(frm, field_name)

        if isinstance(current_value, types.ListType):
            current_value = ", ".join(current_value)

        return {"success": True, "current_value": current_value}
    except Form.DoesNotExist:
        return {"error": "Formulário não existente."}
    except ValidationError as e:
        return {"error": e.messages}
    except AttributeError:
        return {"error": "Formulários não possuem este campo para ser atualizado. Bug?"}


def str_to_bool(values):
    return (bool(int(value)) for value in values if value.isdigit())
