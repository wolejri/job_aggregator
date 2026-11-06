from typing import Protocol
from app.models.job import Job

class JobSourceAdapter(Protocol):
    name: str
    def search(self, keywords: list[str], location: str) -> list[Job]: ...
