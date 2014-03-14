from datetime import timedelta, datetime
from rapidsms.router.api import send, lookup_connections
from django.db import models
from forms.models import Submission
from pastoral.models.configuration import Config
import logging

logger = logging.getLogger("pastoral")

class TimedTask(models.Model):
    form = models.ForeignKey('Form', related_name="tasks")
    submission_status = models.SmallIntegerField()
    status_to_change = models.SmallIntegerField(null=True)
    answer = models.CharField(max_length=Config.get("max_sms_length"))
    run_after_min = models.IntegerField()
    once = models.BooleanField(default=False)

    def run(self):
        submissions = self.form.submission_set.filter(created__lt=datetime.now() - timedelta(
            minutes=self.run_after_min), status=self.submission_status)

        for submission in submissions:
            if self.once:
                if self.tasks_ran.filter(submission=submission).count() > 0:
                    continue

            connections = lookup_connections(backend='purebros', identities=[submission.identity])
            answer = self.form.process_answer_template(self.answer, submission.context)
            logger.debug("Lembrete: %s - para %s" % (answer, submission.identity))
            send(answer, connections=connections)

            if self.once:
                self.tasks_ran.create(submission=submission)

            if self.status_to_change:
                submission.set_status(self.status_to_change)

    def pretty_submission_status(self):
        return Submission.STATUS_TYPES[self.submission_status][1]

    def pretty_status_to_change(self):
        if self.status_to_change:
            return Submission.STATUS_TYPES[self.status_to_change][1]
        else:
            return None

    @staticmethod
    def run_tasks():
        tasks = TimedTask.objects.all()  # TODO: LIMITAR APENAS A FORMULARIOS ATIVOS

        for task in tasks:
            task.run()

    class Meta:
        app_label = "forms"