from django.contrib import admin
from .models import LabEquipment
# Register your models here.
@admin.register(LabEquipment)
class LabAdmin(admin.ModelAdmin):
    list_display = ['name','available_quantity','date_added']
    search_fields = ['name']