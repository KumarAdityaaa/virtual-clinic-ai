from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import analyze_symptoms


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

    return JsonResponse(result)