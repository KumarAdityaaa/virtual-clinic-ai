from .copilot import get_my_appointments


def tool_get_my_appointments(request):
    return {
        "success": True,
        "data": get_my_appointments(request),
    }
