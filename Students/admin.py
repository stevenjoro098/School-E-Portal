from django.contrib import admin
from django.utils.html import format_html

from Students.models import Student


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name','second_name','grade','gender']
    list_filter = ['grade', 'gender']
    search_fields = ['first_name','second_name']
    readonly_fields = ['image_tag']

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;" />', obj.image.url)
        return "No Image"

    image_tag.short_description = 'Profile Image'