from app.adapters import AdzunaAdapter, GreenhouseAdapter, LeverAdapter, AshbyAdapter, RemotiveAdapter, ArbeitnowAdapter
from app.repositories.job_repository import InMemoryJobRepository
from app.services.aggregation_service import AggregationService

class JobController:
    """Application composition root; provider implementations are swappable."""
    def __init__(self, adapters=None, repository=None):
        self.repository = repository or InMemoryJobRepository()
        self.service = AggregationService(adapters or [
            RemotiveAdapter(), ArbeitnowAdapter(), AdzunaAdapter("ca"), AdzunaAdapter("us"),
            GreenhouseAdapter(), LeverAdapter(), AshbyAdapter()
        ], self.repository)
    def search(self, keywords, preferences, profile):
        jobs, errors = self.service.search(keywords, preferences, profile)
        return {"jobs": [job.to_dict() for job in jobs], "errors": errors}
