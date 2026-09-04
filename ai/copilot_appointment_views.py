from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .copilot_appointment_tools import tool_confirm_reschedule, tool_confirm_cancel

@require_POST
def confirm_reschedule(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"message": "Please log in to use VirtualClinic AI."},
            status=401,
        )

    appointment_id = request.POST.get("appointment_id")
    new_start = request.POST.get("new_start")
    new_end = request.POST.get("new_end")

    result = tool_confirm_reschedule(
        request,
        appointment_id=appointment_id,
        new_start=new_start,
        new_end=new_end,
    )

    status = 200 if result.get("success") else 400

    return JsonResponse(result, status=status)


@require_POST
def confirm_cancel(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"message": "Please log in to use VirtualClinic AI."},
            status=401,
        )

    appointment_id = request.POST.get("appointment_id")

    result = tool_confirm_cancel(
        request,
        appointment_id=appointment_id,
    )

    status = 200 if result.get("success") else 400

    return JsonResponse(result, status=status)
