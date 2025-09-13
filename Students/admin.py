from django.contrib import admin

from Students.models import Student


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name','second_name','grade','gender']
