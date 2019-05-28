from django.core.management.base import BaseCommand
from hello.models import Feature
import urllib.request
import json
import datetime


class Command(BaseCommand):
    help = 'Scrapes bicicas to obtain the details of all the docks.'
    def handle(self, *args, **options):
        self.stdout.write('\nScraping started at %s\n' % str(datetime.datetime.now()))
        with urllib.request.urlopen("https://ws2.bicicas.es/bench_status_map") as url:
            data = json.loads(url.read().decode())
        feature = Feature()
        feature.time_scrape = datetime.datetime.utcnow()
        feature.feature_collection = data
        feature.save()
        self.stdout.write('\nScraping ended at %s\n' % str(datetime.datetime.now()))
