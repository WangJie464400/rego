from django.db import models
from django.contrib.auth.models import AbstractUser


class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    calories = models.FloatField()

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    pass
    
    def __str__(self):
        return self.username