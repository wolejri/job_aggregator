import os
from app.models.job import Job
from .utils import get_json, parse_date, remote_arrangement

class AshbyAdapter:
    """Reads public Ashby job boards. Configure ASHBY_BOARDS=company:board_name,..."""
    name = "Ashby"
    def search(self, keywords, location):
        boards = [x.strip().split(":", 1) for x in os.getenv("ASHBY_BOARDS", "").split(",") if ":" in x]
        found = {}
        for company, board in boards:
            payload = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}", {"includeCompensation":"true"})
            for item in payload.get("jobs", []):
                description = item.get("descriptionPlain") or item.get("descriptionHtml") or ""
                title = item.get("title", "")
                if keywords and not any(k.casefold() in f"{title} {description}".casefold() for k in keywords):
                    continue
                location = item.get("location", "") or ", ".join(item.get("secondaryLocations", []) or [])
                arrangement = remote_arrangement(location + " " + description, explicit_remote=item.get("isRemote", False))
                job = Job(id=f"ashby:{board}:{item.get('id') or item.get('jobUrl')}", title=title, company=company,
                    location=location, url=item.get("jobUrl", ""), posted_at=parse_date(item.get("publishedAt")),
                    description=description, source=self.name, remote=arrangement == "remote", work_arrangement=arrangement,
                    eligibility_verified=False, eligibility_note="Ashby public board does not independently verify candidate-country eligibility")
                if job.url: found[job.id] = job
        return list(found.values())
