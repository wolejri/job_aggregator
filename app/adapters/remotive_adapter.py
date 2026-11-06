from app.models.job import Job
from .utils import get_json, parse_date, remote_arrangement, country_codes

class RemotiveAdapter:
    name = "Remotive"
    def search(self, keywords, location):
        found = {}
        for term in keywords[:4]:
            payload = get_json("https://remotive.com/api/remote-jobs", {"search": term, "limit": 100})
            for item in payload.get("jobs", []):
                eligible_text = item.get("candidate_required_location", "")
                job = Job(id=f"remotive:{item.get('id')}", title=item.get("title", ""), company=item.get("company_name", ""),
                    location=eligible_text or "Remote", url=item.get("url", ""), posted_at=parse_date(item.get("publication_date")),
                    description=item.get("description", ""), source=self.name, remote=True, work_arrangement="remote",
                    eligible_countries=country_codes(eligible_text), eligibility_verified=bool(country_codes(eligible_text)),
                    eligibility_note=f"Candidate location: {eligible_text or 'not specified'}")
                if job.url: found[job.id] = job
        return list(found.values())
