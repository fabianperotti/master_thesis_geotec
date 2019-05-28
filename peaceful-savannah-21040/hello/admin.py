from django.contrib import admin
from .models import Feature
# Register your models here.

admin.register(Feature)(admin.ModelAdmin)
