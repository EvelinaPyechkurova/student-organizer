import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from notifications.scheduler import send_notifications

TIME_INTERVAL = timedelta(minutes=1)

class Command(BaseCommand):
    help = "Continuously send scheduled notifications every minute"
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Notification loop started..."))

        while True:
            now = datetime.now()
            send_notifications()
            next_minute = (now + TIME_INTERVAL).replace(second=0, microsecond=0)
            sleep_seconds = (next_minute - datetime.now()).total_seconds
            time.sleep(sleep_seconds)