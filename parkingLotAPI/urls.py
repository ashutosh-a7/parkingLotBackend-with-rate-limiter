from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import SlotViewSet

router = routers.DefaultRouter()
router.register('slots',SlotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]