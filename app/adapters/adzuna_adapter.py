import os
from app.models.job import Job
from .utils import get_json, parse_date, country_codes

class AdzunaAdapter:
    name = "Adzuna"
    def __init__(self, country="ca"): self.country = country
    def search(self, keywords, location):
        app_id, app_key = os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY")
        if not app_id or not app_key: return []
        found = {}
        for term in keywords[:3]:
            payload = get_json(f"https://api.adzuna.com/v1/api/jobs/{self.country}/search/1", {"app_id":app_id,"app_key":app_key,"results_per_page":50,"what":term,"where":location,"content-type":"application/json","sort_by":"date"})
            for item in payload.get("results", []):
                loc = item.get("location", {}).get("display_name", "")
                codes = country_codes(loc)
                job = Job(id=f"adzuna:{item.get('id')}", title=item.get("title", ""), company=item.get("company", {}).get("display_name", ""), location=loc,
                    url=item.get("redirect_url", ""), posted_at=parse_date(item.get("created")), description=item.get("description", ""), source=self.name,
                    remote=False, work_arrangement="unknown", eligible_countries=codes, eligibility_verified=False, job_country=self.country.upper(),
                    eligibility_note="Regional search result; remote-work eligibility is not established")
                if job.url: found[job.id] = job
        return list(found.values())
