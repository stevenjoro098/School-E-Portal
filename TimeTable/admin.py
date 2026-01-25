from django.contrib import admin
from .models import Day, TimetableSlot

# Register your models here.
@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ['order','day']

@admin.register(TimetableSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['grade','day','subject','label','start_time','end_time','teacher']
    list_filter = ['day','teacher','grade']
