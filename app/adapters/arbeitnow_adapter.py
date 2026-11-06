from app.models.job import Job
from .utils import get_json, parse_date, remote_arrangement, country_codes

class ArbeitnowAdapter:
    name = "Arbeitnow"
    def search(self, keywords, location):
        found = {}
        for page in range(1, 4):
            payload = get_json("https://www.arbeitnow.com/api/job-board-api", {"page": page})
            for item in payload.get("data", []):
                text = " ".join([item.get("title", ""), item.get("company_name", ""), " ".join(item.get("tags", []) or []), item.get("description", "")]).lower()
                if not any(term.lower() in text for term in keywords): continue
                loc = item.get("location", "")
                arrangement = remote_arrangement(loc + " " + item.get("title", ""), item.get("remote", False))
                job = Job(id=f"arbeitnow:{item.get('slug') or item.get('url')}", title=item.get("title", ""), company=item.get("company_name", ""), location=loc,
                    url=item.get("url", ""), posted_at=parse_date(item.get("created_at") or item.get("createdAt")), description=item.get("description", ""),
                    source=self.name, remote=arrangement == "remote", work_arrangement=arrangement,
                    eligible_countries=country_codes(loc), eligibility_verified=False, job_country=(country_codes(loc) or [""])[0],
                    eligibility_note="Source does not reliably establish whether Canadian residents are eligible")
                if job.url: found[job.id] = job
            if not payload.get("links", {}).get("next"): break
        return list(found.values())
