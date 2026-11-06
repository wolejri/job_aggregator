from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from app.services.filtering_service import filter_by_time, filter_by_preferences
from app.services.deduplication_service import deduplicate
from app.services.matching_service import score_job
class AggregationService:
    def __init__(self, adapters, repository=None, max_workers=8):
        self.adapters, self.repository, self.max_workers = adapters, repository, max_workers
    def search(self, keywords, preferences, profile):
        preferences.validate(); jobs, errors = [], []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, max(1, len(self.adapters)))) as pool:
            futures = {pool.submit(adapter.search, keywords, preferences.location_query): adapter.name for adapter in self.adapters}
            for future in as_completed(futures):
                try: jobs.extend(future.result())
                except Exception as exc: errors.append(f"{futures[future]}: {type(exc).__name__}: {exc}")
        jobs = deduplicate(filter_by_preferences(filter_by_time(jobs, preferences.duration_seconds), preferences))
        for job in jobs: job.match_score = score_job({"title": job.title, "description": job.description}, profile)
        jobs.sort(key=lambda j: (j.match_score, j.posted_at or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
        if self.repository: self.repository.save_many(jobs)
        return jobs, errors
