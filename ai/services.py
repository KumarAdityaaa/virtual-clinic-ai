def analyze_symptoms(symptoms):
    symptoms = [s.strip().lower() for s in symptoms if s.strip()]

    if not symptoms:
        return {
            "prediction": "No symptoms provided",
            "priority": "LOW",
            "confidence": 0.0,
        }

    return {
        "prediction": "Preliminary analysis pending",
        "priority": "MEDIUM",
        "confidence": 0.0,
    }