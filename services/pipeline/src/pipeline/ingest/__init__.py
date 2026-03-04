from pipeline.ingest.base import BaseIngestor
from pipeline.ingest.parties import PartiesIngestor
from pipeline.ingest.deputies import DeputiesIngestor
from pipeline.ingest.votings import VotingsIngestor

__all__ = [
    "BaseIngestor",
    "PartiesIngestor",
    "DeputiesIngestor",
    "VotingsIngestor",
]
