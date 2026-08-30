from django.contrib.auth.models import User
from server.models import (
    Account,
    Profile,
    MedicalInfo,
    Speciality,
    Location,
    Hospital,
    Symptom,
)


def get_or_create_user(email, password, first_name, last_name, role, speciality=None):
    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    if created:
        user.set_password(password)
        user.save()

    profile, _ = Profile.objects.get_or_create(
        firstname=first_name,
        lastname=last_name,
        defaults={
            "speciality": speciality,
        },
    )

    if speciality and profile.speciality_id != speciality.id:
        profile.speciality = speciality
        profile.save()

    account, _ = Account.objects.get_or_create(
        user=user,
        defaults={
            "profile": profile,
            "role": role,
        },
    )

    MedicalInfo.objects.get_or_create(account=account)

    return account


def seed():
    print("Seeding Virtual Clinic demo data...")

    # Specialities
    general_medicine, _ = Speciality.objects.get_or_create(
        name="General Medicine",
        defaults={"description": "Primary and general medical care"},
    )

    cardiology, _ = Speciality.objects.get_or_create(
        name="Cardiology",
        defaults={"description": "Heart and cardiovascular care"},
    )

    pulmonology, _ = Speciality.objects.get_or_create(
        name="Pulmonology",
        defaults={"description": "Respiratory and lung care"},
    )

    # Hospitals
    location1, _ = Location.objects.get_or_create(
        address="MG Road",
        defaults={
            "city": "Bengaluru",
            "zip": "560001",
            "state": "Karnataka",
            "country": "India",
        },
    )

    hospital1, _ = Hospital.objects.get_or_create(
        name="Virtual Care Hospital",
        defaults={
            "phone": "9876543210",
            "location": location1,
        },
    )

    location2, _ = Location.objects.get_or_create(
        address="Park Street",
        defaults={
            "city": "Kolkata",
            "zip": "700016",
            "state": "West Bengal",
            "country": "India",
        },
    )

    hospital2, _ = Hospital.objects.get_or_create(
        name="City Medical Centre",
        defaults={
            "phone": "9876501234",
            "location": location2,
        },
    )

    # Symptoms
    symptoms = [
        ("Fever", "Elevated body temperature"),
        ("Cough", "Persistent or recurring cough"),
        ("Fatigue", "Feeling unusually tired"),
        ("Body Pain", "General body aches"),
        ("Sore Throat", "Pain or irritation in the throat"),
        ("Breathing Difficulty", "Difficulty breathing or shortness of breath"),
        ("Vomiting", "Feeling or act of vomiting"),
        ("Diarrhea", "Frequent loose stools"),
        ("Stomach Pain", "Abdominal discomfort or pain"),
        ("Headache", "Pain or pressure in the head"),
    ]

    for name, description in symptoms:
        Symptom.objects.get_or_create(
            name=name,
            defaults={"description": description},
        )

    # Users
    admin = get_or_create_user(
        "admin@virtualclinic.com",
        "Admin@123",
        "System",
        "Admin",
        Account.ACCOUNT_ADMIN,
    )

    patient1 = get_or_create_user(
        "patient1@virtualclinic.com",
        "Patient@123",
        "Aarav",
        "Sharma",
        Account.ACCOUNT_PATIENT,
    )

    patient2 = get_or_create_user(
        "patient2@virtualclinic.com",
        "Priya",
        "Priya",
        "Mehta",
        Account.ACCOUNT_PATIENT,
    )

    doctor1 = get_or_create_user(
        "doctor1@virtualclinic.com",
        "Doctor@123",
        "Mahesh",
        "Suresh",
        Account.ACCOUNT_DOCTOR,
        general_medicine,
    )

    doctor2 = get_or_create_user(
        "doctor2@virtualclinic.com",
        "Doctor@123",
        "Ananya",
        "Rao",
        Account.ACCOUNT_DOCTOR,
        cardiology,
    )

    doctor3 = get_or_create_user(
        "doctor3@virtualclinic.com",
        "Doctor@123",
        "Rohan",
        "Kapoor",
        Account.ACCOUNT_DOCTOR,
        pulmonology,
    )

    lab = get_or_create_user(
        "lab@virtualclinic.com",
        "Lab@123",
        "Central",
        "Diagnostics",
        Account.ACCOUNT_LAB,
    )

    chemist = get_or_create_user(
        "chemist@virtualclinic.com",
        "Chemist@123",
        "Medi",
        "Pharmacy",
        Account.ACCOUNT_CHEMIST,
    )

    print("Demo data created successfully.")

    print("\nUsers:")
    print("Admin: admin@virtualclinic.com / Admin@123")
    print("Patient: patient1@virtualclinic.com / Patient@123")
    print("Patient: patient2@virtualclinic.com / Patient@123")
    print("Doctor: doctor1@virtualclinic.com / Doctor@123")
    print("Doctor: doctor2@virtualclinic.com / Doctor@123")
    print("Doctor: doctor3@virtualclinic.com / Doctor@123")
    print("Lab: lab@virtualclinic.com / Lab@123")
    print("Chemist: chemist@virtualclinic.com / Chemist@123")