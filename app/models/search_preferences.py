from dataclasses import dataclass, field

@dataclass
class SearchPreferences:
    regions: list[str] = field(default_factory=lambda: ["CA", "US", "MX"])
    remote_scope: str = "canada"
    work_arrangement: str = "remote"
    location_query: str = "Canada"
    duration_seconds: int = 86400

    def validate(self):
        if self.remote_scope not in {"canada", "north_america", "anywhere"}:
            raise ValueError("Invalid remote eligibility scope")
        if self.work_arrangement not in {"remote", "remote_hybrid", "any"}:
            raise ValueError("Invalid work arrangement")
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
