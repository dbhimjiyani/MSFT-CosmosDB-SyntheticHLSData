"""
Synthetic medication / prescription generator.

Generates MedicationRequest-style documents linked to patient encounters,
drawn from a curated list of commonly prescribed drugs.
"""

import uuid
from datetime import date, timedelta
from typing import List
import random

from faker import Faker


# (name, dose, route, frequency, indication)
_MEDICATIONS = [
    ("Metformin", "500 mg", "oral", "twice daily", "type 2 diabetes"),
    ("Metformin", "1000 mg", "oral", "twice daily", "type 2 diabetes"),
    ("Lisinopril", "10 mg", "oral", "once daily", "hypertension"),
    ("Lisinopril", "20 mg", "oral", "once daily", "hypertension"),
    ("Amlodipine", "5 mg", "oral", "once daily", "hypertension"),
    ("Atorvastatin", "40 mg", "oral", "once daily", "hyperlipidemia"),
    ("Rosuvastatin", "20 mg", "oral", "once daily", "hyperlipidemia"),
    ("Omeprazole", "20 mg", "oral", "once daily", "GERD"),
    ("Pantoprazole", "40 mg", "oral", "once daily", "GERD"),
    ("Sertraline", "50 mg", "oral", "once daily", "depression/anxiety"),
    ("Escitalopram", "10 mg", "oral", "once daily", "depression/anxiety"),
    ("Levothyroxine", "50 mcg", "oral", "once daily", "hypothyroidism"),
    ("Levothyroxine", "100 mcg", "oral", "once daily", "hypothyroidism"),
    ("Albuterol inhaler", "90 mcg/actuation", "inhalation", "as needed", "asthma"),
    ("Fluticasone inhaler", "44 mcg/actuation", "inhalation", "twice daily", "asthma"),
    ("Ibuprofen", "400 mg", "oral", "every 6 hours as needed", "pain/inflammation"),
    ("Naproxen", "500 mg", "oral", "twice daily as needed", "pain/inflammation"),
    ("Acetaminophen", "500 mg", "oral", "every 6 hours as needed", "pain/fever"),
    ("Amoxicillin", "500 mg", "oral", "three times daily", "bacterial infection"),
    ("Azithromycin", "500 mg", "oral", "once daily", "bacterial infection"),
    ("Metoprolol succinate", "25 mg", "oral", "once daily", "heart failure/hypertension"),
    ("Furosemide", "40 mg", "oral", "once daily", "heart failure/edema"),
    ("Warfarin", "5 mg", "oral", "once daily", "anticoagulation"),
    ("Aspirin", "81 mg", "oral", "once daily", "cardiovascular prevention"),
    ("Gabapentin", "300 mg", "oral", "three times daily", "neuropathic pain"),
]

_MED_STATUSES = ["active", "completed", "stopped", "on-hold"]
_SUPPLY_DAYS = [30, 60, 90]


def _random_start_date() -> date:
    today = date.today()
    days_back = random.randint(30, 3 * 365)
    return today - timedelta(days=days_back)


class MedicationGenerator:
    """Generates synthetic medication request records linked to encounters."""

    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)

    def generate(self, encounters: List[dict], max_per_encounter: int = 3) -> List[dict]:
        """Return medication documents for each encounter in *encounters*."""
        medications = []
        for encounter in encounters:
            count = random.randint(0, max_per_encounter)
            selected = random.sample(_MEDICATIONS, min(count, len(_MEDICATIONS)))
            for med in selected:
                medications.append(self._generate_one(encounter, med))
        return medications

    def _generate_one(self, encounter: dict, med_tuple: tuple) -> dict:
        fake = self.fake
        name, dose, route, frequency, indication = med_tuple
        med_id = str(uuid.uuid4())
        start_date = _random_start_date()
        supply_days = random.choice(_SUPPLY_DAYS)
        end_date = start_date + timedelta(days=supply_days)
        status = random.choice(_MED_STATUSES)

        return {
            "id": med_id,
            "medicationId": med_id,
            "patientId": encounter["patientId"],
            "encounterId": encounter["encounterId"],
            "resourceType": "MedicationRequest",
            "name": name,
            "dose": dose,
            "route": route,
            "frequency": frequency,
            "indication": indication,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "supplyDays": supply_days,
            "refillsAllowed": random.randint(0, 5),
            "prescriber": fake.name(),
            "status": status,
            "encounterDate": encounter["date"],
        }
