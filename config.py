"""Configuration management for the synthetic HLS data generator."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Loads and validates configuration from environment variables."""

    # CosmosDB settings
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    COSMOS_DATABASE_NAME: str = os.getenv(
        "COSMOS_DATABASE_NAME", "SyntheticHealthcareData"
    )

    # Data generation settings
    NUM_PATIENTS: int = int(os.getenv("NUM_PATIENTS", "100"))
    NUM_ENCOUNTERS_PER_PATIENT: int = int(
        os.getenv("NUM_ENCOUNTERS_PER_PATIENT", "3")
    )

    # Faker locale
    FAKER_LOCALE: str = os.getenv("FAKER_LOCALE", "en_US")

    @classmethod
    def validate_cosmos(cls) -> None:
        """Raise ValueError if CosmosDB credentials are missing."""
        if not cls.COSMOS_ENDPOINT:
            raise ValueError(
                "COSMOS_ENDPOINT is required. Set it in your .env file or "
                "as an environment variable."
            )
        if not cls.COSMOS_KEY:
            raise ValueError(
                "COSMOS_KEY is required. Set it in your .env file or "
                "as an environment variable."
            )
