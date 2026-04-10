from django.contrib import admin
from .models import Book, IssuedBooks

# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title','category','grade','available']
    list_filter = ['grade','category','available']

@admin.register(IssuedBooks)
class IssuedBooksAdmin(admin.ModelAdmin):
    list_display = ['book','issued_to','date_issued','return_date']