# Medical Diagnosis using Knowledge Representation

def diagnose(symptoms):
    knowledge_base = {
        ("fever", "cough", "fatigue"): "Flu",
        ("fever", "rash"): "Measles",
        ("headache", "nausea"): "Migraine",
        ("chest pain", "shortness of breath"): "Heart Disease"
    }

    for cond, disease in knowledge_base.items():
        if all(s in symptoms for s in cond):
            return disease
    return "No diagnosis found"


if __name__ == "__main__":
    symptoms = input("Enter symptoms separated by commas: ").lower().split(",")
    symptoms = [s.strip() for s in symptoms]
    print("Possible Diagnosis:", diagnose(symptoms))
