from django.core.management.base import BaseCommand, CommandError
from forms.models.timed_tasks import TimedTask
from forms.models.submission import Submission
from lock import acquire_lock, release_lock
import logging

logger = logging.getLogger("pastoral")


class Command(BaseCommand):
    help = "Executa tarefas dependente de intervalos"

    def handle(self, *args, **options):
        logger.debug("Trying to acquire lock...")

        lock = acquire_lock("cron_lock")
        if lock:
            try:
                logger.debug("Lock acquired, running timed tasks...")
                TimedTask.run_tasks()

                logger.debug("Saving pending submissions to the remote server...")
                Submission.retry_pending()

                logger.debug("Done")

            finally:
                release_lock(lock)
        else:
            logger.warning("Cron Process still running, skipping...")