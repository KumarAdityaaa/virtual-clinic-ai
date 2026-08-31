import os
import time

from google import genai
from google.genai import types
from google.genai.errors import ServerError


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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


def analyze_symptoms(symptoms):
    symptoms = [
        s.strip().lower()
        for s in symptoms
        if s.strip()
    ]

    if not symptoms:
        return {
            "prediction": "Insufficient information",
            "possible_conditions": [],
            "priority": "LOW",
            "confidence": 0.0,
            "matched_symptoms": [],
            "explanation": "No symptoms were provided."
        }

    prompt = f"""
You are an AI decision-support assistant inside a virtual clinic.

Analyze ONLY the symptoms explicitly listed below.

Patient symptoms:
{", ".join(symptoms)}

Important rules:
- Use ONLY the symptoms listed above.
- Do not introduce, assume, infer, or invent additional symptoms.
- matched_symptoms MUST contain only items from the patient symptoms list.
- Every reason MUST refer only to the supplied symptoms.
- Do not mention symptoms that were not supplied.
- Return 2 to 4 possible conditions when enough information exists.
- Rank the possibilities from most relevant to least relevant.
- Give a short reason for each possibility.
- Assign consultation priority as LOW, MEDIUM, or HIGH.
- Return confidence as a decimal between 0 and 1.
- This is NOT a final diagnosis.
- Do not prescribe medicines.
- Do not recommend treatment.
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