from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from server.models import Account, Appointment, AIAnalysis
from .services import analyze_symptoms


def health_check(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Login required"},
            status=401
        )

    appointment_id = request.GET.get("appointment_id")
    appointment = None
    analysis = None

    if appointment_id:
        try:
            appointment = Appointment.objects.select_related(
                "ai_analysis",
                "patient",
                "doctor"
            ).get(pk=int(appointment_id))

            if request.user.account.role == Account.ACCOUNT_PATIENT:
                if appointment.patient != request.user.account:
                    return JsonResponse(
                        {"error": "You do not have permission to view this appointment."},
                        status=403
                    )

            elif request.user.account.role == Account.ACCOUNT_DOCTOR:
                if appointment.doctor != request.user.account:
                    return JsonResponse(
                        {"error": "You do not have permission to view this appointment."},
                        status=403
                    )

            else:
                return JsonResponse(
                    {"error": "You do not have permission to view AI analysis."},
                    status=403
                )

            analysis = appointment.ai_analysis

        except (ValueError, Appointment.DoesNotExist):
            return JsonResponse(
                {"error": "Appointment not found."},
                status=404
            )

    return render(
        request,
        "ai/health_check.html",
        {
            "appointment_id": appointment_id,
            "appointment": appointment,
            "analysis": analysis,
        }
    )


@csrf_exempt
def analyze(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Login required"},
            status=401
        )

    symptoms = request.POST.get("symptoms", "").strip()
    appointment_id = request.POST.get("appointment_id")

    if not symptoms:
        return JsonResponse(
            {"error": "Please enter at least one symptom."},
            status=400
        )

    if not appointment_id:
        return JsonResponse(
            {"error": "Appointment is required."},
            status=400
        )

    try:
        appointment = Appointment.objects.get(
            pk=int(appointment_id)
        )
    except (ValueError, Appointment.DoesNotExist):
        return JsonResponse(
            {"error": "Appointment not found."},
            status=404
        )

    if request.user.account.role == Account.ACCOUNT_PATIENT:
        if appointment.patient != request.user.account:
            return JsonResponse(
                {"error": "You do not have permission to analyze this appointment."},
                status=403
            )

    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        if appointment.doctor != request.user.account:
            return JsonResponse(
                {"error": "You do not have permission to analyze this appointment."},
                status=403
            )

    else:
        return JsonResponse(
            {"error": "You do not have permission to perform AI analysis."},
            status=403
        )

    result = analyze_symptoms(symptoms.split(","))

    analysis = AIAnalysis.objects.create(
        account=request.user.account,
        symptoms=symptoms,
        prediction=result["prediction"],
        priority=result["priority"],
        confidence=result["confidence"],
        explanation=result["explanation"],
    )

    appointment.ai_analysis = analysis
    appointment.save()

    return JsonResponse(result)