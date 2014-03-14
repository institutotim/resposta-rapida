# encoding: utf-8
from django.core.exceptions import ValidationError
from annoying.decorators import ajax_request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from annoying.functions import get_object_or_None
from forms.models import Form, Field, Submission, Condition
from django.utils import simplejson


@login_required()
def lst(req, cond_type, id):
    conditions, field, form = None, None, None
    form_id = id

    try:
        if cond_type == "form":
            form = get_object_or_None(Form, pk=form_id)
            conditions = form.conditions.all()

        elif cond_type == "confirmation":
            form = get_object_or_None(Form, pk=form_id)
            conditions = form.confirmation_conditions.all()

        elif cond_type == "field":
            field = get_object_or_None(Field, pk=id)
            conditions = field.conditions.all()
            form_id = field.form.pk
    except AttributeError:
        messages.error(req, "Não foi possível encontrar condições para esse elemento.")
        return redirect(reverse("view_form", kwargs={"form_id": form_id}))

    form = form or get_object_or_None(Form, pk=form_id)

    return render_to_response("conditions.html",
                              {"conditions": conditions,
                               "logic_lookup": Condition.LOGIC_TYPES,
                               "form": form,
                               "field": field,
                               "id": int(id),
                               "cond_type": cond_type,
                               "breadcrumbs": (
                                   ('Formulários', reverse("list_forms")),
                                   (form.name or "Edição de formulário", reverse("view_form", kwargs={'form_id': 1})),
                                   ('Editar condições', '')

                               ),
                               "heading": "Formulários",
                               "heading_icon": "list-alt"},
                              context_instance=RequestContext(req))


@login_required()
def edit(req, id):
    condition = get_object_or_None(Condition, pk=id)
    related_to = condition.get_related()

    condition.param = condition.get_params_for_js()
    extra_vars = []

    if hasattr(condition, 'extra_vars') and condition.extra_vars:
        for name, value in condition.extra_vars.items():
            extra_vars.append({"name": name, "value": value})

    extra_vars = simplejson.dumps(extra_vars)

    if condition:
        return render_to_response("condition_form.html",
                                  {"condition": condition,
                                   "related": related_to,
                                   "condition_model": Condition,
                                   "extra_vars": extra_vars,
                                   "submission_model": Submission,
                                   "id": id,
                                   "breadcrumbs": (
                                       ('Formulários', reverse("list_forms")),
                                       ('Editar Formulário', reverse("view_form", kwargs={'form_id': 1})),
                                       ('Editar condição', '')

                                   ),
                                   "heading": "Formulários",
                                   "heading_icon": "list-alt"},
                                  context_instance=RequestContext(req))
    else:
        messages.error(req, "Não foi possível encontrar a condição requisitada.")
        if "last_viewed_form" in req.session:
            form_id = req.session["last_viewed_form"]
            return redirect(reverse("view_form", kwargs={"form_id": form_id}))
        else:
            return redirect(reverse("list_forms"))


@login_required()
def show_new_form(req, cond_type, id):
    condition = Condition()
    related = (cond_type, {"pk": id})
    return render_to_response("condition_form.html",
                              {"condition": condition,
                               "cond_type": cond_type,
                               "related": related,
                               "condition_model": Condition,
                               "submission_model": Submission,
                               "id": id,
                               "breadcrumbs": (
                                   ('Formulários', reverse("list_forms")),
                                   ('Editar Formulário', reverse("view_form", kwargs={'form_id': 1})),
                                   ('Nova condição', '')

                               ),
                               "heading": "Formulários",
                               "heading_icon": "list-alt"},
                              context_instance=RequestContext(req))


@csrf_exempt
@login_required()
@ajax_request
def save(req):
    condition_changeset = simplejson.loads(req.POST.get("data"))
    cond_type = req.POST.get("cond_type")
    cond_id = req.POST.get("related_id")
    resp_obj = {"success": True,
                "return_url": reverse("list_conditions", kwargs={"cond_type": cond_type, "id": cond_id})}

    try:
        if not any([condition_changeset[key] for key in condition_changeset.keys() if key != 'logic']):
            raise ValidationError("Esta condição não realiza nenhum operação.")

        if "extra_vars" in condition_changeset:
            condition_changeset["extra_vars"] = {condition['name']: condition['value'] for condition in
                                                 condition_changeset["extra_vars"]}

        if "id" in condition_changeset:  # ** Edit
            condition = get_object_or_None(Condition, pk=condition_changeset["id"])

            if condition:
                condition_columns = condition._meta.get_all_field_names()

                for condition_column in condition_columns:
                    if condition_column in condition_changeset:
                        setattr(condition, condition_column, condition_changeset[condition_column])

                condition.save()
                messages.success(req, "Condição alterada com sucesso.")

            else:
                raise ValidationError("Condição com id %d não encontrada" % condition_changeset['id'])
        else:                          # ** New
            condition = Condition.objects.create(**condition_changeset)

            related = get_related(cond_type, cond_id)

            if cond_type == "form":
                related.conditions.add(condition)
            elif cond_type == "confirmation":
                related.confirmation_conditions.add(condition)
            else:
                related.conditions.add(condition)

            if not condition.pk:
                raise ValidationError("Não foi possível criar essa condição.")

            messages.success(req, "Condição criada com sucesso.")
    except ValidationError as e:
        resp_obj["success"] = False
        resp_obj["message"] = e.messages

    return resp_obj


def get_related(cond_type, id):
    if cond_type in ('form', 'confirmation'):
        return Form.objects.get(pk=id)
    elif cond_type == 'field':
        field = Field.objects.get(pk=id)
        return field

@login_required()
def delete(req, id, cond_type, cond_id):
    try:
        condition = Condition.objects.get(pk=id)
        condition.delete()
        messages.success(req, "Condição removida com sucesso.")
    finally:
        return redirect(reverse("list_conditions", kwargs={"cond_type": cond_type, "id": cond_id}))
    return None