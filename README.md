# Insurance Claims Processing Synthetic Dataset

Python 3.10+, standard library only.

Run from this folder:
```bash
python src/main.py
```
Optional:
```bash
python src/main.py --seed 20261022 --out output
```

Creates CSV and JSON tables for customers, adjusters, policies, coverage, incidents,
claims, claim items, documents, assessments, reserves, and settlements; a ground-truth
CSV; SQLite schema; and validation reports.

All data is fictional. Settlement formula used in this demonstration:
`min(max(claim_amount - deductible, 0), coverage_limit)`.
The first five claims are labelled example scenarios: valid, missing document,
potential duplicate, outside policy period, and over limit. This is a learning prototype,
not production insurance software.


## Claim Status Portal
Run `python src/claim_status_app.py` after generating data, then open http://127.0.0.1:8000 and enter a claim ID such as `CLM-000001`. Stop with Ctrl+C.


## Claims Dashboard
Run `python src/main.py` to generate data, then `python src/claim_status_app.py` and open http://127.0.0.1:8000. The dashboard shows totals, decision breakdown, claim types, recent claims, and a claim ID lookup.


## Enhanced dashboard features
The dashboard now includes searchable/filterable claims, status and claim-type filters, quick exception filters, pagination, CSV export, decision/type breakdowns, KPI cards, and claim details lookup. Start data generation with `python src/main.py`, then run `python src/claim_status_app.py`.
