import os
from app.models.job import Job
from .utils import get_json, parse_date, remote_arrangement

class GreenhouseAdapter:
    name = "Greenhouse"
    """Fetches public Greenhouse boards. Configure GREENHOUSE_BOARDS=company:board_token,..."""
    def search(self, keywords, location):
        boards = [x.strip().split(":", 1) for x in os.getenv("GREENHOUSE_BOARDS", "").split(",") if ":" in x]
        found = {}
        for company, token in boards:
            payload = get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs", {"content":"true"})
            for item in payload.get("jobs", []):
                content = item.get("content", "")
                text = f"{item.get('title','')} {content}".lower()
                if not any(k.lower() in text for k in keywords): continue
                loc = item.get("location", {}).get("name", "")
                arrangement = remote_arrangement(loc + " " + content)
                job = Job(id=f"greenhouse:{token}:{item.get('id')}", title=item.get("title", ""), company=company, location=loc,
                    url=item.get("absolute_url", ""), posted_at=parse_date(item.get("updated_at")), description=content, source=self.name,
                    remote=arrangement == "remote", work_arrangement=arrangement, eligibility_verified=False,
                    eligibility_note="Greenhouse board listing does not independently verify country eligibility")
                if job.url: found[job.id] = job
        return list(found.values())
