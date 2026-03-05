# MSFT-CosmosDB-SyntheticHLSData

Generate synthetic **Healthcare and Life Sciences (HLS)** datasets using
[Microsoft Presidio](https://microsoft.github.io/presidio/) and store them in
your own **Azure Cosmos DB** account for use in projects and demos.

---

## Overview

This tool creates realistic, fully synthetic healthcare records across five
entity types:

| Container | FHIR ResourceType | Description |
|---|---|---|
| `patients` | `Patient` | Demographics, insurance, Presidio-synthesized clinical summary |
| `encounters` | `Encounter` | Outpatient / ER / inpatient visits with vitals and physician notes |
| `diagnoses` | `Condition` | ICD-10-CM coded diagnoses linked to encounters |
| `medications` | `MedicationRequest` | Prescriptions with dose, route, and frequency |
| `lab_results` | `Observation` | CBC, CMP, lipid panel, HbA1c, thyroid, and urinalysis results |

**How Presidio is used:** every free-text clinical note is first populated with
realistic Faker-generated data (names, dates, phone numbers, emails), then
passed through the **Presidio Analyzer** (PII detection) and **Presidio
Anonymizer** (replacement with fresh Faker values). This guarantees that no
real PHI can accidentally appear in the output.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.9+ | Tested with Python 3.12 |
| Azure Cosmos DB account | Any tier; free tier works for demos |
| Internet access | Required at first run to download the spaCy NLP model |

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/dbhimjiyani/MSFT-CosmosDB-SyntheticHLSData.git
cd MSFT-CosmosDB-SyntheticHLSData
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

> **Tip:** use `en_core_web_lg` instead of `en_core_web_sm` to improve PII
> detection accuracy in clinical notes (requires ~700 MB of disk space).

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env and fill in your CosmosDB endpoint and key
```

Your `.env` file should look like:

```
COSMOS_ENDPOINT=https://<your-account>.documents.azure.com:443/
COSMOS_KEY=<your-primary-or-secondary-key>
COSMOS_DATABASE_NAME=SyntheticHealthcareData
NUM_PATIENTS=100
NUM_ENCOUNTERS_PER_PATIENT=3
FAKER_LOCALE=en_US
```

### 3. Generate and upload data

```bash
# Generate 100 patients (reads credentials from .env)
python generate_data.py

# Override record counts on the command line
python generate_data.py --patients 500 --encounters 5

# Dry-run: generate locally without uploading (no CosmosDB required)
python generate_data.py --patients 10 --dry-run
```

---

## CLI Reference

```
python generate_data.py [OPTIONS]

Options:
  --patients INT        Number of synthetic patients (default: 100)
  --encounters INT      Encounters per patient (default: 3)
  --endpoint URL        CosmosDB endpoint (overrides COSMOS_ENDPOINT)
  --key KEY             CosmosDB key (overrides COSMOS_KEY)
  --database NAME       Database name (default: SyntheticHealthcareData)
  --locale LOCALE       Faker locale, e.g. en_US, en_GB (default: en_US)
  --spacy-model MODEL   spaCy model for Presidio (default: en_core_web_sm)
  --dry-run             Generate data only; skip CosmosDB upload
```

---

## Project Structure

```
MSFT-CosmosDB-SyntheticHLSData/
├── generate_data.py          # Main CLI entry point
├── config.py                 # Environment-based configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── src/
│   ├── synthesizer.py        # Presidio-based PII synthesizer
│   ├── generators/
│   │   ├── patient.py        # Patient demographics generator
│   │   ├── encounter.py      # Clinical encounter generator
│   │   ├── diagnosis.py      # ICD-10 diagnosis generator
│   │   ├── medication.py     # Medication / prescription generator
│   │   └── lab_result.py     # Laboratory result generator
│   └── cosmosdb/
│       └── uploader.py       # CosmosDB database / container management
└── tests/
    ├── test_generators.py    # Unit tests for generators
    └── test_synthesizer.py   # Unit tests for Presidio synthesizer
```

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## CosmosDB Schema

All containers use `/patientId` as the partition key to enable efficient
per-patient queries across the entire dataset.

### Query example — all data for a patient

```python
from azure.cosmos import CosmosClient

client = CosmosClient(endpoint, key)
db = client.get_database_client("SyntheticHealthcareData")

patient_id = "<uuid>"
for container_name in ["encounters", "diagnoses", "medications", "lab_results"]:
    container = db.get_container_client(container_name)
    items = list(container.query_items(
        query="SELECT * FROM c WHERE c.patientId = @pid",
        parameters=[{"name": "@pid", "value": patient_id}],
        partition_key=patient_id,
    ))
    print(f"{container_name}: {len(items)} records")
```

---

## License

This project is provided for demonstration and educational purposes.

