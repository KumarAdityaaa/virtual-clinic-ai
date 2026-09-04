from server.models import (
    Account,
    Appointment,
    MedicalInfo,
    MedicalTest,
    Prescription,
    Message,
    AIAnalysis,
    Action,
)


def get_account_from_request(request):
    return request.user.account


def get_user_role(account):
    return Account.to_name(account.role)


def get_copilot_context(request):
    account = get_account_from_request(request)

    return {
        "account_id": account.pk,
        "role": get_user_role(account),
        "name": str(account.profile),
    }


def get_my_appointments(request):
    account = get_account_from_request(request)

    if account.role == Account.ACCOUNT_DOCTOR:
        appointments = Appointment.objects.filter(
            doctor=account
        )

    elif account.role == Account.ACCOUNT_PATIENT:
        appointments = Appointment.objects.filter(
            patient=account
        )

    else:
        appointments = Appointment.objects.none()

    appointments = appointments.select_related(
        "doctor__profile",
        "patient__profile",
        "hospital",
        "symptom",
    ).order_by("startTime")

    return [
        {
            "id": appointment.pk,
            "url": f"/appointment/update/?pk={appointment.pk}",
            "doctor": str(appointment.doctor),
            "patient": str(appointment.patient),
            "date": appointment.startTime.strftime("%Y-%m-%d"),
            "start_time": appointment.startTime.strftime("%H:%M"),
            "end_time": appointment.endTime.strftime("%H:%M"),
            "status": appointment.status,
            "type": appointment.appointment_type,
            "hospital": appointment.hospital.name,
            "symptom": appointment.symptom.name,
            "description": appointment.description,
        }
        for appointment in appointments
    ]
