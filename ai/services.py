def analyze_symptoms(symptoms):
    symptoms = {s.strip().lower() for s in symptoms if s.strip()}

    rules = {
        "Flu-like illness": {
            "symptoms": {"fever", "cough", "fatigue", "body pain"},
            "priority": "MEDIUM",
        },
        "Respiratory infection": {
            "symptoms": {"cough", "sore throat", "breathing difficulty", "fever"},
            "priority": "HIGH",
        },
        "Gastrointestinal infection": {
            "symptoms": {"vomiting", "diarrhea", "stomach pain", "fever"},
            "priority": "MEDIUM",
        },
    }

    best_match = None
    best_score = 0

    for condition, rule in rules.items():
        matched = symptoms.intersection(rule["symptoms"])
        score = len(matched)

        if score > best_score:
            best_score = score
            best_match = {
                "prediction": condition,
                "matched_symptoms": list(matched),
                "priority": rule["priority"],
            }

    if best_match is None:
        return {
            "prediction": "Insufficient information",
            "priority": "LOW",
            "confidence": 0.0,
            "matched_symptoms": [],
        }

    confidence = round(best_score / len(rule["symptoms"]) * 100, 2)

    return {
        "prediction": best_match["prediction"],
        "priority": best_match["priority"],
        "confidence": confidence,
        "matched_symptoms": best_match["matched_symptoms"],
    }