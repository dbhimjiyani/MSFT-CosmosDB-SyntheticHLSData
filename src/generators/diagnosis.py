"""
Synthetic diagnosis (ICD-10) generator.

Each encounter may have one or more diagnoses drawn from a curated list of
common ICD-10 codes representative of outpatient and inpatient settings.
"""

import uuid
from datetime import date, timedelta
from typing import List
import random


# (ICD-10 code, description, clinical category)
_ICD10_CODES = [
    ("Z00.00", "General adult medical examination without abnormal findings", "Preventive"),
    ("I10", "Essential (primary) hypertension", "Cardiovascular"),
    ("E11.9", "Type 2 diabetes mellitus without complications", "Endocrine"),
    ("E78.5", "Hyperlipidemia, unspecified", "Endocrine"),
    ("J18.9", "Pneumonia, unspecified organism", "Respiratory"),
    ("J06.9", "Acute upper respiratory infection, unspecified", "Respiratory"),
    ("J45.20", "Mild intermittent asthma, uncomplicated", "Respiratory"),
    ("M54.5", "Low back pain", "Musculoskeletal"),
    ("M17.11", "Primary osteoarthritis, right knee", "Musculoskeletal"),
    ("K21.0", "Gastro-esophageal reflux disease with esophagitis", "Gastrointestinal"),
    ("K59.00", "Constipation, unspecified", "Gastrointestinal"),
    ("F32.1", "Major depressive disorder, single episode, moderate", "Mental Health"),
    ("F41.1", "Generalized anxiety disorder", "Mental Health"),
    ("F10.10", "Alcohol abuse, uncomplicated", "Mental Health"),
    ("E03.9", "Hypothyroidism, unspecified", "Endocrine"),
    ("N18.3", "Chronic kidney disease, stage 3 (moderate)", "Renal"),
    ("I25.10", "Atherosclerotic heart disease of native coronary artery", "Cardiovascular"),
    ("I50.9", "Heart failure, unspecified", "Cardiovascular"),
    ("D50.9", "Iron deficiency anemia, unspecified", "Hematologic"),
    ("R05.9", "Cough, unspecified", "Respiratory"),
    ("R51.9", "Headache, unspecified", "Neurological"),
    ("G43.909", "Migraine, unspecified, not intractable, without status migrainosus", "Neurological"),
    ("L30.9", "Dermatitis, unspecified", "Dermatology"),
    ("B35.1", "Tinea unguium", "Dermatology"),
    ("Z87.891", "Personal history of nicotine dependence", "Preventive"),
]

_DIAGNOSIS_STATUSES = ["active", "resolved", "chronic", "in-remission"]
_SEVERITIES = ["mild", "moderate", "severe"]


def _random_onset_date() -> date:
    today = date.today()
    days_back = random.randint(30, 5 * 365)
    return today - timedelta(days=days_back)


class DiagnosisGenerator:
    """Generates synthetic diagnosis records linked to encounters."""

    def generate(self, encounters: List[dict], max_per_encounter: int = 3) -> List[dict]:
        """Return diagnosis documents for each encounter in *encounters*."""
        diagnoses = []
        for encounter in encounters:
            count = random.randint(1, max_per_encounter)
            selected = random.sample(_ICD10_CODES, min(count, len(_ICD10_CODES)))
            for code, description, category in selected:
                diagnoses.append(
                    self._generate_one(encounter, code, description, category)
                )
        return diagnoses

    def _generate_one(
        self,
        encounter: dict,
        code: str,
        description: str,
        category: str,
    ) -> dict:
        diagnosis_id = str(uuid.uuid4())
        return {
            "id": diagnosis_id,
            "diagnosisId": diagnosis_id,
            "patientId": encounter["patientId"],
            "encounterId": encounter["encounterId"],
            "resourceType": "Condition",
            "code": code,
            "description": description,
            "category": category,
            "codingSystem": "ICD-10-CM",
            "status": random.choice(_DIAGNOSIS_STATUSES),
            "severity": random.choice(_SEVERITIES),
            "onsetDate": _random_onset_date().isoformat(),
            "encounterDate": encounter["date"],
        }
