from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from server.models import Account, Appointment, AIAnalysis, MedicalInfo
from .services import analyze_patient


def build_patient_context(patient):
    try:
        medical_info = MedicalInfo.objects.get(
            account=patient
        )
    except MedicalInfo.DoesNotExist:
        medical_info = None

    medical_history = []

    if medical_info:
        if medical_info.bloodType:
            medical_history.append(
                f"Blood type: {medical_info.bloodType}"
            )

        if medical_info.asthma:
            medical_history.append(
                "History of asthma"
            )

        if medical_info.diabetes:
            medical_history.append(
                "History of diabetes"
            )

        if medical_info.stroke:
            medical_history.append(
                "History of stroke"
            )

        if medical_info.alzheimer:
            medical_history.append(
                "History of Alzheimer's disease"
            )

        if medical_info.comments:
            medical_history.append(
                medical_info.comments
            )

    allergies = []

    if patient.profile.allergies:
        allergies.append(
            patient.profile.allergies.strip()
        )

    if medical_info and medical_info.allergy:
        allergies.append(
            medical_info.allergy.strip()
        )

    allergies = list(
        dict.fromkeys(
            allergy
            for allergy in allergies
            if allergy
        )
    )

    return {
        "name": str(patient.profile),
        "blood_type": (
            medical_info.bloodType
            if medical_info
            else "Not provided"
        ),
        "medical_history": medical_history,
        "allergies": allergies,
        "speciality": (
            patient.profile.speciality.name
            if patient.profile.speciality
            else "Not specified"
        ),
    }


def health_check(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Login required"},
            status=401
        )

    appointment_id = request.GET.get("appointment_id")
    appointment = None
    analysis = None
    patient_context = None
    previous_analyses = []

    if appointment_id:
        try:
            appointment = Appointment.objects.select_related(
                "ai_analysis",
                "patient",
                "doctor",
                "symptom"
            ).get(
                pk=int(appointment_id)
            )

            if request.user.account.role == Account.ACCOUNT_PATIENT:
                if appointment.patient != request.user.account:
                    return JsonResponse(
                        {
                            "error":
                                "You do not have permission to view this appointment."
                        },
                        status=403
                    )

            elif request.user.account.role == Account.ACCOUNT_DOCTOR:
                if appointment.doctor != request.user.account:
                    return JsonResponse(
                        {
                            "error":
                                "You do not have permission to view this appointment."
                        },
                        status=403
                    )

            else:
                return JsonResponse(
                    {
                        "error":
                            "You do not have permission to view AI analysis."
                    },
                    status=403
                )

            analysis = appointment.ai_analysis
            patient = appointment.patient

            patient_context = build_patient_context(
                patient
            )

            previous_analyses = list(
                AIAnalysis.objects.filter(
                    account=patient
                )
                .exclude(
                    id=appointment.ai_analysis_id
                )
                .order_by("-created")
                .values(
                    "prediction",
                    "priority",
                    "confidence",
                    "created"
                )[:5]
            )

        except (
            ValueError,
            Appointment.DoesNotExist
        ):
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
            "patient_context": patient_context,
            "previous_analyses": previous_analyses,
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

    symptoms = request.POST.get(
        "symptoms",
        ""
    ).strip()

    appointment_id = request.POST.get(
        "appointment_id"
    )

    if not symptoms:
        return JsonResponse(
            {
                "error":
                    "Please enter at least one symptom."
            },
            status=400
        )

    if not appointment_id:
        return JsonResponse(
            {"error": "Appointment is required."},
            status=400
        )

    try:
        appointment = Appointment.objects.select_related(
            "patient",
            "doctor"
        ).get(
            pk=int(appointment_id)
        )

    except (
        ValueError,
        Appointment.DoesNotExist
    ):
        return JsonResponse(
            {"error": "Appointment not found."},
            status=404
        )

    if request.user.account.role == Account.ACCOUNT_PATIENT:
        if appointment.patient != request.user.account:
            return JsonResponse(
                {
                    "error":
                        "You do not have permission to analyze this appointment."
                },
                status=403
            )

    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        if appointment.doctor != request.user.account:
            return JsonResponse(
                {
                    "error":
                        "You do not have permission to analyze this appointment."
                },
                status=403
            )

    else:
        return JsonResponse(
            {
                "error":
                    "You do not have permission to perform AI analysis."
            },
            status=403
        )

    patient = appointment.patient

    try:
        medical_info = MedicalInfo.objects.get(
            account=patient
        )
    except MedicalInfo.DoesNotExist:
        medical_info = None

    medical_history = []

    if medical_info:
        if medical_info.bloodType:
            medical_history.append(
                f"Blood type: {medical_info.bloodType}"
            )

        if medical_info.asthma:
            medical_history.append(
                "History of asthma"
            )

        if medical_info.diabetes:
            medical_history.append(
                "History of diabetes"
            )

        if medical_info.stroke:
            medical_history.append(
                "History of stroke"
            )

        if medical_info.alzheimer:
            medical_history.append(
                "History of Alzheimer's disease"
            )

        if medical_info.comments:
            medical_history.append(
                f"Additional information: "
                f"{medical_info.comments}"
            )

    if medical_history:
        medical_history_text = "\n".join(
            f"- {item}"
            for item in medical_history
        )
    else:
        medical_history_text = (
            "No known medical history provided."
        )

    allergy_values = []

    if patient.profile.allergies:
        allergy_values.append(
            patient.profile.allergies.strip()
        )

    if medical_info and medical_info.allergy:
        allergy_values.append(
            medical_info.allergy.strip()
        )

    allergy_values = list(
        dict.fromkeys(
            allergy
            for allergy in allergy_values
            if allergy
        )
    )

    allergies = "; ".join(
        allergy_values
    )

    previous_analyses = list(
        AIAnalysis.objects.filter(
            account=patient
        )
        .exclude(
            id=appointment.ai_analysis_id
        )
        .order_by("-created")
        .values(
            "prediction",
            "priority",
            "confidence"
        )[:5]
    )

    result = analyze_patient(
        symptoms=symptoms.split(","),
        medical_history=medical_history_text,
        allergies=allergies,
        previous_analyses=previous_analyses
    )

    analysis = AIAnalysis.objects.create(
        account=patient,
        symptoms=symptoms,
        prediction=result["prediction"],
        possible_conditions=result.get(
            "possible_conditions",
            []
        ),
        priority=result["priority"],
        confidence=result["confidence"],
        explanation=result["explanation"],
    )

    appointment.ai_analysis = analysis
    appointment.save()

    return JsonResponse(result)


@csrf_exempt
def review(request):
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

    if request.user.account.role != Account.ACCOUNT_DOCTOR:
        return JsonResponse(
            {
                "error":
                    "Only doctors can review AI analysis."
            },
            status=403
        )

    appointment_id = request.POST.get(
        "appointment_id"
    )

    doctor_review = request.POST.get(
        "doctor_review",
        ""
    ).strip()

    final_diagnosis = request.POST.get(
        "final_diagnosis",
        ""
    ).strip()

    if not appointment_id:
        return JsonResponse(
            {"error": "Appointment is required."},
            status=400
        )

    if doctor_review not in [
        "ACCEPTED",
        "MODIFIED",
        "REJECTED"
    ]:
        return JsonResponse(
            {"error": "Invalid review decision."},
            status=400
        )

    try:
        appointment = Appointment.objects.select_related(
            "ai_analysis"
        ).get(
            pk=int(appointment_id),
            doctor=request.user.account
        )

    except (
        ValueError,
        Appointment.DoesNotExist
    ):
        return JsonResponse(
            {"error": "Appointment not found."},
            status=404
        )

    if not appointment.ai_analysis:
        return JsonResponse(
            {
                "error":
                    "No AI analysis exists for this appointment."
            },
            status=400
        )

    analysis = appointment.ai_analysis

    analysis.doctor_review = doctor_review
    analysis.final_diagnosis = final_diagnosis
    analysis.reviewed_by = request.user.account
    analysis.reviewed_at = timezone.now()
    analysis.save()

    return JsonResponse(
        {
            "success": True,
            "doctor_review": analysis.doctor_review,
            "final_diagnosis": analysis.final_diagnosis,
            "reviewed_at": (
                analysis.reviewed_at.isoformat()
            ),
        }
    )

    

def history(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Login required"},
            status=401
        )

    account = request.user.account

    if account.role == Account.ACCOUNT_PATIENT:

        analyses = (
            AIAnalysis.objects
            .filter(
                account=account
            )
            .select_related(
                "reviewed_by"
            )
            .prefetch_related(
                "appointment"
            )
            .order_by("-created")
        )

        patient = account

    elif account.role == Account.ACCOUNT_DOCTOR:

        analyses = (
            AIAnalysis.objects
            .filter(
                appointment__doctor=account
            )
            .select_related(
                "account",
                "reviewed_by"
            )
            .prefetch_related(
                "appointment"
            )
            .order_by("-created")
            .distinct()
        )

        patient = None

    else:
        return JsonResponse(
            {
                "error":
                    "You do not have permission to view AI history."
            },
            status=403
        )

    return render(
        request,
        "ai/history.html",
        {
            "analyses": analyses,
            "patient": patient,
        }
    )