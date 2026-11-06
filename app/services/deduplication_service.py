import re
from urllib.parse import urlsplit, urlunsplit
def _normalize_url(url):
    if not url: return ""
    p = urlsplit(url.strip())
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", ""))
def deduplicate(jobs):
    unique = {}
    for job in jobs:
        key = _normalize_url(job.url) or "|".join(re.sub(r"\W+", " ", x.lower()).strip() for x in (job.company, job.title, job.location))
        if not key: continue
        old = unique.get(key)
        if old is None or (job.posted_at and (not old.posted_at or job.posted_at > old.posted_at)): unique[key] = job
    return list(unique.values())
