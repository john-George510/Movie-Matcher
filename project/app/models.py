from django.db import models
from ndarray import NDArrayField

class Actor(models.Model):
    name = models.CharField(max_length=100)
    encoding = NDArrayField(blank=True)
