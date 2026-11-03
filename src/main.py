import argparse, csv, json, random
from pathlib import Path
from datetime import date, timedelta

SEED=20261022
N_CUSTOMERS=2000
N_POLICIES=2000
N_CLAIMS=1000
TYPES=["AUTO","HEALTH","PROPERTY","TRAVEL","LIFE"]
FIRST=["Aarav","Ananya","Ravi","Priya","Arjun","Meera","Kiran","Sana","Vikram","Neha"]
LAST=["Sharma","Kumar","Reddy","Patel","Singh","Rao","Iyer","Das","Khan","Gupta"]
CITIES=["Hyderabad","Chennai","Bengaluru","Pune","Mumbai","Delhi","Kochi","Jaipur"]
FIELDS={
"customers":"customer_id full_name email city created_date",
"adjusters":"adjuster_id full_name specialty",
"policies":"policy_id customer_id policy_type start_date end_date status coverage_limit deductible",
"coverage":"coverage_id policy_id coverage_type coverage_limit exclusions",
"incidents":"incident_id policy_id incident_date incident_type description",
"claims":"claim_id policy_id incident_id claim_type submitted_date claimed_amount status",
"claim_items":"claim_item_id claim_id description quantity unit_cost line_amount",
"documents":"document_id claim_id document_type received_date required is_present",
"assessments":"assessment_id claim_id adjuster_id eligible_amount assessment_date decision decision_reason",
"reserves":"reserve_id claim_id reserve_amount created_date released",
"settlements":"settlement_id claim_id approved_amount payment_status payment_date"}
def date_between(r,a,b): return a+timedelta(days=r.randint(0,max(0,(b-a).days)))
def dump(out,name,rows):
    fields=FIELDS[name].split()
    with (out/"data"/(name+".csv")).open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    (out/"data"/(name+".json")).write_text(json.dumps(rows,indent=2),encoding="utf8")
def run(seed,out):
    r=random.Random(seed); out=Path(out)
    for d in ["data","ground_truth","reports"]: (out/d).mkdir(parents=True,exist_ok=True)
    customers=[dict(customer_id=f"CUS-{i:06}",full_name=f"{r.choice(FIRST)} {r.choice(LAST)}",email=f"customer{i:06}@example.test",city=r.choice(CITIES),created_date=str(date(2022,1,1)+timedelta(days=r.randrange(1460)))) for i in range(1,N_CUSTOMERS+1)]
    adjusters=[dict(adjuster_id=f"ADJ-{i:04}",full_name=f"{r.choice(FIRST)} {r.choice(LAST)}",specialty=r.choice(TYPES)) for i in range(1,31)]
    policies=[]; coverage=[]
    for i in range(1,N_POLICIES+1):
        typ=r.choice(TYPES); start=date_between(r,date(2024,1,1),date(2026,9,1)); end=start+timedelta(days=365); limit=r.choice([100000,250000,500000,1000000,5000000]); ded=r.choice([0,5000,10000,25000]); pid=f"POL-{i:06}"
        policies.append(dict(policy_id=pid,customer_id=customers[i-1]["customer_id"],policy_type=typ,start_date=str(start),end_date=str(end),status="ACTIVE" if end>=date(2026,1,1) else "EXPIRED",coverage_limit=limit,deductible=ded))
        coverage.append(dict(coverage_id=f"COV-{i:06}",policy_id=pid,coverage_type=typ,coverage_limit=limit,exclusions="fraud; intentional_damage"))
    incidents=[]; claims=[]; items=[]; docs=[]; assessments=[]; reserves=[]; settlements=[]; gt=[]
    scenarios=["VALID","MISSING_DOCUMENT","DUPLICATE_CLAIM","OUTSIDE_POLICY_PERIOD","OVER_LIMIT"]
    for i in range(1,N_CLAIMS+1):
        p=policies[r.randrange(len(policies))]; start=date.fromisoformat(p["start_date"]); end=date.fromisoformat(p["end_date"])
        scenario=scenarios[i-1] if i<=5 else "VALID"
        incdate=start-timedelta(days=3) if scenario=="OUTSIDE_POLICY_PERIOD" else date_between(r,max(start,date(2025,1,1)),max(max(start,date(2025,1,1)),min(end,date(2026,10,1))))
        iid=f"INC-{i:06}"; cid=f"CLM-{i:06}"; submitted=incdate+timedelta(days=5); amount=r.randint(15000,200000)
        if scenario=="OVER_LIMIT": amount=p["coverage_limit"]+50000
        incidents.append(dict(incident_id=iid,policy_id=p["policy_id"],incident_date=str(incdate),incident_type=r.choice(["accident","illness","fire","theft","delay"]),description="Synthetic incident"))
        claims.append(dict(claim_id=cid,policy_id=p["policy_id"],incident_id=iid,claim_type=p["policy_type"],submitted_date=str(submitted),claimed_amount=amount,status="SUBMITTED"))
        items.append(dict(claim_item_id=f"ITM-{i:06}",claim_id=cid,description="Eligible expense",quantity=1,unit_cost=amount,line_amount=amount))
        for j,typ in enumerate(["CLAIM_FORM","INCIDENT_EVIDENCE"],1):
            present=not(scenario=="MISSING_DOCUMENT" and typ=="INCIDENT_EVIDENCE")
            docs.append(dict(document_id=f"DOC-{i:06}-{j}",claim_id=cid,document_type=typ,received_date=str(submitted) if present else "",required=True,is_present=present))
        decision,reason="APPROVE","Policy and documents validated"
        if scenario=="MISSING_DOCUMENT": decision,reason="REQUEST_DOCUMENTS","Required incident evidence missing"
        if scenario=="DUPLICATE_CLAIM": decision,reason="MANUAL_REVIEW","Potential duplicate incident"
        if scenario=="OUTSIDE_POLICY_PERIOD": decision,reason="REJECT","Incident outside policy period"
        if scenario=="OVER_LIMIT": decision,reason="MANUAL_REVIEW","Claim amount exceeds coverage limit"
        assessments.append(dict(assessment_id=f"ASM-{i:06}",claim_id=cid,adjuster_id=adjusters[(i-1)%30]["adjuster_id"],eligible_amount=amount,assessment_date=str(submitted+timedelta(days=2)),decision=decision,decision_reason=reason))
        reserves.append(dict(reserve_id=f"RSV-{i:06}",claim_id=cid,reserve_amount=min(amount,p["coverage_limit"]),created_date=str(submitted),released=decision in ["APPROVE","REJECT"]))
        pay=min(max(amount-p["deductible"],0),p["coverage_limit"]) if decision=="APPROVE" else 0
        settlements.append(dict(settlement_id=f"SET-{i:06}",claim_id=cid,approved_amount=pay,payment_status="PENDING" if pay else "NOT_APPROVED",payment_date=""))
        gt.append(dict(claim_id=cid,scenario=scenario,expected_decision=decision,expected_reason=reason))
    tables=locals()
    names=list(FIELDS)
    vals=[customers,adjusters,policies,coverage,incidents,claims,items,docs,assessments,reserves,settlements]
    for name,rows in zip(names,vals): dump(out,name,rows)
    with (out/"ground_truth"/"ground_truth.csv").open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=["claim_id","scenario","expected_decision","expected_reason"]); w.writeheader(); w.writerows(gt)
    (out/"schema.sql").write_text("""PRAGMA foreign_keys=ON;
CREATE TABLE customers(customer_id TEXT PRIMARY KEY,full_name TEXT,email TEXT UNIQUE,city TEXT,created_date TEXT);
CREATE TABLE adjusters(adjuster_id TEXT PRIMARY KEY,full_name TEXT,specialty TEXT);
CREATE TABLE policies(policy_id TEXT PRIMARY KEY,customer_id TEXT REFERENCES customers,policy_type TEXT,start_date TEXT,end_date TEXT,status TEXT,coverage_limit INTEGER,deductible INTEGER);
CREATE TABLE coverage(coverage_id TEXT PRIMARY KEY,policy_id TEXT REFERENCES policies,coverage_type TEXT,coverage_limit INTEGER,exclusions TEXT);
CREATE TABLE incidents(incident_id TEXT PRIMARY KEY,policy_id TEXT REFERENCES policies,incident_date TEXT,incident_type TEXT,description TEXT);
CREATE TABLE claims(claim_id TEXT PRIMARY KEY,policy_id TEXT REFERENCES policies,incident_id TEXT REFERENCES incidents,claim_type TEXT,submitted_date TEXT,claimed_amount INTEGER,status TEXT);
CREATE TABLE claim_items(claim_item_id TEXT PRIMARY KEY,claim_id TEXT REFERENCES claims,description TEXT,quantity INTEGER,unit_cost INTEGER,line_amount INTEGER);
CREATE TABLE documents(document_id TEXT PRIMARY KEY,claim_id TEXT REFERENCES claims,document_type TEXT,received_date TEXT,required INTEGER,is_present INTEGER);
CREATE TABLE assessments(assessment_id TEXT PRIMARY KEY,claim_id TEXT REFERENCES claims,adjuster_id TEXT REFERENCES adjusters,eligible_amount INTEGER,assessment_date TEXT,decision TEXT,decision_reason TEXT);
CREATE TABLE reserves(reserve_id TEXT PRIMARY KEY,claim_id TEXT REFERENCES claims,reserve_amount INTEGER,created_date TEXT,released INTEGER);
CREATE TABLE settlements(settlement_id TEXT PRIMARY KEY,claim_id TEXT REFERENCES claims,approved_amount INTEGER,payment_status TEXT,payment_date TEXT);""",encoding="utf8")
    checks={"policy_customer_fk":all(x["customer_id"] in {c["customer_id"] for c in customers} for x in policies),"claim_policy_fk":all(x["policy_id"] in {p["policy_id"] for p in policies} for x in claims),"claim_incident_fk":all(x["incident_id"] in {a["incident_id"] for a in incidents} for x in claims),"unique_claim_ids":len({x["claim_id"] for x in claims})==len(claims),"nonnegative_amounts":all(x["claimed_amount"]>=0 for x in claims)}
    summary={"seed":seed,"counts":{n:len(v) for n,v in zip(names,vals)},"checks":checks,"all_checks_pass":all(checks.values())}
    (out/"reports"/"validation_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf8")
    (out/"reports"/"validation_summary.txt").write_text(json.dumps(summary,indent=2),encoding="utf8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--seed",type=int,default=SEED); ap.add_argument("--out",default="."); a=ap.parse_args(); run(a.seed,a.out)
