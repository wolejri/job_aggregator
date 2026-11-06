from datetime import datetime, timedelta, timezone
NORTH_AMERICA = {"CA", "US", "MX"}
def filter_by_time(jobs, duration_seconds, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None: now = now.replace(tzinfo=timezone.utc)
    cutoff = now - timedelta(seconds=duration_seconds)
    return [job for job in jobs if job.posted_at and cutoff <= (job.posted_at.replace(tzinfo=timezone.utc) if job.posted_at.tzinfo is None else job.posted_at) <= now]
def filter_by_preferences(jobs, preferences):
    result = []
    for job in jobs:
        remote_capable = job.work_arrangement in {"remote", "hybrid"}
        if preferences.work_arrangement == "remote" and job.work_arrangement != "remote": continue
        if preferences.work_arrangement == "remote_hybrid" and job.work_arrangement not in {"remote", "hybrid"}: continue
        if preferences.remote_scope == "canada":
            if job.job_country != "CA" and not (remote_capable and job.eligibility_verified and "CA" in job.eligible_countries): continue
        elif preferences.remote_scope == "north_america":
            if not remote_capable or not job.eligibility_verified or not (set(job.eligible_countries) & NORTH_AMERICA): continue
        elif preferences.remote_scope == "anywhere":
            if not remote_capable or not job.eligibility_verified or not job.eligible_countries: continue
        elif job.eligible_countries and not (set(job.eligible_countries) & set(preferences.regions)): continue
        result.append(job)
    return result
