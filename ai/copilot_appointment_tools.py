from datetime import datetime

from django.db.models import Q
from django.utils import timezone

from server import logger
from server import message
from server.models import Account, Action, Appointment


def tool_get_appointment(request, appointment_id=None, id=None):
    account = request.user.account

    if appointment_id is None:
        appointment_id = id

    if not appointment_id:
        return {
            "success": False,
            "error": "Appointment ID is required.",
        }

    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        return {
            "success": False,
            "error": "Appointment not found.",
        }

    if (
        account.role == Account.ACCOUNT_PATIENT
        and appointment.patient != account
    ):
        return {
            "success": False,
            "error": "You do not have access to this appointment.",
        }

    if (
        account.role == Account.ACCOUNT_DOCTOR
        and appointment.doctor != account
    ):
        return {
            "success": False,
            "error": "You do not have access to this appointment.",
        }

    return {
        "success": True,
        "data": {
            "id": appointment.pk,
            "doctor": str(appointment.doctor),
            "patient": str(appointment.patient),
            "start_time": appointment.startTime.isoformat(),
            "end_time": appointment.endTime.isoformat(),
            "status": appointment.status,
            "type": appointment.appointment_type,
            "description": appointment.description,
            "hospital": appointment.hospital.name,
            "symptom": appointment.symptom.name,
        },
    }


def tool_prepare_reschedule(
    request,
    appointment_id=None,
    id=None,
    new_start=None,
    new_end=None,
):
    account = request.user.account

    if appointment_id is None:
        appointment_id = id

    if not appointment_id:
        return {
            "success": False,
            "error": "Appointment ID is required.",
        }

    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        return {
            "success": False,
            "error": "Appointment not found.",
        }

    if (
        account.role == Account.ACCOUNT_PATIENT
        and appointment.patient != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to modify this appointment.",
        }

    if (
        account.role == Account.ACCOUNT_DOCTOR
        and appointment.doctor != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to modify this appointment.",
        }

    if not new_start:
        return {
            "success": False,
            "error": "The new start time is required.",
        }

    try:
        start_time = datetime.fromisoformat(new_start)

        if new_end:
            end_time = datetime.fromisoformat(new_end)
        else:
            duration = appointment.endTime - appointment.startTime
            end_time = start_time + duration

    except ValueError:
        return {
            "success": False,
            "error": "Invalid date or time format.",
        }

    if timezone.is_naive(start_time):
        start_time = timezone.make_aware(start_time)

    if timezone.is_naive(end_time):
        end_time = timezone.make_aware(end_time)

    if end_time <= start_time:
        return {
            "success": False,
            "error": "The end time must be after the start time.",
        }

    conflict = Appointment.objects.filter(
        ~Q(pk=appointment.pk),
        Q(status="Active"),
        Q(doctor=appointment.doctor) | Q(patient=appointment.patient),
        Q(
            startTime__range=(
                start_time,
                end_time,
            )
        )
        | Q(
            endTime__range=(
                start_time,
                end_time,
            )
        ),
    ).exists()

    if conflict:
        return {
            "success": False,
            "error": "The requested time conflicts with another active appointment.",
        }

    return {
        "success": True,
        "requires_confirmation": True,
        "data": {
            "id": appointment.pk,
            "doctor": str(appointment.doctor),
            "patient": str(appointment.patient),
            "old_start": appointment.startTime.isoformat(),
            "old_end": appointment.endTime.isoformat(),
            "new_start": start_time.isoformat(),
            "new_end": end_time.isoformat(),
        },
    }


def tool_confirm_reschedule(
    request,
    appointment_id=None,
    id=None,
    new_start=None,
    new_end=None,
):
    account = request.user.account

    if appointment_id is None:
        appointment_id = id

    if not appointment_id or not new_start:
        return {
            "success": False,
            "error": "Appointment ID and new start time are required.",
        }

    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        return {
            "success": False,
            "error": "Appointment not found.",
        }

    if (
        account.role == Account.ACCOUNT_PATIENT
        and appointment.patient != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to modify this appointment.",
        }

    if (
        account.role == Account.ACCOUNT_DOCTOR
        and appointment.doctor != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to modify this appointment.",
        }

    try:
        start_time = datetime.fromisoformat(new_start)

        if new_end:
            end_time = datetime.fromisoformat(new_end)
        else:
            duration = appointment.endTime - appointment.startTime
            end_time = start_time + duration

    except ValueError:
        return {
            "success": False,
            "error": "Invalid date or time format.",
        }

    if timezone.is_naive(start_time):
        start_time = timezone.make_aware(start_time)

    if timezone.is_naive(end_time):
        end_time = timezone.make_aware(end_time)

    if end_time <= start_time:
        return {
            "success": False,
            "error": "The end time must be after the start time.",
        }

    conflict = Appointment.objects.filter(
        ~Q(pk=appointment.pk),
        Q(status="Active"),
        Q(doctor=appointment.doctor) | Q(patient=appointment.patient),
        Q(
            startTime__range=(
                start_time,
                end_time,
            )
        )
        | Q(
            endTime__range=(
                start_time,
                end_time,
            )
        ),
    ).exists()

    if conflict:
        return {
            "success": False,
            "error": "The requested time conflicts with another active appointment.",
        }

    appointment.startTime = start_time
    appointment.endTime = end_time
    appointment.save()

    logger.log(
        Action.ACTION_APPOINTMENT,
        "Appointment Updated by AI Copilot",
        account,
    )

    if account.role == Account.ACCOUNT_PATIENT:
        message.send_appointment_update(
            request,
            appointment,
            appointment.doctor,
        )
    else:
        message.send_appointment_update(
            request,
            appointment,
            appointment.patient,
        )

    return {
        "success": True,
        "data": {
            "id": appointment.pk,
            "doctor": str(appointment.doctor),
            "patient": str(appointment.patient),
            "start_time": appointment.startTime.isoformat(),
            "end_time": appointment.endTime.isoformat(),
            "status": appointment.status,
        },
    }


def tool_prepare_cancel(request, appointment_id=None, id=None):
    account = request.user.account

    if appointment_id is None:
        appointment_id = id

    if not appointment_id:
        return {
            "success": False,
            "error": "Appointment ID is required.",
        }

    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        return {
            "success": False,
            "error": "Appointment not found.",
        }

    if (
        account.role == Account.ACCOUNT_PATIENT
        and appointment.patient != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to modify this appointment.",
        }

    if (
        account.role == Account.ACCOUNT_DOCTOR
        and appointment.doctor != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to modify this appointment.",
        }

    if appointment.status == "Cancelled":
        return {
            "success": False,
            "error": "This appointment is already cancelled.",
        }

    return {
        "success": True,
        "requires_confirmation": True,
        "data": {
            "id": appointment.pk,
            "doctor": str(appointment.doctor),
            "patient": str(appointment.patient),
            "start_time": appointment.startTime.isoformat(),
            "end_time": appointment.endTime.isoformat(),
            "status": appointment.status,
        },
    }


def tool_confirm_cancel(request, appointment_id=None, id=None):
    account = request.user.account

    if appointment_id is None:
        appointment_id = id

    if not appointment_id:
        return {
            "success": False,
            "error": "Appointment ID is required.",
        }

    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        return {
            "success": False,
            "error": "Appointment not found.",
        }

    if (
        account.role == Account.ACCOUNT_PATIENT
        and appointment.patient != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to cancel this appointment.",
        }

    if (
        account.role == Account.ACCOUNT_DOCTOR
        and appointment.doctor != account
    ):
        return {
            "success": False,
            "error": "You do not have permission to cancel this appointment.",
        }

    if appointment.status == "Cancelled":
        return {
            "success": False,
            "error": "This appointment is already cancelled.",
        }

    appointment.status = "Cancelled"
    appointment.save(update_fields=["status"])

    logger.log(
        Action.ACTION_APPOINTMENT,
        "Appointment Cancelled by AI Copilot",
        account,
    )

    if account.role == Account.ACCOUNT_PATIENT:
        message.send_appointment_cancel(
            request,
            appointment,
            appointment.doctor,
        )
    else:
        message.send_appointment_cancel(
            request,
            appointment,
            appointment.patient,
        )

    return {
        "success": True,
        "data": {
            "id": appointment.pk,
            "doctor": str(appointment.doctor),
            "patient": str(appointment.patient),
            "status": appointment.status,
        },
    }
