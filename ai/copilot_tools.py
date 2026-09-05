from .copilot import (
    get_account_from_request,
    get_my_appointments,
    get_user_role,
)
from server.models import Prescription


def tool_get_my_appointments(request):
    return {
        "success": True,
        "data": get_my_appointments(request),
    }


def tool_get_prescriptions(request):
    account = get_account_from_request(request)
    role = get_user_role(account)

    qs = Prescription.objects.select_related("patient", "doctor")

    if role == "Patient":
        qs = qs.filter(patient=account)
    elif role == "Doctor":
        qs = qs.filter(doctor=account)
    else:
        return {
            "success": False,
            "error": "You do not have permission to view prescriptions.",
        }

    prescriptions = []

    for p in qs.order_by("-date"):
        prescriptions.append({
            "id": p.id,
            "patient": str(p.patient),
            "doctor": str(p.doctor),
            "date": p.date.isoformat(),
            "medication": p.medication,
            "strength": p.strength,
            "instruction": p.instruction,
            "refill": p.refill,
            "active": p.active,
        })

    return {
        "success": True,
        "data": prescriptions,
        "count": len(prescriptions),
    }