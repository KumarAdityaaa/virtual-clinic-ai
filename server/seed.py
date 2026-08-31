from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import User

from server.models import (
    Account,
    Profile,
    MedicalInfo,
    MedicalTest,
    Prescription,
    Appointment,
    Speciality,
    Location,
    Hospital,
    Symptom,
)


def get_or_create_user(
    email,
    password,
    first_name,
    last_name,
    role,
    speciality=None,
):
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

    MedicalInfo.objects.get_or_create(
        account=account,
        defaults={
            "bloodType": "O+",
            "allergy": "",
            "alzheimer": False,
            "asthma": False,
            "diabetes": False,
            "stroke": False,
            "comments": "",
        },
    )

    return account


def seed():
    print("Seeding Virtual Clinic demo data...")

    # ---------------------------------------------------------
    # SPECIALITIES
    # ---------------------------------------------------------

    general_medicine, _ = Speciality.objects.get_or_create(
        name="General Medicine",
        defaults={
            "description": "Primary and general medical care",
        },
    )

    cardiology, _ = Speciality.objects.get_or_create(
        name="Cardiology",
        defaults={
            "description": "Heart and cardiovascular care",
        },
    )

    pulmonology, _ = Speciality.objects.get_or_create(
        name="Pulmonology",
        defaults={
            "description": "Respiratory and lung care",
        },
    )

    dermatology, _ = Speciality.objects.get_or_create(
        name="Dermatology",
        defaults={
            "description": "Skin and related conditions",
        },
    )

    # ---------------------------------------------------------
    # HOSPITALS
    # ---------------------------------------------------------

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

    location3, _ = Location.objects.get_or_create(
        address="Hauz Khas",
        defaults={
            "city": "New Delhi",
            "zip": "110016",
            "state": "Delhi",
            "country": "India",
        },
    )

    hospital3, _ = Hospital.objects.get_or_create(
        name="Metro Health Institute",
        defaults={
            "phone": "9876505678",
            "location": location3,
        },
    )

    # ---------------------------------------------------------
    # SYMPTOMS
    # ---------------------------------------------------------

    symptom_data = [
        ("Fever", "Elevated body temperature"),
        ("Cough", "Persistent or recurring cough"),
        ("Fatigue", "Feeling unusually tired"),
        ("Body Pain", "General body aches"),
        ("Sore Throat", "Pain or irritation in the throat"),
        (
            "Breathing Difficulty",
            "Difficulty breathing or shortness of breath",
        ),
        ("Vomiting", "Feeling or act of vomiting"),
        ("Diarrhea", "Frequent loose stools"),
        ("Stomach Pain", "Abdominal discomfort or pain"),
        ("Headache", "Pain or pressure in the head"),
        ("Chest Pain", "Pain or discomfort in the chest"),
        ("Dizziness", "Feeling light-headed or unsteady"),
        ("Skin Rash", "Redness, irritation or rash on the skin"),
        ("Runny Nose", "Nasal discharge or congestion"),
        ("Palpitations", "Feeling of rapid or irregular heartbeat"),
    ]

    symptom_objects = {}

    for name, description in symptom_data:
        symptom, _ = Symptom.objects.get_or_create(
            name=name,
            defaults={
                "description": description,
            },
        )
        symptom_objects[name] = symptom

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------

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
        "Patient@123",
        "Priya",
        "Mehta",
        Account.ACCOUNT_PATIENT,
    )

    patient3 = get_or_create_user(
        "patient3@virtualclinic.com",
        "Patient@123",
        "Rahul",
        "Verma",
        Account.ACCOUNT_PATIENT,
    )

    patient4 = get_or_create_user(
        "patient4@virtualclinic.com",
        "Patient@123",
        "Isha",
        "Nair",
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

    doctor4 = get_or_create_user(
        "doctor4@virtualclinic.com",
        "Doctor@123",
        "Neha",
        "Malhotra",
        Account.ACCOUNT_DOCTOR,
        dermatology,
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

    # ---------------------------------------------------------
    # PATIENT PROFILES
    # ---------------------------------------------------------

    patient_profiles = [
        (
            patient1,
            "M",
            "1999-05-14",
            "9876500001",
            "Dust",
            hospital1,
            doctor1,
            general_medicine,
            {
                "bloodType": "O+",
                "allergy": "Dust",
                "asthma": True,
                "comments": "Occasional seasonal breathing discomfort.",
            },
        ),
        (
            patient2,
            "F",
            "2001-11-02",
            "9876500002",
            "None",
            hospital2,
            doctor2,
            general_medicine,
            {
                "bloodType": "A+",
                "allergy": "None",
                "diabetes": False,
                "comments": "No major chronic conditions reported.",
            },
        ),
        (
            patient3,
            "M",
            "1998-08-21",
            "9876500003",
            "Penicillin",
            hospital3,
            doctor3,
            pulmonology,
            {
                "bloodType": "B+",
                "allergy": "Penicillin",
                "asthma": True,
                "comments": "History of respiratory sensitivity.",
            },
        ),
        (
            patient4,
            "F",
            "2000-03-09",
            "9876500004",
            "None",
            hospital1,
            doctor4,
            dermatology,
            {
                "bloodType": "AB+",
                "allergy": "None",
                "comments": "No major medical history.",
            },
        ),
    ]

    for (
        account,
        sex,
        birthday,
        phone,
        allergies,
        preferred_hospital,
        primary_doctor,
        speciality,
        medical_data,
    ) in patient_profiles:

        profile = account.profile
        profile.sex = sex
        profile.birthday = birthday
        profile.phone = phone
        profile.allergies = allergies
        profile.prefHospital = preferred_hospital
        profile.primaryCareDoctor = primary_doctor
        profile.speciality = speciality
        profile.save()

        MedicalInfo.objects.update_or_create(
            account=account,
            defaults={
                "bloodType": medical_data.get(
                    "bloodType",
                    "O+",
                ),
                "allergy": medical_data.get(
                    "allergy",
                    "",
                ),
                "alzheimer": medical_data.get(
                    "alzheimer",
                    False,
                ),
                "asthma": medical_data.get(
                    "asthma",
                    False,
                ),
                "diabetes": medical_data.get(
                    "diabetes",
                    False,
                ),
                "stroke": medical_data.get(
                    "stroke",
                    False,
                ),
                "comments": medical_data.get(
                    "comments",
                    "",
                ),
            },
        )

    # ---------------------------------------------------------
    # APPOINTMENTS
    # ---------------------------------------------------------

    now = timezone.now()

    appointment_data = [
        (
            doctor1,
            patient1,
            "Fever, cough and fatigue for two days",
            "Fever",
            hospital1,
            "Online",
            now + timedelta(days=1, hours=2),
        ),
        (
            doctor2,
            patient2,
            "Routine cardiovascular consultation",
            "Dizziness",
            hospital2,
            "Offline",
            now + timedelta(days=2),
        ),
        (
            doctor3,
            patient3,
            "Persistent cough and breathing discomfort",
            "Breathing Difficulty",
            hospital3,
            "Online",
            now + timedelta(days=3),
        ),
        (
            doctor4,
            patient4,
            "Skin irritation and recurring rash",
            "Skin Rash",
            hospital1,
            "Offline",
            now + timedelta(days=4),
        ),
        (
            doctor1,
            patient2,
            "Headache and mild fever",
            "Headache",
            hospital1,
            "Online",
            now + timedelta(days=5),
        ),
        (
            doctor3,
            patient1,
            "Follow-up respiratory consultation",
            "Cough",
            hospital3,
            "Online",
            now + timedelta(days=6),
        ),
        (
            doctor2,
            patient3,
            "Palpitations and dizziness",
            "Palpitations",
            hospital2,
            "Offline",
            now + timedelta(days=7),
        ),
        (
            doctor4,
            patient4,
            "Follow-up dermatology appointment",
            "Skin Rash",
            hospital1,
            "Offline",
            now + timedelta(days=9),
        ),
    ]

    created_appointments = []

    for (
        doctor,
        patient,
        description,
        symptom_name,
        hospital,
        appointment_type,
        start_time,
    ) in appointment_data:

        appointment, _ = Appointment.objects.get_or_create(
            doctor=doctor,
            patient=patient,
            description=description,
            startTime=start_time,
            defaults={
                "symptom": symptom_objects[symptom_name],
                "status": "Active",
                "hospital": hospital,
                "appointment_type": appointment_type,
                "endTime": start_time + timedelta(minutes=30),
            },
        )

        created_appointments.append(appointment)

    # ---------------------------------------------------------
    # PRESCRIPTIONS
    # ---------------------------------------------------------

    prescription_data = [
        (
            patient1,
            doctor1,
            "Paracetamol",
            "500 mg",
            "Take after food when required",
            2,
        ),
        (
            patient2,
            doctor2,
            "Vitamin D",
            "1000 IU",
            "Take once daily",
            1,
        ),
        (
            patient3,
            doctor3,
            "Salbutamol",
            "2 mg",
            "Use only as directed by doctor",
            1,
        ),
        (
            patient4,
            doctor4,
            "Cetirizine",
            "10 mg",
            "Take once daily if required",
            1,
        ),
    ]

    for (
        patient,
        doctor,
        medication,
        strength,
        instruction,
        refill,
    ) in prescription_data:

        Prescription.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            medication=medication,
            date=now.date(),
            defaults={
                "strength": strength,
                "instruction": instruction,
                "refill": refill,
                "active": True,
            },
        )

    # ---------------------------------------------------------
    # MEDICAL TESTS
    # ---------------------------------------------------------

    medical_tests = [
        (
            "Complete Blood Count",
            patient1,
            doctor1,
            hospital1,
            "Routine blood investigation for fever symptoms.",
        ),
        (
            "Chest X-Ray",
            patient3,
            doctor3,
            hospital3,
            "Respiratory investigation for persistent cough.",
        ),
        (
            "ECG",
            patient2,
            doctor2,
            hospital2,
            "Cardiac rhythm evaluation.",
        ),
        (
            "Allergy Panel",
            patient4,
            doctor4,
            hospital1,
            "Investigation related to recurring skin irritation.",
        ),
    ]

    for (
        name,
        patient,
        doctor,
        hospital,
        description,
    ) in medical_tests:

        MedicalTest.objects.get_or_create(
            name=name,
            patient=patient,
            doctor=doctor,
            date=now.date(),
            defaults={
                "hospital": hospital,
                "description": description,
                "private": True,
                "completed": False,
            },
        )

    print("")
    print("==========================================")
    print(" Virtual Clinic demo data ready")
    print("==========================================")
    print("")
    print("PATIENTS")
    print("patient1@virtualclinic.com / Patient@123")
    print("patient2@virtualclinic.com / Patient@123")
    print("patient3@virtualclinic.com / Patient@123")
    print("patient4@virtualclinic.com / Patient@123")
    print("")
    print("DOCTORS")
    print("doctor1@virtualclinic.com / Doctor@123")
    print("doctor2@virtualclinic.com / Doctor@123")
    print("doctor3@virtualclinic.com / Doctor@123")
    print("doctor4@virtualclinic.com / Doctor@123")
    print("")
    print("ADMIN")
    print("admin@virtualclinic.com / Admin@123")
    print("")
    print("LAB")
    print("lab@virtualclinic.com / Lab@123")
    print("")
    print("CHEMIST")
    print("chemist@virtualclinic.com / Chemist@123")
    print("")
    print("Appointments:", len(created_appointments))
    print("==========================================")


if __name__ == "__main__":
    seed()