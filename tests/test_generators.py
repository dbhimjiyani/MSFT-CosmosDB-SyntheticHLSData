"""
Unit tests for diagnosis, medication, and lab result generators.

These generators do not require Presidio / spaCy, so they run quickly
without any external model download.
"""

import uuid
import pytest

from src.generators.diagnosis import DiagnosisGenerator
from src.generators.medication import MedicationGenerator
from src.generators.lab_result import LabResultGenerator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_patient(patient_id: str = None) -> dict:
    pid = patient_id or str(uuid.uuid4())
    return {
        "id": pid,
        "patientId": pid,
        "name": "Test Patient",
        "dateOfBirth": "1980-01-01",
        "age": 44,
        "gender": "female",
    }


def _make_encounter(patient: dict, encounter_id: str = None) -> dict:
    eid = encounter_id or str(uuid.uuid4())
    return {
        "id": eid,
        "encounterId": eid,
        "patientId": patient["patientId"],
        "type": "outpatient",
        "date": "2024-06-15",
    }


# ---------------------------------------------------------------------------
# DiagnosisGenerator
# ---------------------------------------------------------------------------

class TestDiagnosisGenerator:
    def setup_method(self):
        self.gen = DiagnosisGenerator()
        self.patient = _make_patient()
        self.encounter = _make_encounter(self.patient)

    def test_generates_for_each_encounter(self):
        encounters = [_make_encounter(self.patient) for _ in range(5)]
        diagnoses = self.gen.generate(encounters, max_per_encounter=2)
        assert len(diagnoses) >= 5  # at least 1 per encounter

    def test_diagnosis_fields_present(self):
        diagnoses = self.gen.generate([self.encounter], max_per_encounter=1)
        assert len(diagnoses) >= 1
        doc = diagnoses[0]
        required = {
            "id", "diagnosisId", "patientId", "encounterId",
            "resourceType", "code", "description", "category",
            "codingSystem", "status", "severity", "onsetDate",
        }
        assert required.issubset(doc.keys())

    def test_resource_type_is_condition(self):
        diagnoses = self.gen.generate([self.encounter], max_per_encounter=1)
        for d in diagnoses:
            assert d["resourceType"] == "Condition"

    def test_patient_id_propagated(self):
        pid = str(uuid.uuid4())
        patient = _make_patient(pid)
        encounter = _make_encounter(patient)
        diagnoses = self.gen.generate([encounter], max_per_encounter=3)
        for d in diagnoses:
            assert d["patientId"] == pid

    def test_encounter_id_propagated(self):
        encounter = _make_encounter(self.patient)
        diagnoses = self.gen.generate([encounter], max_per_encounter=3)
        for d in diagnoses:
            assert d["encounterId"] == encounter["encounterId"]

    def test_icd10_coding_system(self):
        diagnoses = self.gen.generate([self.encounter], max_per_encounter=3)
        for d in diagnoses:
            assert d["codingSystem"] == "ICD-10-CM"

    def test_unique_ids(self):
        encounters = [_make_encounter(self.patient) for _ in range(10)]
        diagnoses = self.gen.generate(encounters, max_per_encounter=3)
        ids = [d["id"] for d in diagnoses]
        assert len(ids) == len(set(ids))

    def test_empty_encounters(self):
        diagnoses = self.gen.generate([], max_per_encounter=3)
        assert diagnoses == []


# ---------------------------------------------------------------------------
# MedicationGenerator
# ---------------------------------------------------------------------------

class TestMedicationGenerator:
    def setup_method(self):
        self.gen = MedicationGenerator()
        self.patient = _make_patient()
        self.encounter = _make_encounter(self.patient)

    def test_generates_documents(self):
        medications = self.gen.generate([self.encounter], max_per_encounter=3)
        assert isinstance(medications, list)

    def test_medication_fields_present(self):
        # Keep generating until we get at least one medication
        medications = []
        for _ in range(20):
            medications = self.gen.generate([self.encounter], max_per_encounter=3)
            if medications:
                break
        if not medications:
            pytest.skip("Random generation produced no medications; retry.")
        doc = medications[0]
        required = {
            "id", "medicationId", "patientId", "encounterId",
            "resourceType", "name", "dose", "route", "frequency",
            "indication", "startDate", "endDate", "prescriber", "status",
        }
        assert required.issubset(doc.keys())

    def test_resource_type_is_medication_request(self):
        medications = []
        for _ in range(20):
            medications = self.gen.generate([self.encounter], max_per_encounter=3)
            if medications:
                break
        for m in medications:
            assert m["resourceType"] == "MedicationRequest"

    def test_patient_id_propagated(self):
        pid = str(uuid.uuid4())
        patient = _make_patient(pid)
        encounter = _make_encounter(patient)
        for _ in range(20):
            meds = self.gen.generate([encounter], max_per_encounter=3)
            if meds:
                for m in meds:
                    assert m["patientId"] == pid
                break

    def test_unique_ids(self):
        encounters = [_make_encounter(self.patient) for _ in range(10)]
        medications = self.gen.generate(encounters, max_per_encounter=3)
        ids = [m["id"] for m in medications]
        assert len(ids) == len(set(ids))

    def test_empty_encounters(self):
        medications = self.gen.generate([], max_per_encounter=3)
        assert medications == []


# ---------------------------------------------------------------------------
# LabResultGenerator
# ---------------------------------------------------------------------------

class TestLabResultGenerator:
    def setup_method(self):
        self.gen = LabResultGenerator()
        self.patient = _make_patient()
        self.encounter = _make_encounter(self.patient)

    def test_generates_documents(self):
        labs = self.gen.generate([self.encounter], max_per_encounter=5)
        assert isinstance(labs, list)

    def test_lab_fields_present(self):
        labs = []
        for _ in range(20):
            labs = self.gen.generate([self.encounter], max_per_encounter=5)
            if labs:
                break
        if not labs:
            pytest.skip("Random generation produced no labs; retry.")
        doc = labs[0]
        required = {
            "id", "labId", "patientId", "encounterId",
            "resourceType", "testName", "panel", "value",
            "unit", "referenceRange", "interpretation", "status", "date",
        }
        assert required.issubset(doc.keys())

    def test_resource_type_is_observation(self):
        labs = []
        for _ in range(20):
            labs = self.gen.generate([self.encounter], max_per_encounter=5)
            if labs:
                break
        for lab in labs:
            assert lab["resourceType"] == "Observation"

    def test_interpretation_values(self):
        valid_interpretations = {"Normal", "Low", "High", "Critical Low", "Critical High"}
        labs = []
        for _ in range(20):
            labs = self.gen.generate([self.encounter], max_per_encounter=5)
            if labs:
                break
        for lab in labs:
            assert lab["interpretation"] in valid_interpretations

    def test_patient_id_propagated(self):
        pid = str(uuid.uuid4())
        patient = _make_patient(pid)
        encounter = _make_encounter(patient)
        for _ in range(20):
            labs = self.gen.generate([encounter], max_per_encounter=5)
            if labs:
                for lab in labs:
                    assert lab["patientId"] == pid
                break

    def test_unique_ids(self):
        encounters = [_make_encounter(self.patient) for _ in range(10)]
        labs = self.gen.generate(encounters, max_per_encounter=5)
        ids = [lab["id"] for lab in labs]
        assert len(ids) == len(set(ids))

    def test_empty_encounters(self):
        labs = self.gen.generate([], max_per_encounter=5)
        assert labs == []
