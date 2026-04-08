from django.db import models
from Subjects.models import Grade

category = (
    ('Story Book', 'Story Book'),
    ('TextBook','TextBook'),
    ('Encyclopedia','Encyclopedia'),
    ('Revision Material','Revision Material'),
    ('Others', 'Others')
            )

class Book(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200, choices=category)
    library_code = models.CharField(max_length=200, unique=True, blank=True)
    grade = models.ForeignKey(Grade, related_name='grade_books', null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ImageField(default='library/default.png',upload_to='library/books', blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}-{ self.category }-{self.available}"

class IssuedBooks(models.Model):
    book = models.ForeignKey(Book, related_name='issued_book', null=True, blank=True, on_delete=models.SET_NULL)
    issued_to = models.CharField(max_length=200)
    date_issued = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.book}-{self.issued_to}"