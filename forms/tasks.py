from celery import task
from django.core.management import call_command
import logging

logger = logging.getLogger("pastoral")

@task()
def cron():
    logger.debug("Running cron...")
    call_command('cron', interactive=True)