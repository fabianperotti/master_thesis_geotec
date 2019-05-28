from django.db import models
from django.contrib.postgres.fields import JSONField
# Create your models here.
# class Greeting(models.Model):
#     when = models.DateTimeField('date created', auto_now_add=True)


class Feature(models.Model):
    time_scrape = models.DateTimeField()
    feature_collection = JSONField()

# class Station_record(models.Model):
#     station_id = models.IntegerField()
#     name =  models.CharField(max_length=100)
#     time_scrap = models.DateTimeField()
#     bikes_total = models.IntegerField()
#     bikes_available = models.IntegerField()
#     last_seen = models.DateTimeField()
#     anchorsb = JSONField()
