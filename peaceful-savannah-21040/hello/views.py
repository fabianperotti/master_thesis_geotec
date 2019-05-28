import os
import requests
from django.shortcuts import render
from django.http import HttpResponse
# from .models import Station_record
from .models import Feature 
import urllib.request
import json
import datetime

# Create your views here.
def index(request):
    # return HttpResponse(getJson()['features'])
    return HttpResponse(getJson())

# def db(request):
#     station_records = Station_record.objects.all()
#     return render(request, 'db.html', {'station_records': station_records})
def db(request):
    features = Feature.objects.all()
    return render(request, 'db.html', {'features': features})


def getJson():
    with urllib.request.urlopen("https://ws2.bicicas.es/bench_status_map") as url:
        data = json.loads(url.read().decode())
        return(data)

# def addDb():
#     data2 = getJson()['features']
#     for station in data2:
#         name_i = station['properties']['name']
#         station_id_i = int(name_i.split(".")[0])
#         bk_total = station['properties']['bikes_total']
#         bk_av = station['properties']['bikes_available']
#         anchors_i = station['properties']['anchors']
#         last_seen_i = station['properties']['last_seen']
#         # online = station['properties']['online']
#         # nr_loans = station['properties']['number_loans']
#         # incidents = station['properties']['incidents']
#         time_i = datetime.datetime.utcnow()
#         station_record = Station_record()
#         station_record.station_id = station_id_i #int(name_i.split(".")[0])
#         station_record.name = name_i
#         station_record.anchorsb = anchors_i
#         station_record.time_scrap = time_i
#         station_record.bikes_total = bk_total
#         station_record.bikes_available = bk_av
#         station_record.last_seen = last_seen_i
#         station_record.save()
#         return(station_record)
