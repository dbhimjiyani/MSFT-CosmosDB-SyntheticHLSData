"""
Synthetic patient demographics generator.

Each patient document follows the FHIR-inspired structure and includes
a Presidio-synthesized free-text clinical summary.
"""

import uuid
from datetime import date, timedelta
from typing import List
import random

from faker import Faker

from src.synthesizer import PresidioSynthesizer


# Clinical note templates; PII placeholders are replaced by Presidio + Faker
_CLINICAL_SUMMARY_TEMPLATES = [
    (
        "Patient {name} is a {age}-year-old {gender} presenting for a routine wellness "
        "exam. DOB {dob}. MRN {mrn}. Contact: {phone}, {email}. "
        "Patient reports no acute complaints. Medical history is significant for "
        "{condition}. Current medications reviewed and reconciled."
    ),
    (
        "{name}, {age} y/o {gender}, DOB {dob}, SSN {ssn}. Scheduled follow-up visit. "
        "Lives at {address}. Phone {phone}. Primary insurance: {insurance}. "
        "Established patient with history of {condition}. No new concerns today."
    ),
    (
        "Reason for visit: Annual physical. Patient: {name}, DOB {dob}, MRN {mrn}. "
        "{age}-year-old {gender}. Emergency contact: {ec_name} at {ec_phone}. "
        "Medical history: {condition}. Allergies: NKDA. Vitals stable."
    ),
]

_CONDITIONS = [
    "hypertension",
    "type 2 diabetes",
    "hyperlipidemia",
    "asthma",
    "hypothyroidism",
    "gastroesophageal reflux disease",
    "osteoarthritis",
    "anxiety disorder",
    "chronic lower back pain",
    "mild depression",
]

_INSURANCE_PLANS = [
    "Blue Cross Blue Shield",
    "Aetna",
    "United Healthcare",
    "Cigna",
    "Humana",
    "Medicare",
    "Medicaid",
    "Kaiser Permanente",
    "Anthem",
    "Molina Healthcare",
]

_BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


def _random_dob(fake: Faker, min_age: int = 18, max_age: int = 85) -> date:
    today = date.today()
    days = random.randint(min_age * 365, max_age * 365)
    return today - timedelta(days=days)


class PatientGenerator:
    """Generates synthetic patient demographic records."""

    def __init__(self, locale: str = "en_US", spacy_model: str = "en_core_web_sm"):
        self.fake = Faker(locale)
        self.synth = PresidioSynthesizer(locale=locale, spacy_model=spacy_model)

    def generate(self, count: int = 10) -> List[dict]:
        """Return *count* synthetic patient documents."""
        return [self._generate_one() for _ in range(count)]

    def _generate_one(self) -> dict:
        fake = self.fake
        patient_id = str(uuid.uuid4())
        gender = random.choice(["male", "female"])
        name = fake.name_male() if gender == "male" else fake.name_female()
        dob = _random_dob(fake)
        age = (date.today() - dob).days // 365
        mrn = f"MRN{fake.numerify('########')}"
        ssn = fake.ssn()
        phone = fake.phone_number()
        email = fake.email()
        address = {
            "line": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postalCode": fake.zipcode(),
            "country": "US",
        }
        insurance = random.choice(_INSURANCE_PLANS)
        insurance_id = f"INS-{fake.numerify('##########')}"
        condition = random.choice(_CONDITIONS)
        ec_name = fake.name()
        ec_phone = fake.phone_number()

        template = random.choice(_CLINICAL_SUMMARY_TEMPLATES)
        raw_note = template.format(
            name=name,
            age=age,
            gender=gender,
            dob=dob.isoformat(),
            mrn=mrn,
            ssn=ssn,
            phone=phone,
            email=email,
            address=f"{address['line']}, {address['city']}, {address['state']}",
            insurance=insurance,
            condition=condition,
            ec_name=ec_name,
            ec_phone=ec_phone,
        )
        clinical_summary = self.synth.synthesize(raw_note)

        return {
            "id": patient_id,
            "patientId": patient_id,
            "resourceType": "Patient",
            "name": name,
            "dateOfBirth": dob.isoformat(),
            "age": age,
            "gender": gender,
            "mrn": mrn,
            "ssn": ssn,
            "bloodType": random.choice(_BLOOD_TYPES),
            "phone": phone,
            "email": email,
            "address": address,
            "insurancePlan": insurance,
            "insuranceId": insurance_id,
            "emergencyContact": {
                "name": ec_name,
                "phone": ec_phone,
                "relationship": random.choice(
                    ["spouse", "parent", "sibling", "child", "friend"]
                ),
            },
            "clinicalSummary": clinical_summary,
        }
