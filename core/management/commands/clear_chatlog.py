from django.core.management.base import BaseCommand

from core.models import ChatLog


class Command(BaseCommand):
    help = "Clear all AI chat logs."

    def handle(self, *args, **options):
        deleted, _ = ChatLog.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} chat logs."))
