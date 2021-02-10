from rest_framework import serializers
from .models import Slot

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ('slotNo','carNo','isFree')