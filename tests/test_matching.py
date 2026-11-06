from app.services.resume_service import extract_profile, build_search_terms
from app.services.matching_service import score_job

def test_extracts_cloud_infrastructure_and_multiple_engineering_roles():
    resume = "Senior Software Engineer and Platform Engineer. Cloud Infrastructure: AWS, Azure, Kubernetes, Terraform, Docker, Linux, Prometheus, Grafana, CI/CD. Data Engineer experience with Kafka and PostgreSQL."
    profile = extract_profile(resume)
    assert {"software engineer", "platform engineer", "cloud engineer", "infrastructure engineer", "data engineer"}.issubset(set(profile["titles"]))
    assert {"aws", "azure", "kubernetes", "terraform", "docker", "linux", "prometheus", "grafana", "kafka", "postgresql"}.issubset(set(profile["skills"]))
    terms = build_search_terms(profile)
    assert "platform engineer" in terms and "infrastructure engineer" in terms and "cloud engineer" in terms

def test_match_score_rewards_relevant_cloud_role():
    profile = extract_profile("Cloud Engineer with AWS, Kubernetes and Terraform")
    score = score_job({"title":"Cloud Infrastructure Engineer", "description":"AWS Kubernetes Terraform"}, profile)
    assert score >= 80
