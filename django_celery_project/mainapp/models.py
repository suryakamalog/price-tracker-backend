from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Product(models.Model):
    website = models.CharField(max_length=10)
    url = models.TextField()
    price = models.IntegerField(null=True)
    users = models.ManyToManyField(User)