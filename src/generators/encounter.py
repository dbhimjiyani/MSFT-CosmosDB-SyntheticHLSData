"""
Synthetic clinical encounter generator.

Encounters represent patient visits (outpatient, emergency, inpatient) and
include a Presidio-synthesized physician note.
"""

import uuid
from datetime import date, timedelta
from typing import List
import random

from faker import Faker

from src.synthesizer import PresidioSynthesizer


_ENCOUNTER_TYPES = [
    "outpatient",
    "emergency",
    "inpatient",
    "telehealth",
    "preventive",
]

_CHIEF_COMPLAINTS = [
    "chest pain",
    "shortness of breath",
    "abdominal pain",
    "headache",
    "fever and chills",
    "back pain",
    "fatigue",
    "dizziness",
    "cough",
    "routine follow-up",
    "medication refill",
    "annual wellness visit",
    "knee pain",
    "rash",
    "nausea and vomiting",
]

_FACILITIES = [
    "City General Hospital",
    "Riverside Medical Center",
    "Lakeside Clinic",
    "Northside Family Practice",
    "Community Health Center",
    "St. Mary's Hospital",
    "Valley Urgent Care",
    "Downtown Medical Associates",
    "Suburban Primary Care",
    "Mountain View Hospital",
]

_PHYSICIAN_NOTE_TEMPLATES = [
    (
        "Seen by Dr. {provider} at {facility} on {date}. Chief complaint: {complaint}. "
        "Patient {patient_name} is a {age}-year-old presenting today. Vitals: BP "
        "{bp}, HR {hr} bpm, Temp {temp}°F, SpO2 {spo2}%. "
        "Assessment and plan discussed with patient. Follow-up in {followup} weeks."
    ),
    (
        "Visit note for {patient_name}, DOB {dob}. Provider: Dr. {provider}. "
        "Location: {facility}. Date: {date}. Type: {encounter_type}. "
        "Complaint: {complaint}. Vitals stable. BP {bp}, HR {hr}. "
        "Plan: continue current management and return to clinic as needed."
    ),
    (
        "Encounter at {facility} on {date}. Attending: Dr. {provider}. "
        "Patient: {patient_name}. Chief complaint: {complaint}. "
        "VS: T {temp}°F, P {hr}, BP {bp}, RR {rr}, SpO2 {spo2}%. "
        "Patient counseled on treatment plan. Next appointment scheduled."
    ),
]


def _random_date_in_past(years: int = 3) -> date:
    today = date.today()
    days_back = random.randint(0, years * 365)
    return today - timedelta(days=days_back)


class EncounterGenerator:
    """Generates synthetic clinical encounter records for a list of patients."""

    def __init__(self, locale: str = "en_US", spacy_model: str = "en_core_web_sm"):
        self.fake = Faker(locale)
        self.synth = PresidioSynthesizer(locale=locale, spacy_model=spacy_model)

    def generate(
        self, patients: List[dict], encounters_per_patient: int = 3
    ) -> List[dict]:
        """Return encounter documents for every patient in *patients*."""
        encounters = []
        for patient in patients:
            for _ in range(encounters_per_patient):
                encounters.append(self._generate_one(patient))
        return encounters

    def _generate_one(self, patient: dict) -> dict:
        fake = self.fake
        encounter_id = str(uuid.uuid4())
        encounter_type = random.choice(_ENCOUNTER_TYPES)
        encounter_date = _random_date_in_past()
        provider = fake.name()
        facility = random.choice(_FACILITIES)
        complaint = random.choice(_CHIEF_COMPLAINTS)

        bp = f"{random.randint(100, 160)}/{random.randint(60, 100)}"
        hr = random.randint(55, 110)
        temp = round(random.uniform(97.0, 102.5), 1)
        rr = random.randint(12, 22)
        spo2 = random.randint(93, 100)
        followup = random.choice([1, 2, 4, 6, 8, 12])

        template = random.choice(_PHYSICIAN_NOTE_TEMPLATES)
        raw_note = template.format(
            provider=provider,
            facility=facility,
            date=encounter_date.isoformat(),
            complaint=complaint,
            patient_name=patient.get("name", "the patient"),
            age=patient.get("age", ""),
            dob=patient.get("dateOfBirth", ""),
            encounter_type=encounter_type,
            bp=bp,
            hr=hr,
            temp=temp,
            rr=rr,
            spo2=spo2,
            followup=followup,
        )
        note = self.synth.synthesize(raw_note)

        return {
            "id": encounter_id,
            "encounterId": encounter_id,
            "patientId": patient["patientId"],
            "resourceType": "Encounter",
            "type": encounter_type,
            "date": encounter_date.isoformat(),
            "provider": provider,
            "facility": facility,
            "chiefComplaint": complaint,
            "vitals": {
                "bloodPressure": bp,
                "heartRate": hr,
                "temperature": temp,
                "respiratoryRate": rr,
                "oxygenSaturation": spo2,
            },
            "note": note,
        }
