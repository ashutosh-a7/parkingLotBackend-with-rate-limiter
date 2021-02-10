from django.db import models

# Create your models here.

class Slot(models.Model):
    slotNo = models.IntegerField()
    carNo = models.IntegerField(null=True,db_index=True)
    isFree = models.BooleanField(default=True)

