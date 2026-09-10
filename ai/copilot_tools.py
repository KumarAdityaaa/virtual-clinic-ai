from .copilot import (
    get_account_from_request,
    get_my_appointments,
    get_user_role,
)
from django.db.models import Q
from server.models import MedicalInfo, MedicalTest, Message, Prescription
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

def tool_get_medical_tests(request):
    account = get_account_from_request(request)
    role = get_user_role(account)

    qs = MedicalTest.objects.select_related(
        "patient",
        "doctor",
        "hospital",
    )

    if role == "Patient":
        qs = qs.filter(patient=account, private=False)
    elif role == "Doctor":
        qs = qs.filter(doctor=account)
    else:
        return {
            "success": False,
            "error": "You do not have permission to view medical tests.",
        }

    tests = []

    for test in qs.order_by("-date"):
        tests.append({
            "id": test.id,
            "name": test.name,
            "date": test.date.isoformat(),
            "hospital": str(test.hospital),
            "description": test.description,
            "doctor": str(test.doctor),
            "patient": str(test.patient),
            "private": test.private,
            "completed": test.completed,
        })

    return {
        "success": True,
        "data": tests,
        "count": len(tests),
    }
def tool_get_medical_info(request):
    account = get_account_from_request(request)

    try:
        info = MedicalInfo.objects.get(account=account)
    except MedicalInfo.DoesNotExist:
        return {
            "success": True,
            "data": None,
        }

    return {
        "success": True,
        "data": {
            "blood_type": info.bloodType,
            "allergy": info.allergy,
            "alzheimer": info.alzheimer,
            "asthma": info.asthma,
            "diabetes": info.diabetes,
            "stroke": info.stroke,
            "comments": info.comments,
        },
    }

def tool_get_my_messages(request):
    account = get_account_from_request(request)

    messages = Message.objects.select_related(
        "sender",
        "target",
    ).filter(
        Q(sender=account, sender_deleted=False)
        | Q(target=account, target_deleted=False)
    ).order_by("-timestamp")

    data = []

    for message in messages:
        data.append({
            "id": message.id,
            "sender": str(message.sender),
            "target": str(message.target),
            "header": message.header,
            "body": message.body,
            "timestamp": message.timestamp.isoformat(),
        })

    return {
        "success": True,
        "data": data,
        "count": len(data),
    }