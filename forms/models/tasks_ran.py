from django.db import models


class TasksRan(models.Model):
    task = models.ForeignKey('TimedTask', related_name="tasks_ran")
    submission = models.ForeignKey('Submission')

    class Meta:
        app_label = "forms"