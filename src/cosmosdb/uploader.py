"""
Azure CosmosDB uploader for synthetic HLS datasets.

Creates the target database and containers if they do not exist, then
bulk-upserts all generated documents.
"""

from typing import List

from azure.cosmos import CosmosClient, PartitionKey, exceptions


# Container definitions: (container_name, partition_key_path)
_CONTAINERS = [
    ("patients", "/patientId"),
    ("encounters", "/patientId"),
    ("diagnoses", "/patientId"),
    ("medications", "/patientId"),
    ("lab_results", "/patientId"),
]

# Provisioned throughput (RU/s) for each container
_DEFAULT_THROUGHPUT = 400


class CosmosUploader:
    """
    Manages the CosmosDB database / container lifecycle and uploads documents.

    Parameters
    ----------
    endpoint:
        CosmosDB account endpoint URL.
    key:
        CosmosDB account primary or secondary key.
    database_name:
        Name of the database to create / use.
    """

    def __init__(self, endpoint: str, key: str, database_name: str):
        self._client = CosmosClient(endpoint, credential=key)
        self._db = self._client.create_database_if_not_exists(id=database_name)
        self._containers: dict = {}
        self._ensure_containers()

    def _ensure_containers(self) -> None:
        """Create all required containers if they do not already exist."""
        for name, partition_key in _CONTAINERS:
            container = self._db.create_container_if_not_exists(
                id=name,
                partition_key=PartitionKey(path=partition_key),
                offer_throughput=_DEFAULT_THROUGHPUT,
            )
            self._containers[name] = container

    def upload_patients(self, patients: List[dict]) -> int:
        """Upsert *patients* into the ``patients`` container."""
        return self._upsert_all("patients", patients)

    def upload_encounters(self, encounters: List[dict]) -> int:
        """Upsert *encounters* into the ``encounters`` container."""
        return self._upsert_all("encounters", encounters)

    def upload_diagnoses(self, diagnoses: List[dict]) -> int:
        """Upsert *diagnoses* into the ``diagnoses`` container."""
        return self._upsert_all("diagnoses", diagnoses)

    def upload_medications(self, medications: List[dict]) -> int:
        """Upsert *medications* into the ``medications`` container."""
        return self._upsert_all("medications", medications)

    def upload_lab_results(self, lab_results: List[dict]) -> int:
        """Upsert *lab_results* into the ``lab_results`` container."""
        return self._upsert_all("lab_results", lab_results)

    def _upsert_all(self, container_name: str, documents: List[dict]) -> int:
        """Upsert every document in *documents* and return the count uploaded."""
        container = self._containers[container_name]
        uploaded = 0
        for doc in documents:
            try:
                container.upsert_item(body=doc)
                uploaded += 1
            except exceptions.CosmosHttpResponseError as exc:
                raise RuntimeError(
                    f"Failed to upsert document {doc.get('id')} "
                    f"into '{container_name}': {exc}"
                ) from exc
        return uploaded
