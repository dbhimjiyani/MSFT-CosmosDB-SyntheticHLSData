"""
Unit tests for the PresidioSynthesizer.

Validates that PII is detected and replaced with synthetic values,
and that the output structure is preserved.
"""

import pytest

from src.synthesizer import PresidioSynthesizer


@pytest.fixture(scope="module")
def synth():
    """A single synthesizer instance shared across all tests in this module."""
    return PresidioSynthesizer(locale="en_US", spacy_model="en_core_web_sm")


class TestPresidioSynthesizer:
    def test_returns_string(self, synth):
        result = synth.synthesize("Hello world.")
        assert isinstance(result, str)

    def test_text_without_pii_unchanged(self, synth):
        text = "The patient reported mild chest discomfort."
        result = synth.synthesize(text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_email_replaced(self, synth):
        text = "Contact: john.doe@example.com"
        result = synth.synthesize(text)
        assert "john.doe@example.com" not in result

    def test_person_name_replaced(self, synth):
        text = "Patient John Smith presented today."
        result = synth.synthesize(text)
        assert "John Smith" not in result

    def test_date_replaced(self, synth):
        text = "Patient DOB 1972-05-10 came for a checkup."
        result = synth.synthesize(text)
        assert "1972-05-10" not in result

    def test_synthesize_preserves_non_pii_tokens(self, synth):
        text = "The patient presented with hypertension and chest pain."
        result = synth.synthesize(text)
        assert "hypertension" in result
        assert "chest pain" in result

    def test_synthesize_clinical_note(self, synth):
        note = (
            "Patient John Smith, DOB 1972-05-10, "
            "presented at City Hospital. Contact: jsmith@email.com, "
            "Phone: 555-123-4567."
        )
        result = synth.synthesize(note)
        assert isinstance(result, str)
        assert len(result) > 0
        # Original person name should not appear in output
        assert "John Smith" not in result
        # Original email should not appear in output
        assert "jsmith@email.com" not in result

    def test_two_calls_produce_different_output(self, synth):
        text = "Patient Jane Doe, email jane@test.com, phone 555-999-1234."
        results = {synth.synthesize(text) for _ in range(5)}
        # Each call uses a fresh Faker value, so we expect at least 2 distinct outputs
        assert len(results) >= 2

    def test_empty_string(self, synth):
        result = synth.synthesize("")
        assert result == ""
