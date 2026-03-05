#!/usr/bin/env python3
"""
generate_data.py — Main CLI entry point for synthetic HLS data generation.

Generates synthetic healthcare datasets using Microsoft Presidio and
optionally uploads them to an Azure CosmosDB account.

Usage
-----
    # Generate 50 patients and upload to CosmosDB (credentials in .env)
    python generate_data.py --patients 50

    # Dry-run: generate data and print summary without uploading
    python generate_data.py --patients 10 --dry-run

    # Override CosmosDB settings on the command line
    python generate_data.py \\
        --endpoint https://myaccount.documents.azure.com:443/ \\
        --key <key> \\
        --database MyDatabase \\
        --patients 100 \\
        --encounters 3
"""

import argparse
import json
import sys
import time

from config import Config
from src.generators.patient import PatientGenerator
from src.generators.encounter import EncounterGenerator
from src.generators.diagnosis import DiagnosisGenerator
from src.generators.medication import MedicationGenerator
from src.generators.lab_result import LabResultGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic HLS datasets using Microsoft Presidio."
    )
    parser.add_argument(
        "--patients",
        type=int,
        default=Config.NUM_PATIENTS,
        help=f"Number of synthetic patients to generate (default: {Config.NUM_PATIENTS}).",
    )
    parser.add_argument(
        "--encounters",
        type=int,
        default=Config.NUM_ENCOUNTERS_PER_PATIENT,
        help=(
            f"Number of encounters per patient "
            f"(default: {Config.NUM_ENCOUNTERS_PER_PATIENT})."
        ),
    )
    parser.add_argument(
        "--endpoint",
        default=Config.COSMOS_ENDPOINT,
        help="CosmosDB account endpoint URL (overrides COSMOS_ENDPOINT env var).",
    )
    parser.add_argument(
        "--key",
        default=Config.COSMOS_KEY,
        help="CosmosDB account key (overrides COSMOS_KEY env var).",
    )
    parser.add_argument(
        "--database",
        default=Config.COSMOS_DATABASE_NAME,
        help=(
            f"CosmosDB database name "
            f"(default: {Config.COSMOS_DATABASE_NAME})."
        ),
    )
    parser.add_argument(
        "--locale",
        default=Config.FAKER_LOCALE,
        help=f"Faker locale for synthetic data (default: {Config.FAKER_LOCALE}).",
    )
    parser.add_argument(
        "--spacy-model",
        default="en_core_web_sm",
        help="spaCy model used by Presidio (default: en_core_web_sm).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Generate data and print a summary without uploading to CosmosDB. "
            "CosmosDB credentials are not required in dry-run mode."
        ),
    )
    return parser.parse_args()


def _print_summary(label: str, documents: list) -> None:
    count = len(documents)
    sample = documents[0] if documents else {}
    print(f"  {label}: {count} documents generated.")
    if sample:
        print(f"    Sample keys: {list(sample.keys())}")


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("Synthetic HLS Data Generator (Microsoft Presidio + CosmosDB)")
    print("=" * 60)
    print(f"  Patients        : {args.patients}")
    print(f"  Encounters/pt   : {args.encounters}")
    print(f"  Locale          : {args.locale}")
    print(f"  spaCy model     : {args.spacy_model}")
    print(f"  Dry-run         : {args.dry_run}")
    if not args.dry_run:
        print(f"  CosmosDB DB     : {args.database}")
    print()

    # ------------------------------------------------------------------ #
    # 1. Generate patients
    # ------------------------------------------------------------------ #
    print("[1/5] Generating patients …")
    t0 = time.time()
    patient_gen = PatientGenerator(locale=args.locale, spacy_model=args.spacy_model)
    patients = patient_gen.generate(count=args.patients)
    print(f"      {len(patients)} patients generated in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------ #
    # 2. Generate encounters
    # ------------------------------------------------------------------ #
    print("[2/5] Generating encounters …")
    t0 = time.time()
    encounter_gen = EncounterGenerator(
        locale=args.locale, spacy_model=args.spacy_model
    )
    encounters = encounter_gen.generate(
        patients=patients, encounters_per_patient=args.encounters
    )
    print(f"      {len(encounters)} encounters generated in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------ #
    # 3. Generate diagnoses
    # ------------------------------------------------------------------ #
    print("[3/5] Generating diagnoses …")
    t0 = time.time()
    diagnosis_gen = DiagnosisGenerator()
    diagnoses = diagnosis_gen.generate(encounters=encounters)
    print(f"      {len(diagnoses)} diagnoses generated in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------ #
    # 4. Generate medications
    # ------------------------------------------------------------------ #
    print("[4/5] Generating medications …")
    t0 = time.time()
    med_gen = MedicationGenerator(locale=args.locale)
    medications = med_gen.generate(encounters=encounters)
    print(f"      {len(medications)} medications generated in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------ #
    # 5. Generate lab results
    # ------------------------------------------------------------------ #
    print("[5/5] Generating lab results …")
    t0 = time.time()
    lab_gen = LabResultGenerator(locale=args.locale)
    lab_results = lab_gen.generate(encounters=encounters)
    print(f"      {len(lab_results)} lab results generated in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    print()
    print("Generation complete:")
    _print_summary("Patients", patients)
    _print_summary("Encounters", encounters)
    _print_summary("Diagnoses", diagnoses)
    _print_summary("Medications", medications)
    _print_summary("Lab Results", lab_results)
    total = (
        len(patients)
        + len(encounters)
        + len(diagnoses)
        + len(medications)
        + len(lab_results)
    )
    print(f"\n  Total documents : {total}")

    if args.dry_run:
        print("\nDry-run mode: skipping CosmosDB upload.")
        print("Sample patient document:")
        print(json.dumps(patients[0], indent=2, default=str))
        return

    # ------------------------------------------------------------------ #
    # Upload to CosmosDB
    # ------------------------------------------------------------------ #
    endpoint = args.endpoint
    key = args.key
    if not endpoint or not key:
        print(
            "\nError: CosmosDB credentials are required. "
            "Set COSMOS_ENDPOINT and COSMOS_KEY in your .env file "
            "or pass --endpoint and --key on the command line.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nUploading to CosmosDB ({args.database}) …")
    from src.cosmosdb.uploader import CosmosUploader

    uploader = CosmosUploader(
        endpoint=endpoint, key=key, database_name=args.database
    )

    n = uploader.upload_patients(patients)
    print(f"  ✓ {n} patients uploaded.")
    n = uploader.upload_encounters(encounters)
    print(f"  ✓ {n} encounters uploaded.")
    n = uploader.upload_diagnoses(diagnoses)
    print(f"  ✓ {n} diagnoses uploaded.")
    n = uploader.upload_medications(medications)
    print(f"  ✓ {n} medications uploaded.")
    n = uploader.upload_lab_results(lab_results)
    print(f"  ✓ {n} lab results uploaded.")

    print("\nAll done! Your synthetic HLS dataset is ready in CosmosDB.")


if __name__ == "__main__":
    main()
