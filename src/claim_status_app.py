from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import csv, json

BASE=Path(__file__).resolve().parent.parent
DATA=BASE/"data"
def rows(file):
    with (DATA/file).open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
claims={r["claim_id"].upper():r for r in rows("claims.csv")}
assessments={r["claim_id"].upper():r for r in rows("assessments.csv")}
settlements={r["claim_id"].upper():r for r in rows("settlements.csv")}

PAGE="""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Insurance Claims Dashboard</title><style>
*{box-sizing:border-box}body{margin:0;background:#f4f7fb;font:14px Segoe UI,Arial;color:#17243a}
header{background:linear-gradient(120deg,#14253b,#315efb);color:white;padding:27px max(22px,calc((100% - 1180px)/2))}
.brand{font-size:12px;letter-spacing:2px;text-transform:uppercase;opacity:.8}.title{font-size:29px;font-weight:750;margin:8px 0}.sub{color:#dce7ff}
main{max-width:1180px;margin:26px auto;padding:0 20px}.toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:18px}
h2{font-size:18px;margin:0 0 15px}.muted{color:#64748b;font-size:12px}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin-bottom:18px}.metric,.panel{background:white;border:1px solid #e1e8f0;border-radius:15px;box-shadow:0 7px 24px #10204008}.metric{padding:18px}.metric-label{font-size:12px;color:#64748b}.metric-value{font-size:26px;font-weight:750;margin:8px 0}.metric-note{font-size:12px;color:#64748b}
.content{display:grid;grid-template-columns:1.4fr 1fr;gap:16px}.panel{padding:20px;margin-bottom:16px}
.controls{display:grid;grid-template-columns:1.5fr 1fr 1fr auto;gap:9px;margin-bottom:14px}
input,select{width:100%;min-width:0;padding:11px 12px;border:1px solid #cbd5e1;border-radius:9px;background:white;font-size:13px;color:#17243a}
button{border:0;background:#315efb;color:white;border-radius:9px;padding:11px 15px;font-weight:700;cursor:pointer;white-space:nowrap}button:hover{background:#2449d8}button.secondary{background:#e9efff;color:#2449a5}button.secondary:hover{background:#dce6ff}
.tablewrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:12px}th,td{text-align:left;padding:11px 8px;border-bottom:1px solid #e8edf4;white-space:nowrap}th{color:#64748b;font-weight:600;font-size:11px;text-transform:uppercase}td a{color:#315efb;text-decoration:none;font-weight:700}
.status{display:inline-block;padding:5px 8px;border-radius:20px;font-size:10px;font-weight:750;background:#e0e7ff;color:#3730a3}.status.APPROVE{background:#dcfce7;color:#166534}.status.REJECT{background:#fee2e2;color:#991b1b}.status.MANUAL_REVIEW,.status.REQUEST_DOCUMENTS{background:#fef3c7;color:#92400e}
.bar-row{display:grid;grid-template-columns:115px 1fr 28px;gap:9px;align-items:center;margin:15px 0;font-size:12px}.bar{height:8px;background:#edf1f7;border-radius:99px;overflow:hidden}.fill{height:100%;background:#315efb;border-radius:99px}
.detailgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:16px 0}.detail{padding:12px;background:#f8fafc;border-radius:10px;min-width:0}.detail label{display:block;color:#64748b;font-size:11px;margin-bottom:5px}.detail strong{overflow-wrap:anywhere;font-size:13px}.reason{padding:13px;background:#f8fafc;border-radius:10px;font-size:13px;line-height:1.5}.error{padding:12px;border-radius:9px;background:#fff1f2;color:#991b1b}
.pagination{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:14px}.pagebuttons{display:flex;gap:7px}.pagebuttons button{padding:8px 12px}
.quick{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.quick button{font-size:11px;padding:7px 10px}
footer{text-align:center;color:#94a3b8;font-size:12px;padding:24px}
@media(max-width:900px){.cards{grid-template-columns:repeat(2,1fr)}.content{grid-template-columns:1fr}.controls{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.controls{grid-template-columns:1fr}.metric-value{font-size:22px}.panel{padding:14px}.detailgrid{grid-template-columns:repeat(2,1fr)}.title{font-size:25px}}
</style></head><body>
<header><div class=brand>Insurance Services · Operations</div><div class=title>Claims Dashboard</div><div class=sub>Track claim performance, investigate exceptions, and look up individual claims.</div></header>
<main>
<div class=toolbar><div><h2>Overview</h2><div class=muted>Live metrics from the local generated dataset</div></div><div class=muted id=refresh>Loading…</div></div>
<section class=cards id=metrics></section>
<section class=content>
<div>
<div class=panel><h2>Claims register</h2>
<div class=controls><input id=search placeholder="Search claim ID or policy ID"><select id=status><option value="">All statuses</option></select><select id=type><option value="">All claim types</option></select><button id=export class=secondary>Export CSV</button></div>
<div class=tablewrap><table><thead><tr><th>Claim ID</th><th>Type</th><th>Submitted</th><th>Claimed</th><th>Status</th></tr></thead><tbody id=rows></tbody></table></div>
<div class=pagination><span class=muted id=pageinfo></span><div class=pagebuttons><button class=secondary id=prev>Previous</button><button class=secondary id=next>Next</button></div></div>
</div>
<div class=panel><h2>Claim lookup</h2><div class=controls style="grid-template-columns:1fr auto"><input id=claimid placeholder="Enter claim ID"><button id=check>Check</button></div><div id=claimresult class=muted>Choose a claim from the register or enter its ID.</div></div>
</div>
<div>
<div class=panel><h2>Decision breakdown</h2><div id=breakdown></div></div>
<div class=panel><h2>Claim types</h2><div id=types></div></div>
<div class=panel><h2>Quick filters</h2><div class=muted>Focus on claims that need attention.</div><div class=quick><button class=secondary data-quick="MANUAL_REVIEW">Manual review</button><button class=secondary data-quick="REQUEST_DOCUMENTS">Missing documents</button><button class=secondary data-quick="REJECT">Rejected</button><button class=secondary data-quick="">Show all</button></div></div>
</div></section></main><footer>Local demo dashboard · Synthetic data only</footer>
<script>
let all=[],page=1,perPage=10,filtered=[];
const $=id=>document.getElementById(id);
const money=n=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(Number(n||0));
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const statusClass=s=>(s||'').toUpperCase().replaceAll(' ','_');
function populateSelect(id,values){$(id).innerHTML='<option value="">All '+(id==='status'?'statuses':'claim types')+'</option>'+values.map(v=>`<option value="${safe(v)}">${safe(v.replaceAll('_',' '))}</option>`).join('')}
async function load(){let r=await fetch('/api/dashboard'),d=await r.json();if(!r.ok)return;all=d.records||[];$('refresh').textContent=all.length+' records loaded';
$('metrics').innerHTML=[['Total claims',d.total,'All generated claims'],['Approved',d.decisions.APPROVE||0,'Approved decisions'],['Needs attention',(d.decisions.MANUAL_REVIEW||0)+(d.decisions.REQUEST_DOCUMENTS||0),'Review or documents'],['Total claimed',money(d.total_claimed),'Gross claim amount']].map(x=>`<div class=metric><div class=metric-label>${x[0]}</div><div class=metric-value>${x[1]}</div><div class=metric-note>${x[2]}</div></div>`).join('');
populateSelect('status',Object.keys(d.decisions).sort());populateSelect('type',Object.keys(d.types).sort());
$('breakdown').innerHTML=Object.entries(d.decisions).map(([s,n])=>`<div class=bar-row><span>${safe(s.replaceAll('_',' '))}</span><div class=bar><div class=fill style="width:${d.total?n/d.total*100:0}%"></div></div><b>${n}</b></div>`).join('');
$('types').innerHTML=Object.entries(d.types).map(([s,n])=>`<div class=bar-row><span>${safe(s)}</span><div class=bar><div class=fill style="width:${d.total?n/d.total*100:0}%"></div></div><b>${n}</b></div>`).join('');
applyFilters()}
function applyFilters(){let q=$('search').value.trim().toUpperCase(),s=$('status').value,t=$('type').value;
filtered=all.filter(c=>(!q||c.claim_id.includes(q)||c.policy_id.toUpperCase().includes(q))&&(!s||c.decision===s)&&(!t||c.claim_type===t));
page=1;renderRows()}
function renderRows(){let pages=Math.max(1,Math.ceil(filtered.length/perPage));page=Math.min(page,pages);let slice=filtered.slice((page-1)*perPage,page*perPage);
$('rows').innerHTML=slice.map(c=>`<tr><td><a href="#" data-id="${safe(c.claim_id)}">${safe(c.claim_id)}</a></td><td>${safe(c.claim_type)}</td><td>${safe(c.submitted_date)}</td><td>${money(c.claimed_amount)}</td><td><span class="status ${safe(c.decision)}">${safe(c.decision.replaceAll('_',' '))}</span></td></tr>`).join('')||'<tr><td colspan=5>No matching claims.</td></tr>';
$('pageinfo').textContent=`Page ${page} of ${pages} · ${filtered.length} matching claims`;$('prev').disabled=page<=1;$('next').disabled=page>=pages}
async function lookup(id){id=id.trim();if(!id)return;let box=$('claimresult');box.textContent='Searching…';let r=await fetch('/api/claim?id='+encodeURIComponent(id));let d=await r.json();if(!r.ok){box.innerHTML='<div class=error>'+safe(d.error)+'</div>';return}
let c=d.claim,a=d.assessment||{},s=d.settlement||{};
box.innerHTML=`<div class=detailgrid><div class=detail><label>Status</label><strong><span class="status ${safe(a.decision)}">${safe((a.decision||c.status).replaceAll('_',' '))}</span></strong></div><div class=detail><label>Claim ID</label><strong>${safe(c.claim_id)}</strong></div><div class=detail><label>Claimed</label><strong>${money(c.claimed_amount)}</strong></div><div class=detail><label>Approved</label><strong>${money(s.approved_amount)}</strong></div><div class=detail><label>Policy ID</label><strong>${safe(c.policy_id)}</strong></div><div class=detail><label>Payment</label><strong>${safe((s.payment_status||'—').replaceAll('_',' '))}</strong></div></div><div class=reason><b>Decision details</b><br>${safe(a.decision_reason||'No decision reason available.')}</div>`}
$('check').onclick=()=>lookup($('claimid').value);$('claimid').addEventListener('keydown',e=>{if(e.key==='Enter')lookup(e.target.value)});
$('search').addEventListener('input',applyFilters);$('status').onchange=applyFilters;$('type').onchange=applyFilters;
$('prev').onclick=()=>{page--;renderRows()};$('next').onclick=()=>{page++;renderRows()};
$('rows').addEventListener('click',e=>{let a=e.target.closest('a[data-id]');if(a){e.preventDefault();$('claimid').value=a.dataset.id;lookup(a.dataset.id)}});
document.querySelectorAll('[data-quick]').forEach(b=>b.onclick=()=>{$('status').value=b.dataset.quick;$('type').value='';applyFilters()});
$('export').onclick=()=>{let cols=['claim_id','policy_id','claim_type','submitted_date','claimed_amount','decision'];let csv=[cols.join(','),...filtered.map(c=>cols.map(k=>'"'+String(c[k]??'').replace(/"/g,'""')+'"').join(','))].join('\\r\\n');let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='claims_export.csv';a.click();URL.revokeObjectURL(a.href)};
load();
</script></body></html>"""
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=="/":
            b=PAGE.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
        if u.path=="/api/dashboard":
            decisions={}
            types={}
            total_claimed=0
            enriched=[]
            for cid,c in claims.items():
                a=assessments.get(cid,{})
                decision=a.get("decision","UNKNOWN")
                decisions[decision]=decisions.get(decision,0)+1
                typ=c.get("claim_type","UNKNOWN")
                types[typ]=types.get(typ,0)+1
                total_claimed+=int(c.get("claimed_amount",0) or 0)
                enriched.append({"claim_id":cid,"policy_id":c.get("policy_id",""),"claim_type":typ,"submitted_date":c.get("submitted_date",""),"claimed_amount":c.get("claimed_amount",0),"decision":decision})
            enriched.sort(key=lambda x:x["claim_id"],reverse=True)
            self.reply(200,{"total":len(claims),"total_claimed":total_claimed,"decisions":decisions,"types":types,"records":enriched}); return
        if u.path=="/api/claim":
            cid=parse_qs(u.query).get("id",[""])[0].strip().upper()
            if cid not in claims: self.reply(404,{"error":"Claim ID not found. Please check the ID and try again."}); return
            self.reply(200,{"claim":claims[cid],"assessment":assessments.get(cid,{}),"settlement":settlements.get(cid,{})}); return
        self.reply(404,{"error":"Not found"})
    def reply(self,status,obj):
        b=json.dumps(obj).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self,*args): pass
if __name__=="__main__":
    if not (DATA/"claims.csv").exists(): raise SystemExit("Run python src/main.py first to generate claim data.")
    print("Claim Status Portal: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")
    try: HTTPServer(("127.0.0.1",8000),Handler).serve_forever()
    except KeyboardInterrupt: print("\nStopped.")
