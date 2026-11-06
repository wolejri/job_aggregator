# Resume-powered Job Aggregator

Python/Streamlit job search app. Upload a PDF, DOCX, TXT, RTF or HTML resume; extract engineering role families and technical skills; search configured public job sources; filter by rolling publication age; deduplicate and rank results.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env  # optional; export credentials/configuration in your shell
streamlit run app.py
```

## Project structure

```text
job-aggregator/
├── app/
│   ├── api/job_controller.py
│   ├── models/{job,resume,search_preferences}.py
│   ├── adapters/{base_adapter,adzuna_adapter,greenhouse_adapter,lever_adapter,ashby_adapter,remotive_adapter,arbeitnow_adapter,utils}.py
│   ├── services/{resume_service,aggregation_service,filtering_service,matching_service,deduplication_service}.py
│   └── repositories/job_repository.py
├── tests/{test_adapters,test_filtering,test_matching,test_aggregation}.py
├── requirements.txt
└── app.py
```

## Job sources

- Remotive and Arbeitnow are queried through their public endpoints.
- Adzuna requires `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.
- Greenhouse requires `GREENHOUSE_BOARDS='Company:board_token'`.
- Lever requires `LEVER_SITES='Company:site_slug'`.
- Ashby requires `ASHBY_BOARDS='Company:board_name'`.

Greenhouse, Lever and Ashby expose company-specific public boards, not universal job-search APIs. Configure boards for the companies you want to monitor.

## Resume extraction

The parser scans PDF text, DOCX paragraphs/tables/headers/footers, RTF, TXT and HTML. It detects a broad skills taxonomy spanning languages, cloud providers, infrastructure-as-code, containers, orchestration, CI/CD, Linux/networking, observability/SRE, security, data platforms, databases and testing. It also detects multiple role families; it does not cap results at two. Scanned PDFs require OCR and legacy `.doc` files must be converted first.

Detected skills and titles are keyword-based signals, not a full semantic resume parser. Review/edit the generated search terms before searching.

## Eligibility and freshness

Canada scope is conservative: a role outside Canada must explicitly verify Canadian candidate eligibility; generic remote labels or employer headquarters do not count. Listings without publication timestamps are excluded from the requested rolling time window. Provider date precision and coverage vary.

## Tests

```bash
python -m pytest -v
```
