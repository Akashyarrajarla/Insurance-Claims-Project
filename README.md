# Insurance Claims Processing – Synthetic Data Project

## 1. Objective

Generate a reproducible synthetic insurance claims dataset and evaluate whether submitted claims satisfy basic policy, coverage, documentation and eligibility requirements.

The solution simulates an insurance claims processing workflow, identifies potential claim exceptions, evaluates claim eligibility, calculates settlement amounts and preserves relationships between customers, policies, incidents and claims.

The project demonstrates how synthetic insurance data can be used to test claims processing workflows, validate business rules and evaluate automated claim decision-making.

## 2. Environment and Dependencies

- Python 3.10+
- CSV and JSON
- SQLite-compatible SQL schema
- Python standard library
- No external Python packages required

## 3. Project Setup

Extract the project repository or downloaded ZIP file.

Navigate to the project directory:

```bash
cd insurance_claims_project
```

Run the dataset generator:

```bash
python src/main.py
```

No package installation is required for the current implementation.

## 4. Run the Complete Dataset

Execute the complete synthetic data generation workflow:

```bash
python src/main.py
```

Default configuration:

| Parameter | Value |
|---|---:|
| Customers | 2,000 |
| Insurance policies | 2,000 |
| Claims | 1,000 |
| Claim adjusters | 30 |
| Coverage records | 2,000 |
| Incident records | 1,000 |
| Claim items | 1,000 |
| Document records | 2,000 |
| Assessment records | 1,000 |
| Reserve records | 1,000 |
| Settlement records | 1,000 |
| Random seed | 20261022 |

The generator creates eleven core datasets in CSV and JSON formats.

You can also specify the configuration:

```bash
python src/main.py --seed 20261022 --out output
```

The `--seed` parameter controls reproducibility, while `--out` specifies the output directory.

## 5. Generate a Dataset

The current implementation uses fixed default dataset sizes.

Run:

```bash
python src/main.py
```

Optional arguments:

```bash
python src/main.py --help
```

Supported arguments:

- `--seed`: Random seed for reproducible data generation.
- `--out`: Output directory for generated files.

The current version does not expose command-line options for independently changing the number of customers, policies, claims or adjusters.

## 6. Required ID Conventions

| Entity | Example |
|---|---|
| Customer | CUS-000001 |
| Adjuster | ADJ-0001 |
| Policy | POL-000001 |
| Coverage | COV-000001 |
| Incident | INC-000001 |
| Claim | CLM-000001 |
| Claim item | ITM-000001 |
| Document | DOC-000001-1 |
| Assessment | ASM-000001 |
| Reserve | RSV-000001 |
| Settlement | SET-000001 |

Each entity uses a unique identifier to maintain traceability across the claims processing workflow.

Claim IDs connect claim information with associated incidents, policies, documents, assessments, reserves and settlements.

## 7. Data Model and Relationships

The implementation includes eleven core entities:

1. Customers
2. Adjusters
3. Policies
4. Coverage
5. Incidents
6. Claims
7. Claim items
8. Documents
9. Assessments
10. Reserves
11. Settlements

Additional supporting datasets:

- `ground_truth/ground_truth.csv` – Stores expected claim scenarios and decisions.
- `reports/validation_summary.json` – Stores dataset counts and validation results.
- `reports/validation_summary.txt` – Stores a readable validation summary.
- `schema.sql` – Defines the relational SQLite-compatible database schema.

The main relationships include:

- One customer can hold an insurance policy.
- Each policy is associated with a customer.
- Each policy has a corresponding coverage record.
- Each incident is associated with a policy.
- Each claim references a policy and an incident.
- Each claim can contain claim items and supporting documents.
- Each claim receives an assessment from an adjuster.
- Each claim has a reserve record and a settlement record.

The relational schema uses primary keys and foreign-key references to maintain data relationships.

## 8. Data Generation and Processing Workflow

The complete synthetic data generation workflow follows this sequence:

1. Generate customer master data.
2. Generate insurance adjuster records.
3. Create insurance policies with coverage limits, deductibles and policy periods.
4. Generate corresponding coverage records.
5. Generate incidents associated with insurance policies.
6. Create claims associated with incidents and policies.
7. Generate claim items and supporting documents.
8. Assign adjusters and generate claim assessments.
9. Calculate reserve amounts.
10. Calculate settlement amounts and payment statuses.
11. Generate controlled exception scenarios and ground-truth labels.
12. Export datasets into CSV and JSON formats.
13. Generate the validation summary.

The generator uses a fixed random seed to support repeatable dataset generation.

## 9. Controlled Anomalies and Ground Truth

The dataset includes five deliberately defined claim scenarios:

| Scenario | Expected decision | Description |
|---|---|---|
| VALID | APPROVE | Claim satisfies the generated policy and document checks. |
| MISSING_DOCUMENT | REQUEST_DOCUMENTS | Required incident evidence is missing. |
| DUPLICATE_CLAIM | MANUAL_REVIEW | Potential duplicate claim requires investigation. |
| OUTSIDE_POLICY_PERIOD | REJECT | Incident occurred outside the policy coverage period. |
| OVER_LIMIT | MANUAL_REVIEW | Claimed amount exceeds the policy coverage limit. |

The first five claims are assigned these five scenarios respectively.

The remaining 995 claims are generated using the VALID scenario.

Expected decisions and scenario labels are stored separately in:

- `ground_truth/ground_truth.csv`
- `ground_truth` scenario records generated by the main script.

Ground-truth separation: The scenario labels represent expected evaluation outcomes. They are not passed as input features to an independent compliance engine. The current implementation generates the assessment decisions using the same scenario conditions used to create the labels.

This makes the dataset useful for testing known claim scenarios, although an independent decision engine would be required for a fully independent evaluation.

## 10. Claim Eligibility and Settlement Calculation

The project simulates basic insurance claim eligibility and settlement processing.

Each policy contains:

- Policy start date.
- Policy end date.
- Policy status.
- Coverage limit.
- Deductible.
- Policy type.

Claim assessments contain:

- Assigned adjuster.
- Eligible amount.
- Assessment date.
- Decision.
- Decision reason.

The settlement calculation follows this formula:

```python
min(
    max(claim_amount - deductible, 0),
    coverage_limit
)
```

Settlement amounts are calculated only for claims receiving an APPROVE decision.

For other decisions, the approved settlement amount is zero.

The project also generates reserve records based on the lesser of the claimed amount and policy coverage limit.

These rules are synthetic demonstration assumptions and are not intended to represent every real-world insurance policy or regulatory requirement.

## 11. Validation

The generator performs basic structural and relationship validation and stores the results in:

```text
reports/validation_summary.json
reports/validation_summary.txt
```

The validation checks include:

- Policy-to-customer relationship integrity.
- Claim-to-policy relationship integrity.
- Claim-to-incident relationship integrity.
- Unique claim identifiers.
- Non-negative claimed amounts.
- Generated record counts.

### Full Dataset Validation Results

The included full-dataset validation report contains:

| Validation metric | Result |
|---|---:|
| Customers generated | 2,000 |
| Adjusters generated | 30 |
| Policies generated | 2,000 |
| Coverage records generated | 2,000 |
| Incidents generated | 1,000 |
| Claims generated | 1,000 |
| Claim items generated | 1,000 |
| Documents generated | 2,000 |
| Assessments generated | 1,000 |
| Reserves generated | 1,000 |
| Settlements generated | 1,000 |
| Policy-customer relationship check | PASS |
| Claim-policy relationship check | PASS |
| Claim-incident relationship check | PASS |
| Unique claim ID check | PASS |
| Non-negative amount check | PASS |

<PRIVATE_PERSON> Overall structural validation: PASS.

The validation report confirms that all five implemented validation checks passed for the included dataset.

Note: The current validation implementation does not yet perform comprehensive SQLite foreign-key checks, duplicate checks across every table, policy coverage calculations or independent ground-truth decision verification.

## 12. Claims Dashboard and Status Lookup

The project includes a web-based Claims Dashboard.

Start the dataset generator:

```bash
python src/main.py
```

Then start the dashboard:

```bash
python src/claim_status_app.py
```

Open the following address in a browser:

```text
http://127.0.0.1:8000
```

The dashboard provides:

- Total claims.
- Approved claims.
- Claims requiring attention.
- Total claimed amount.
- Decision breakdown.
- Claim-type breakdown.
- Searchable claims register.
- Claim status filtering.
- Claim-type filtering.
- Quick exception filters.
- Pagination.
- CSV export of filtered claims.
- Individual claim lookup.

Users can search for a claim using its claim ID, for example:

```text
CLM-000001
```

The claim lookup displays claim details, assessment decisions, claimed amounts, approved settlement amounts, policy information and payment status.

## 13. Reproducibility

The project uses a fixed random seed:

```text
20261022
```

Run the generator using:

```bash
python src/main.py --seed 20261022
```

Using the same seed and configuration allows the synthetic dataset to be regenerated consistently.

The generator uses Python's standard-library random number generator.

The current implementation does not include a separate database checksum comparison or automated reproducibility script.

## 14. Exports

The project supports CSV and JSON exports.

Run the complete generation workflow:

```bash
python src/main.py
```

Generated files are stored in the following directories:

```text
data/
ground_truth/
reports/
```

CSV exports include:

- customers.csv
- adjusters.csv
- policies.csv
- coverage.csv
- incidents.csv
- claims.csv
- claim_items.csv
- documents.csv
- assessments.csv
- reserves.csv
- settlements.csv

JSON exports are generated for all eleven core datasets.

Additional files:

- `ground_truth/ground_truth.csv`
- `reports/validation_summary.json`
- `reports/validation_summary.txt`
- `schema.sql`

The SQL schema provides the relational table definitions for SQLite-compatible database setup.

The current generator exports CSV and JSON data and creates the SQL schema. It does not currently generate a populated SQLite database or a SQL data-dump export.

## 15. Data Provenance

All generated insurance data is synthetic.

No real customer, policyholder, insurance company, claim, incident or payment information is used.

The generator creates fictional:

- Customer names and email addresses.
- Cities and customer records.
- Insurance policies.
- Claim incidents.
- Claim amounts.
- Supporting documents.
- Adjuster assignments.
- Claim decisions.
- Reserve and settlement records.

The email addresses use the reserved `.test` domain.

The fixed random seed supports repeatable generation of the synthetic dataset.

## 16. Assumptions and Limitations

The project uses the following synthetic assumptions:

- Customer names and locations are fictional.
- Insurance policy types include AUTO, HEALTH, PROPERTY, TRAVEL and LIFE.
- Policy coverage limits and deductibles are selected from predefined synthetic values.
- Claims are generated using synthetic incident dates and claim amounts.
- The first five claims represent controlled example scenarios.
- The remaining claims are generated as valid baseline scenarios.
- Claim decisions are based on predefined scenario conditions.
- Settlement amounts follow the implemented deductible and coverage-limit formula.
- Reserve amounts are capped at the policy coverage limit.

Current limitations:

- No actual insurance company data is used.
- No external insurance API integrations are implemented.
- No machine-learning model is included.
- Duplicate claim handling is represented by a predefined synthetic scenario rather than a general duplicate-detection algorithm.
- The validation checks are basic and do not cover every possible relational or business-rule failure.
- The SQL file defines the schema but does not automatically populate a SQLite database.
- The dashboard is a local demonstration application.
- The project does not claim regulatory certification or production insurance processing capability.

The dataset is intended for software testing, synthetic data analysis, insurance workflow demonstrations and claim decision evaluation.

## 17. Repository and Project Structure

The project contains the following main components:

```text
insurance_claims_project/
│
├── src/
│   ├── main.py
│   └── claim_status_app.py
│
├── data/
│   ├── customers.csv
│   ├── customers.json
│   ├── adjusters.csv
│   ├── adjusters.json
│   ├── policies.csv
│   ├── policies.json
│   ├── coverage.csv
│   ├── coverage.json
│   ├── incidents.csv
│   ├── incidents.json
│   ├── claims.csv
│   ├── claims.json
│   ├── claim_items.csv
│   ├── claim_items.json
│   ├── documents.csv
│   ├── documents.json
│   ├── assessments.csv
│   ├── assessments.json
│   ├── reserves.csv
│   ├── reserves.json
│   ├── settlements.csv
│   └── settlements.json
│
├── ground_truth/
│   └── ground_truth.csv
│
├── reports/
│   ├── validation_summary.json
│   └── validation_summary.txt
│
├── schema.sql
└── README.md
```

The repository contains the synthetic data generator, relational schema, generated datasets, ground-truth scenarios, validation reports and claim status dashboard.

**Project:** Insurance Claims Processing – Synthetic Dataset

**Primary execution:** `python src/main.py`

**Dashboard execution:** `python src/claim_status_app.py`

**Dashboard URL:** `http://127.0.0.1:8000`


## 18. PowerShell Commands and Execution Output

The following commands were used to locate the project files, generate the synthetic insurance claims dataset and start the Claims Status Portal on Windows PowerShell.

### 18.1 Locate the Dataset Generator

From the downloaded project directory, run:

```powershell
Get-ChildItem -Recurse -Filter main.py
```

Example output:

```text
Directory: C:\Users\akash\Downloads\insurance_claims_project\insurance_claims_project\src

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----          02-11-2026     14:41           9082 main.py
```

To view the current directory contents:

```powershell
dir
```

Example output:

```text
Directory: C:\Users\akash\Downloads\insurance_claims_project

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----          02-11-2026     14:41                insurance_claims_project
```

### 18.2 Generate the Synthetic Dataset

Change to the inner project directory and run the generator:

```powershell
cd .\insurance_claims_project
python .\src\main.py
```

Example execution output:

```json
{
  "seed": 20261022,
  "counts": {
    "customers": 2000,
    "adjusters": 30,
    "policies": 2000,
    "coverage": 2000,
    "incidents": 1000,
    "claims": 1000,
    "claim_items": 1000,
    "documents": 2000,
    "assessments": 1000,
    "reserves": 1000,
    "settlements": 1000
  },
  "checks": {
    "policy_customer_fk": true,
    "claim_policy_fk": true,
    "claim_incident_fk": true,
    "unique_claim_ids": true,
    "nonnegative_amounts": true
  },
  "all_checks_pass": true
}
```

The output confirms that 2,000 customers, 2,000 policies, 1,000 claims and the other listed records were generated. All five displayed validation checks returned `true`, and `all_checks_pass` is `true`.

### 18.3 Start the Claims Status Portal

After dataset generation, start the dashboard in the same project directory:

```powershell
python .\src\claim_status_app.py
```

Example terminal output:

```text
Claim Status Portal: http://127.0.0.1:8000
Press Ctrl+C to stop.
```

Open the portal in a web browser:

```text
http://127.0.0.1:8000
```

Keep the PowerShell process running while using the portal. Press `Ctrl+C` in the terminal to stop the local dashboard server.
