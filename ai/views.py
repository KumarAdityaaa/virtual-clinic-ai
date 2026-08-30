from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from server.models import Account, AIAnalysis
from .services import analyze_symptoms


def health_check(request):
    return render(request, "ai/health_check.html")


@csrf_exempt
def analyze(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    symptoms = request.POST.get("symptoms", "")
    symptom_list = symptoms.split(",")

    result = analyze_symptoms(symptom_list)

    if request.user.is_authenticated:
        AIAnalysis.objects.create(
            account=request.user.account,
            symptoms=symptoms,
            prediction=result["prediction"],
            priority=result["priority"],
            confidence=result["confidence"],
            explanation=result["explanation"],
        )

    return JsonResponse(result)