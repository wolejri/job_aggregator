import pandas as pd
import streamlit as st
from datetime import datetime
from app.services.resume_service import extract_resume_text, extract_profile, build_search_terms
from app.models.search_preferences import SearchPreferences
from app.api.job_controller import JobController

st.set_page_config(page_title="Resume-powered Job Aggregator", page_icon="🔎", layout="wide")
st.title("🔎 Resume-powered Job Aggregator")
st.caption("Extracts multiple engineering role families and skills, searches configured job sources, and ranks current listings.")
with st.sidebar:
    st.header("Search settings")
    location = st.text_input("Search location", value="Canada")
    st.subheader("Remote eligibility")
    scope_label = st.selectbox("Eligibility scope", ["Remote and explicitly open to candidates in Canada", "Remote anywhere in North America", "Remote anywhere worldwide"], index=0)
    scope = {"Remote and explicitly open to candidates in Canada":"canada", "Remote anywhere in North America":"north_america", "Remote anywhere worldwide":"anywhere"}[scope_label]
    arrangement_label = st.selectbox("Work arrangement", ["Fully remote", "Remote or hybrid", "Any arrangement"], index=0)
    arrangement = {"Fully remote":"remote", "Remote or hybrid":"remote_hybrid", "Any arrangement":"any"}[arrangement_label]
    st.caption("Canada mode requires explicit Canadian candidate eligibility for remote roles outside Canada.")
    st.subheader("Published within")
    amount = st.number_input("Amount", min_value=1, value=24, step=1)
    unit = st.selectbox("Time unit", ["seconds", "minutes", "hours", "days"], index=2)
    duration_seconds = int(amount * {"seconds":1, "minutes":60, "hours":3600, "days":86400}[unit])

uploaded = st.file_uploader("Upload resume", type=["pdf", "docx", "txt", "rtf", "html"])
if uploaded:
    try:
        resume_text = extract_resume_text(uploaded.getvalue(), uploaded.name)
        profile = extract_profile(resume_text)
        with st.expander("Extracted resume profile", expanded=True):
            st.write("**Potential engineering roles**")
            st.write(", ".join(profile["titles"]) or "No exact role title detected. Search terms can be added below.")
            st.write("**Detected skills**")
            st.write(", ".join(profile["skills"]) or "No known skills detected.")
            if profile.get("seniority"):
                st.write("**Seniority signals**")
                st.write(", ".join(profile["seniority"]))
        defaults = build_search_terms(profile)
        terms_text = st.text_area("Search terms (all detected role families are included; edit as needed)", value=", ".join(defaults), height=120)
        if st.button("Find matching jobs", type="primary", use_container_width=True):
            terms = [x.strip() for x in terms_text.split(",") if x.strip()]
            if not terms: st.warning("Add at least one search term.")
            else:
                prefs = SearchPreferences(remote_scope=scope, work_arrangement=arrangement, location_query=location, duration_seconds=duration_seconds)
                with st.spinner("Searching sources in parallel, filtering, deduplicating and ranking..."):
                    response = JobController().search(terms, prefs, profile)
                st.session_state["results"] = response["jobs"]
                st.session_state["errors"] = response["errors"]
                st.session_state["window_label"] = f"{amount} {unit}"
                st.session_state["scope_label"] = scope_label
    except Exception as exc:
        st.error(f"Could not read this resume: {exc}")

if "results" in st.session_state:
    results, errors = st.session_state["results"], st.session_state.get("errors", [])
    c1, c2, c3 = st.columns(3)
    c1.metric("Matching jobs", len(results)); c2.metric("Sources with errors", len(errors)); c3.metric("Time window", st.session_state.get("window_label", ""))
    st.caption(f"Eligibility filter: {st.session_state.get('scope_label','')}")
    if errors:
        with st.expander("Source warnings"):
            for error in errors: st.warning(error)
    if not results: st.info("No listings met all filters. Try a longer window or broader terms. Some providers do not expose reliable dates or country eligibility.")
    else:
        df = pd.DataFrame([{"Match": f'{j["match_score"]}%', "Job title":j["title"], "Company":j["company"], "Location":j["location"], "Job country":j.get("job_country", ""), "Posted (UTC)":datetime.fromisoformat(j["posted_at"]).strftime("%Y-%m-%d %H:%M") if j.get("posted_at") else "Unknown", "Arrangement":j["work_arrangement"], "Canadian eligibility verified":"Yes" if "CA" in j.get("eligible_countries", []) and j.get("eligibility_verified") else "No", "Source":j["source"], "Apply":j["url"]} for j in results])
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={"Apply":st.column_config.LinkColumn("Apply", display_text="Open job")})
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name="matching_jobs.csv", mime="text/csv")
else:
    st.info("Upload a resume to extract engineering roles and skills.")
