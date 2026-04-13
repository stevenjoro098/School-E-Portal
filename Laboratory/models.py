from django.db import models

# Create your models here.
class LabEquipment(models.Model):
    name = models.CharField(max_length=200)
    available_quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='laboratory', blank=True)
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.available_quantity}"