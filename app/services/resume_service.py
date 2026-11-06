import io
import re
from html import unescape
from pathlib import Path
from app.models.resume import ResumeProfile

# Canonical skills are deliberately broad across application, cloud, platform,
# infrastructure, reliability, security, data and delivery engineering.
SKILL_GROUPS = {
    "languages": ["python", "java", "javascript", "typescript", "go", "golang", "c++", "c#", "c", "scala", "kotlin", "ruby", "php", "bash", "shell", "powershell", "sql"],
    "cloud": ["aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud platform", "cloud computing", "cloud architecture", "cloudformation", "aws cloudformation", "iam", "vpc", "ec2", "s3", "lambda", "eks", "ecs", "aks", "gke"],
    "infrastructure_devops": ["docker", "kubernetes", "k8s", "terraform", "terragrunt", "ansible", "puppet", "chef", "helm", "istio", "service mesh", "infrastructure as code", "iac", "linux", "unix", "networking", "dns", "tcp/ip", "load balancing", "nginx", "apache", "virtualization", "vmware", "containers", "containerization"],
    "ci_cd": ["ci/cd", "continuous integration", "continuous delivery", "continuous deployment", "github actions", "gitlab ci", "jenkins", "circleci", "buildkite", "argo cd", "argocd", "spinnaker", "deployment automation", "release engineering"],
    "backend_data": ["node.js", "nodejs", "django", "flask", "fastapi", "spring boot", "spring", "express", "rest api", "restful api", "graphql", "grpc", "microservices", "distributed systems", "postgresql", "postgres", "mysql", "mariadb", "mongodb", "redis", "elasticsearch", "opensearch", "dynamodb", "cassandra", "kafka", "rabbitmq", "apache spark", "spark", "airflow", "dbt", "snowflake", "databricks", "data engineering", "etl", "elt", "data pipelines", "data warehousing", "data warehouse"],
    "observability_reliability": ["observability", "monitoring", "logging", "tracing", "prometheus", "grafana", "datadog", "new relic", "opentelemetry", "splunk", "elk stack", "sre", "site reliability engineering", "incident management", "on-call", "on call", "root cause analysis", "high availability", "disaster recovery", "performance tuning", "capacity planning"],
    "security": ["cybersecurity", "application security", "cloud security", "iam", "oauth", "oauth2", "oidc", "saml", "zero trust", "secrets management", "vault", "threat modeling", "vulnerability management", "soc 2", "iso 27001"],
    "frontend_testing": ["react", "angular", "vue", "html", "css", "pytest", "junit", "unit testing", "integration testing", "test automation", "selenium", "playwright", "cypress", "tdd", "bdd", "git", "github", "gitlab", "agile", "scrum"],
}

TITLE_ALIASES = {
    "software engineer": ["software engineer", "software developer", "application developer"],
    "backend engineer": ["backend engineer", "back-end engineer", "backend developer", "back end developer"],
    "frontend engineer": ["frontend engineer", "front-end engineer", "frontend developer", "front end developer"],
    "full stack engineer": ["full stack engineer", "full-stack engineer", "full stack developer", "full-stack developer"],
    "platform engineer": ["platform engineer", "platform developer", "developer platform engineer"],
    "infrastructure engineer": ["infrastructure engineer", "infrastructure developer", "systems engineer", "systems administrator", "cloud infrastructure"],
    "cloud engineer": ["cloud engineer", "cloud developer", "cloud architect", "cloud infrastructure engineer", "cloud infrastructure"],
    "devops engineer": ["devops engineer", "dev ops engineer", "devops developer", "build and release engineer"],
    "site reliability engineer": ["site reliability engineer", "site-reliability engineer", "reliability engineer", "sre"],
    "production engineer": ["production engineer", "production systems engineer"],
    "systems engineer": ["systems engineer", "distributed systems engineer"],
    "network engineer": ["network engineer", "network infrastructure engineer"],
    "security engineer": ["security engineer", "cloud security engineer", "application security engineer", "devsecops engineer"],
    "data engineer": ["data engineer", "analytics engineer", "data platform engineer", "data infrastructure engineer"],
    "machine learning engineer": ["machine learning engineer", "ml engineer", "mlops engineer", "ai infrastructure engineer"],
    "database engineer": ["database engineer", "database administrator", "database reliability engineer"],
    "qa automation engineer": ["qa automation engineer", "quality automation engineer", "test automation engineer", "software development engineer in test", "sdet"],
    "python developer": ["python developer", "python engineer"],
    "java developer": ["java developer", "java engineer"],
}


def extract_resume_text(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        import fitz
        with fitz.open(stream=content, filetype="pdf") as doc:
            return "\n".join(page.get_text("text", sort=True) for page in doc)
    if ext == ".docx":
        from docx import Document
        doc = Document(io.BytesIO(content))
        chunks = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                chunks.append(" | ".join(cell.text for cell in row.cells))
        for section in doc.sections:
            chunks.extend(p.text for p in section.header.paragraphs)
            chunks.extend(p.text for p in section.footer.paragraphs)
        return "\n".join(chunks)
    if ext == ".rtf":
        from striprtf.striprtf import rtf_to_text
        return rtf_to_text(content.decode("utf-8", errors="ignore"))
    if ext in {".txt", ".html", ".htm"}:
        value = content.decode("utf-8-sig", errors="ignore")
        if ext in {".html", ".htm"}:
            value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
            value = re.sub(r"<[^>]+>", " ", value)
            value = unescape(value)
        return value
    raise ValueError("Supported formats: PDF, DOCX, TXT, RTF and HTML. Convert legacy .doc files to DOCX or PDF.")


def _contains_phrase(text: str, phrase: str) -> bool:
    # Treat punctuation/spacing variants as equivalent while avoiding partial words.
    pattern = r"(?<![a-z0-9])" + re.escape(phrase.lower()).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def extract_profile(text: str) -> dict:
    normalized = re.sub(r"\s+", " ", (text or "").lower())
    skills = []
    for group in SKILL_GROUPS.values():
        for skill in group:
            if _contains_phrase(normalized, skill) and skill not in skills:
                skills.append(skill)
    titles = []
    for canonical, aliases in TITLE_ALIASES.items():
        if any(_contains_phrase(normalized, alias) for alias in aliases):
            titles.append(canonical)
    seniority = [level for level in ("intern", "junior", "intermediate", "mid-level", "senior", "staff", "principal", "lead", "director") if _contains_phrase(normalized, level)]
    return {"skills": skills, "titles": titles, "seniority": seniority, "text": normalized}


def build_search_terms(profile: dict, extra_terms: list[str] | None = None) -> list[str]:
    """Use all detected role families and skills; de-duplicate without a two-role cap."""
    terms = list(profile.get("titles", []))
    # Keep the search fan-out useful without discarding infrastructure/cloud keywords.
    priority = ["python", "java", "aws", "azure", "gcp", "kubernetes", "terraform", "docker", "linux", "devops", "platform", "infrastructure", "prometheus", "grafana", "kafka", "postgresql", "data engineering"]
    skills = profile.get("skills", [])
    terms.extend(skill for skill in priority if skill in skills)
    terms.extend(skill for skill in skills if skill not in terms and len(terms) < 30)
    terms.extend(extra_terms or [])
    result, seen = [], set()
    for term in terms:
        value = term.strip()
        if value and value.casefold() not in seen:
            result.append(value); seen.add(value.casefold())
    return result
