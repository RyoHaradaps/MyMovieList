from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Watchlist

class Command(BaseCommand):
    help = 'Fix Watchlist entries with NULL added_on by setting them to now.'

    def handle(self, *args, **options):
        null_added_on = Watchlist.objects.filter(added_on__isnull=True)
        count = null_added_on.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No Watchlist entries with NULL added_on.'))
            return
        now = timezone.now()
        null_added_on.update(added_on=now)
        self.stdout.write(self.style.SUCCESS(f'Updated {count} Watchlist entries with NULL added_on.')) 