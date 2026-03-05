"""
Synthetic laboratory result generator.

Generates Observation-style lab result documents linked to patient encounters,
with clinically plausible numeric values and reference ranges.
"""

import uuid
from typing import List
import random

from faker import Faker


# (test_name, panel, unit, (low_normal, high_normal), (low_value, high_value))
_LAB_TESTS = [
    # CBC
    ("Hemoglobin", "CBC", "g/dL", (12.0, 17.5), (9.0, 19.0)),
    ("Hematocrit", "CBC", "%", (36.0, 50.0), (28.0, 55.0)),
    ("White Blood Cell Count", "CBC", "K/uL", (4.5, 11.0), (2.0, 18.0)),
    ("Platelet Count", "CBC", "K/uL", (150.0, 400.0), (50.0, 600.0)),
    ("Mean Corpuscular Volume", "CBC", "fL", (80.0, 100.0), (60.0, 120.0)),
    # CMP
    ("Sodium", "CMP", "mEq/L", (136.0, 145.0), (125.0, 155.0)),
    ("Potassium", "CMP", "mEq/L", (3.5, 5.0), (2.5, 6.5)),
    ("Creatinine", "CMP", "mg/dL", (0.6, 1.2), (0.4, 4.0)),
    ("Blood Urea Nitrogen", "CMP", "mg/dL", (7.0, 20.0), (5.0, 50.0)),
    ("Glucose", "CMP", "mg/dL", (70.0, 100.0), (50.0, 400.0)),
    ("Alanine Aminotransferase", "CMP", "U/L", (7.0, 56.0), (5.0, 200.0)),
    ("Aspartate Aminotransferase", "CMP", "U/L", (10.0, 40.0), (8.0, 300.0)),
    ("Alkaline Phosphatase", "CMP", "U/L", (44.0, 147.0), (30.0, 400.0)),
    ("Total Bilirubin", "CMP", "mg/dL", (0.1, 1.2), (0.1, 5.0)),
    # Lipid Panel
    ("Total Cholesterol", "Lipid Panel", "mg/dL", (0.0, 200.0), (100.0, 350.0)),
    ("LDL Cholesterol", "Lipid Panel", "mg/dL", (0.0, 100.0), (40.0, 250.0)),
    ("HDL Cholesterol", "Lipid Panel", "mg/dL", (40.0, 60.0), (20.0, 100.0)),
    ("Triglycerides", "Lipid Panel", "mg/dL", (0.0, 150.0), (50.0, 500.0)),
    # Diabetes
    ("Hemoglobin A1c", "Diabetes Panel", "%", (4.0, 5.6), (4.0, 14.0)),
    ("Fasting Glucose", "Diabetes Panel", "mg/dL", (70.0, 100.0), (50.0, 400.0)),
    # Thyroid
    ("TSH", "Thyroid Panel", "mIU/L", (0.4, 4.0), (0.01, 20.0)),
    ("Free T4", "Thyroid Panel", "ng/dL", (0.8, 1.8), (0.3, 3.0)),
    # Urinalysis
    ("Urine pH", "Urinalysis", "", (4.5, 8.0), (4.5, 9.0)),
    ("Urine Specific Gravity", "Urinalysis", "", (1.005, 1.030), (1.001, 1.035)),
]

_INTERPRETATIONS = {
    "normal": "Normal",
    "low": "Low",
    "high": "High",
    "critical_low": "Critical Low",
    "critical_high": "Critical High",
}

_LAB_STATUSES = ["final", "preliminary", "corrected"]


def _generate_value_and_interpretation(
    low_normal: float,
    high_normal: float,
    low_value: float,
    high_value: float,
) -> tuple:
    value = round(random.uniform(low_value, high_value), 2)
    if value < low_normal * 0.8:
        interp = "Critical Low"
    elif value < low_normal:
        interp = "Low"
    elif value > high_normal * 1.2:
        interp = "Critical High"
    elif value > high_normal:
        interp = "High"
    else:
        interp = "Normal"
    return value, interp


class LabResultGenerator:
    """Generates synthetic laboratory result records linked to encounters."""

    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)

    def generate(self, encounters: List[dict], max_per_encounter: int = 5) -> List[dict]:
        """Return lab result documents for each encounter in *encounters*."""
        lab_results = []
        for encounter in encounters:
            count = random.randint(0, max_per_encounter)
            selected = random.sample(_LAB_TESTS, min(count, len(_LAB_TESTS)))
            for lab in selected:
                lab_results.append(self._generate_one(encounter, lab))
        return lab_results

    def _generate_one(self, encounter: dict, lab_tuple: tuple) -> dict:
        test_name, panel, unit, normal_range, value_range = lab_tuple
        lab_id = str(uuid.uuid4())
        low_normal, high_normal = normal_range
        low_value, high_value = value_range
        value, interpretation = _generate_value_and_interpretation(
            low_normal, high_normal, low_value, high_value
        )
        ref_range = (
            f"{low_normal} - {high_normal} {unit}".strip()
            if unit
            else f"{low_normal} - {high_normal}"
        )

        return {
            "id": lab_id,
            "labId": lab_id,
            "patientId": encounter["patientId"],
            "encounterId": encounter["encounterId"],
            "resourceType": "Observation",
            "testName": test_name,
            "panel": panel,
            "value": value,
            "unit": unit,
            "referenceRange": ref_range,
            "interpretation": interpretation,
            "status": random.choice(_LAB_STATUSES),
            "date": encounter["date"],
            "performingLab": f"{self.fake.city()} Reference Laboratory",
        }
