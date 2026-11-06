import os
from app.models.job import Job
from .utils import get_json, parse_date, remote_arrangement

class LeverAdapter:
    name = "Lever"
    """Fetches public Lever company sites. Configure LEVER_SITES=company:site_slug,..."""
    def search(self, keywords, location):
        sites = [x.strip().split(":", 1) for x in os.getenv("LEVER_SITES", "").split(",") if ":" in x]
        found = {}
        for company, slug in sites:
            payload = get_json(f"https://api.lever.co/v0/postings/{slug}", {"mode":"json"})
            for item in payload:
                text = f"{item.get('text','')} {item.get('descriptionPlain','')}".lower()
                if not any(k.lower() in text for k in keywords): continue
                categories = item.get("categories", {})
                loc = categories.get("location", "")
                arrangement = remote_arrangement(loc + " " + item.get("descriptionPlain", ""))
                job = Job(id=f"lever:{slug}:{item.get('id')}", title=item.get("text", ""), company=company, location=loc,
                    url=item.get("hostedUrl", ""), posted_at=parse_date(item.get("createdAt")), description=item.get("descriptionPlain", ""), source=self.name,
                    remote=arrangement == "remote", work_arrangement=arrangement, eligibility_verified=False,
                    eligibility_note="Lever board listing does not independently verify country eligibility")
                if job.url: found[job.id] = job
        return list(found.values())
