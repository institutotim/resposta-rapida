from annoying.functions import get_object_or_None
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from forms.models import Form, Submission
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.router import lookup_connections


def forms_list(req):
    return render(req, "web/list.html", {"forms": Form.objects.filter(enable_web=True)})


def view_form(req, form_id):
    form = get_object_or_None(Form, pk=form_id)

    if not form:
        return redirect(reverse(forms_list))
    fields = form.fields.all()
    return render(req, "web/view.html", {"form": form, "fields": fields})


def submit_form(req, form_id):
    try:
        form = get_object_or_None(Form, pk=form_id)
        fields = []
        for field in form.fields.all():
            fields.append(req.POST[field.name])

        sms = IncomingMessage(text=form.separator.join(fields),
                              connection=lookup_connections("web", req.META["REMOTE_ADDR"].replace('.', ''))[0])
        answer, submission = form.process_submission(sms, Submission.TYPE_WEB, return_submission=True)

        req.session["last_submission"] = {"form": form, "answer": answer, "submission": submission}

        return redirect(reverse("web_process_submission"))
    except Exception as e:
        # TODO: Logar
        return redirect(reverse("web_answer_form", kwargs={"form_id": form.pk}))


def process_submission(req):
    if not "last_submission" in req.session:
        # TODO: Logar
        return redirect(reverse("web"))

    state = req.session.pop("last_submission")

    return render(req, "web/process.html", state)


def confirm_submission(req, submission_id, confirmation):
    submission = get_object_or_None(Submission, pk=submission_id)

    if confirmation == "confirmar":
        submission.status = Submission.CONFIRMED
        answer = submission.form.ans_positive_confirmation
    else:
        submission.status = Submission.CANCELED
        answer = submission.form.ans_negative_confirmation

    submission.save()

    req.session["last_submission"] = {"answer": answer, "submission": {"status": 0}}

    return redirect(reverse("web_process_submission"))