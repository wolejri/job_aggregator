from datetime import datetime, timezone
from app.models.job import Job
from app.models.search_preferences import SearchPreferences
from app.services.aggregation_service import AggregationService

class FakeAdapter:
    name = "fake"
    def search(self, keywords, location):
        return [Job(id="1", title="Platform Engineer", company="Acme", location="Canada", url="https://example.com/1", posted_at=datetime.now(timezone.utc), description="Kubernetes AWS Terraform", work_arrangement="remote", job_country="CA")]

def test_aggregation_returns_scored_job():
    profile = {"skills":["kubernetes", "aws", "terraform"], "titles":["platform engineer"]}
    jobs, errors = AggregationService([FakeAdapter()]).search(["platform engineer"], SearchPreferences(), profile)
    assert not errors
    assert len(jobs) == 1 and jobs[0].match_score > 0
