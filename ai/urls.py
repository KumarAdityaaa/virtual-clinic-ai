from django.urls import path

from . import views
from . import copilot_views
from . import copilot_history
from . import copilot_delete
from . import copilot_appointment_views



urlpatterns = [

    path("", views.health_check, name="health_check"),

    path("analyze/", views.analyze, name="analyze_symptoms"),

    path("review/", views.review, name="review_ai"),

    path("history/", views.history, name="ai_history"),

    path("copilot/", copilot_views.copilot, name="copilot"),

    path(
        "copilot/history/",
        copilot_history.conversations,
        name="copilot_history",
    ),

    path(
        "copilot/new/",
        copilot_history.new_conversation,
        name="copilot_new",
    ),

    path(
        "copilot/delete/<int:conversation_id>/",
        copilot_delete.delete_conversation,
        name="copilot_delete",
    ),

    path("copilot/appointments/confirm-reschedule/", copilot_appointment_views.confirm_reschedule, name="copilot_confirm_reschedule"),
    path("copilot/appointments/confirm-cancel/", copilot_appointment_views.confirm_cancel, name="copilot_confirm_cancel"),
]