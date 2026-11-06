import re

def score_job(job: dict, profile: dict) -> int:
    text = " ".join([job.get("title", ""), job.get("description", "")]).casefold()
    skills = profile.get("skills", [])
    titles = profile.get("titles", [])
    matched = [s for s in skills if re.search(r"(?<![a-z0-9])" + re.escape(s.casefold()) + r"(?![a-z0-9])", text)]
    title_hits = sum(1 for title in titles if title.casefold() in job.get("title", "").casefold())
    # Cap denominator so a long resume does not dilute relevant matches excessively.
    skill_score = min(1.0, len(matched) / max(1, min(len(skills), 12)))
    title_bonus = min(20, title_hits * 10)
    return min(100, round(skill_score * 80 + title_bonus))
