from django.urls import path
from . import views

urlpatterns = [
    path("", views.health_check, name="health_check"),
    path("analyze/", views.analyze, name="analyze_symptoms"),
]