import os
import time

from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.errors import ServerError


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-flash-lite"

def _generate_analysis(prompt):
    models = [PRIMARY_MODEL, FALLBACK_MODEL]

    for model in models:
        for attempt in range(2):
            try:
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema={
                            "type": "object",
                            "properties": {
                                "possible_conditions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "condition": {
                                                "type": "string"
                                            },
                                            "reason": {
                                                "type": "string"
                                            }
                                        },
                                        "required": [
                                            "condition",
                                            "reason"
                                        ]
                                    }
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": [
                                        "LOW",
                                        "MEDIUM",
                                        "HIGH"
                                    ]
                                },
                                "confidence": {
                                    "type": "number"
                                },
                                "matched_symptoms": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "explanation": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "possible_conditions",
                                "priority",
                                "confidence",
                                "matched_symptoms",
                                "explanation"
                            ]
                        }
                    )
                )

            except ServerError as error:
                if (
                    getattr(error, "code", None) == 503
                    and attempt == 0
                ):
                    time.sleep(2)
                    continue

                if model == FALLBACK_MODEL:
                    raise

                break

    raise RuntimeError(
        "Gemini is temporarily unavailable."
    )


def analyze_patient(
    symptoms,
    medical_history="",
    allergies="",
    previous_analyses=None
):
    symptoms = [
        s.strip().lower()
        for s in symptoms
        if s.strip()
    ]

    previous_analyses = previous_analyses or []

    if not symptoms:
        return {
            "prediction": "Insufficient information",
            "possible_conditions": [],
            "priority": "LOW",
            "confidence": 0.0,
            "matched_symptoms": [],
            "explanation": "No symptoms were provided."
        }

    previous_context = "None available."

    if previous_analyses:
        previous_context = "\n".join(
            [
                (
                    f"- {item.get('prediction', 'Unknown')} "
                    f"(priority: {item.get('priority', 'Unknown')}, "
                    f"confidence: {item.get('confidence', 0)}%)"
                )
                for item in previous_analyses
            ]
        )

    prompt = f"""
You are an AI decision-support assistant inside a virtual clinic.

Create a PRELIMINARY patient-aware assessment for a doctor.

CURRENT SYMPTOMS:
{", ".join(symptoms)}

PATIENT MEDICAL HISTORY:
{medical_history or "No medical history provided."}

PATIENT ALLERGIES:
{allergies or "No allergies provided."}

PREVIOUS AI ASSESSMENTS:
{previous_context}

IMPORTANT RULES:
- Use the current symptoms as the primary evidence.
- Use medical history and allergies only as contextual information.
- Do not invent medical history, allergies, symptoms, test results, or diagnoses.
- matched_symptoms MUST contain only symptoms supplied in CURRENT SYMPTOMS.
- Every condition reason must be based on information actually supplied.
- Do not treat a previous AI result as a confirmed diagnosis.
- Return 2 to 4 possible conditions when enough information exists.
- Rank conditions from most relevant to least relevant.
- Assign priority as LOW, MEDIUM, or HIGH.
- Return confidence as a decimal between 0 and 1.
- Do not prescribe medicines.
- Do not recommend treatment.
- Do not claim certainty.
- Use cautious clinical language.
- The doctor is responsible for the final diagnosis.
"""

    response = _generate_analysis(prompt)

    result = (
        response.parsed
        if hasattr(response, "parsed") and response.parsed
        else response.text
    )

    if isinstance(result, dict):

        possible_conditions = result.get(
            "possible_conditions",
            []
        )

        if possible_conditions:
            result["prediction"] = possible_conditions[0].get(
                "condition",
                "Preliminary assessment"
            )
        else:
            result["prediction"] = "Insufficient information"

        result["confidence"] = round(
            float(result.get("confidence", 0.0)) * 100,
            2
        )

    return result


def analyze_symptoms(symptoms):
    """
    Backward-compatible wrapper for the existing AI workflow.
    """
    return analyze_patient(symptoms)