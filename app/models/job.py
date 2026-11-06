from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    url: str
    posted_at: Optional[datetime]
    description: str = ""
    source: str = "unknown"
    remote: bool = False
    work_arrangement: str = "unknown"
    eligible_countries: list[str] = field(default_factory=list)
    eligibility_verified: bool = False
    job_country: str = ""
    eligibility_note: str = ""
    match_score: int = 0

    def to_dict(self):
        result = dict(self.__dict__)
        result["posted_at"] = self.posted_at.isoformat() if self.posted_at else None
        return result
