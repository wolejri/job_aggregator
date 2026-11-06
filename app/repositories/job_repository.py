from typing import Protocol
from app.models.job import Job
class JobRepository(Protocol):
    def save_many(self, jobs: list[Job]) -> None: ...
    def find_recent(self, since): ...
class InMemoryJobRepository:
    def __init__(self): self._jobs = {}
    def save_many(self, jobs):
        for job in jobs: self._jobs[job.id] = job
    def find_recent(self, since):
        return [job for job in self._jobs.values() if job.posted_at and job.posted_at >= since]
