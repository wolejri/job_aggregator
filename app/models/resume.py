from dataclasses import dataclass, field

@dataclass
class ResumeProfile:
    text: str
    skills: list[str] = field(default_factory=list)
    titles: list[str] = field(default_factory=list)
    seniority: list[str] = field(default_factory=list)
