from datetime import datetime, timedelta, timezone
from app.models.job import Job
from app.models.search_preferences import SearchPreferences
from app.services.filtering_service import filter_by_time, filter_by_preferences

def make_job(posted_at, **kwargs):
    values = dict(id="1", title="Cloud Engineer", company="Acme", location="Canada", url="https://example.com/1", posted_at=posted_at, work_arrangement="remote", job_country="CA")
    values.update(kwargs)
    return Job(**values)

def test_time_filter_excludes_old_jobs():
    now = datetime.now(timezone.utc)
    assert len(filter_by_time([make_job(now - timedelta(hours=1)), make_job(now - timedelta(days=2))], 86400, now)) == 1

def test_canada_filter_requires_explicit_eligibility_for_us_remote_job():
    prefs = SearchPreferences(remote_scope="canada", work_arrangement="remote")
    unverified = make_job(datetime.now(timezone.utc), job_country="US", eligibility_verified=False)
    verified = make_job(datetime.now(timezone.utc), job_country="US", eligible_countries=["CA"], eligibility_verified=True)
    assert filter_by_preferences([unverified, verified], prefs) == [verified]
