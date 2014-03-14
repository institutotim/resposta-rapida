# encoding: utf-8
from time import sleep

from annoying.functions import get_object_or_None
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from annoying.decorators import ajax_request
from forms.models import TimedTask, Form


def set_task_values(obj, values):
    task_columns = obj._meta.get_all_field_names()

    for task_column in task_columns:
        if task_column in values:
            updated_value = values[task_column]
            try:
                if task_column == 'once':
                    updated_value = bool(int(updated_value))
                elif task_column == 'status_to_change' and updated_value == '-1':
                    updated_value = None
                elif task_column == 'form':
                    form = get_object_or_None(Form, pk=updated_value)
                    if not form:
                        raise ValidationError("Formulário não encontrado")

                    updated_value = form
            except ValueError:
                updated_value = None

            if updated_value is not None:
                setattr(obj, task_column, updated_value)


@csrf_exempt
@login_required()
@ajax_request
def save(req):
    task_changeset = simplejson.loads(req.POST.get("task"))
    resp = {"success": True}

    if "pk" in task_changeset:
        try:
            task_db = get_object_or_None(TimedTask, pk=task_changeset['pk'])

            if task_db:
                set_task_values(task_db, task_changeset)
                task_db.save()

                resp["task"] = task_changeset
            else:
                raise ValueError()
        except ValueError:
            resp["success"] = False
            resp["error"] = u"Não foi possível encontrar a Task com ID '%d'" % task_changeset.pk
        except ValidationError as e:
            resp["success"] = False
            resp["error"] = e.messages
    else:
        try:
            task = TimedTask()
            set_task_values(task, task_changeset)
            task.full_clean()
            task.save()

            task_changeset["pk"] = task.pk

            resp["task"] = task_changeset

        except ValidationError as e:
            resp["success"] = False
            resp["error"] = e.messages

    return resp


@csrf_exempt
@login_required()
@ajax_request
def delete(req, id):
    task = get_object_or_None(TimedTask, pk=id)

    if task:
        task.delete()

        return {"success": True}
    else:
        return {"success": False, "error": u"Não foi possível encontrar a Task com ID '%s'" % id}