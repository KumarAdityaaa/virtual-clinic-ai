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
                                "prediction": {
                                    "type": "string"
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": ["LOW", "MEDIUM", "HIGH"]
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
                                "prediction",
                                "priority",
                                "confidence",
                                "matched_symptoms",
                                "explanation"
                            ]
                        }
                    )
                )

            except ServerError as error:
                if getattr(error, "code", None) == 503 and attempt == 0:
                    time.sleep(2)
                    continue

                if model == FALLBACK_MODEL:
                    raise

                break

    raise RuntimeError("Gemini is temporarily unavailable.")


def analyze_symptoms(symptoms):
    symptoms = [s.strip() for s in symptoms if s.strip()]

    if not symptoms:
        return {
            "prediction": "Insufficient information",
            "priority": "LOW",
            "confidence": 0.0,
            "matched_symptoms": [],
            "explanation": "No symptoms were provided.",
        }

    prompt = f"""
You are an AI decision-support assistant inside a virtual clinic.

Analyze the patient's symptoms and return a PRELIMINARY assessment for a
doctor to review.

Patient symptoms:
{", ".join(symptoms)}

Rules:
- This is NOT a final diagnosis.
- Do not prescribe medicines.
- Do not claim certainty.
- Suggest a few possible conditions based only on the supplied symptoms.
- Assign consultation priority as LOW, MEDIUM, or HIGH.
- Return confidence as a decimal between 0 and 1.
- List only symptoms supplied by the patient in matched_symptoms.
- Explain briefly why the symptoms influenced the result.
- Keep the response concise and clinically cautious.
"""

    response = _generate_analysis(prompt)

    result = (
        response.parsed
        if hasattr(response, "parsed") and response.parsed
        else response.text
    )

    if isinstance(result, dict):
        result["confidence"] = round(
            float(result["confidence"]) * 100,
            2
        )

    return result