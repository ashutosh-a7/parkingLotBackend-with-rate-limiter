from django.db import models

# Create your models here.

class Slot(models.Model):
    slotNo = models.IntegerField()
    carNo = models.CharField(null=True,db_index=True,max_length=24)
    isFree = models.BooleanField(default=True)

