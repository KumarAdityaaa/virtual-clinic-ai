from django.urls import path

from . import views


urlpatterns = [
    path("", views.health_check, name="health_check"),
    path("analyze/", views.analyze, name="analyze_symptoms"),
    path("review/", views.review, name="review_ai"),
    path("history/", views.history, name="ai_history"),
]