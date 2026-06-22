#!/usr/bin/env python3
"""Build a single self-contained index.html from the daily-rate CSV.
Embeds data as {date: [per-gram 24K rates in update order]}.
"""
import csv, json
from collections import OrderedDict

data = OrderedDict()
with open('kerala_gold_24k_daily_2yr.csv') as f:
    for r in csv.DictReader(f):
        data.setdefault(r['date'], []).append(int(r['24k_per_gram']))

dates = sorted(data)
MIN, MAX = dates[0], dates[-1]
DATA_JSON = json.dumps(data, separators=(',', ':'))

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kerala Gold Holdings Calculator &middot; 24K</title>
<style>
  :root{
    --bg:#0f1115; --card:#181b22; --line:#2a2f3a; --txt:#e7e9ee;
    --muted:#9aa3b2; --gold:#d9a521; --gold-soft:#f3cf6b; --danger:#e5534b;
    --accent:#1f6feb;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--txt);
    font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  main{max-width:720px;margin:0 auto;padding:24px 16px 64px}
  h1{font-size:22px;margin:0 0 2px;font-weight:650}
  h2{font-size:15px;margin:0 0 14px;color:var(--muted);font-weight:600;
    text-transform:uppercase;letter-spacing:.06em}
  .badge{font-size:12px;background:var(--gold);color:#1a1300;padding:2px 8px;
    border-radius:999px;vertical-align:middle;margin-left:6px;font-weight:700}
  .sub{color:var(--muted);margin:0 0 22px;font-size:13px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;
    padding:18px;margin-bottom:16px}
  .card-head{display:flex;justify-content:space-between;align-items:center}
  .card-head h2{margin-bottom:0}
  .form-row{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;margin-bottom:12px}
  .form-row:last-child{margin-bottom:0}
  label{display:flex;flex-direction:column;gap:6px;font-size:13px;color:var(--muted);flex:1;min-width:140px}
  input,select{background:#0f1218;border:1px solid var(--line);color:var(--txt);
    border-radius:9px;padding:10px 12px;font-size:15px;font-family:inherit}
  input:focus,select:focus{outline:none;border-color:var(--accent)}
  button{background:var(--gold);color:#1a1300;border:0;border-radius:9px;
    padding:11px 18px;font-size:15px;font-weight:650;cursor:pointer;white-space:nowrap}
  button:hover{background:var(--gold-soft)}
  button.ghost{background:transparent;color:var(--muted);border:1px solid var(--line);
    padding:7px 12px;font-size:13px;font-weight:500}
  button.ghost:hover{color:var(--txt);border-color:var(--muted)}
  .indicator{font-size:14px;color:var(--gold-soft);background:#1f1a0d;
    border:1px solid #3a3015;border-radius:9px;padding:10px 12px;margin-bottom:12px}
  .indicator b{color:#fff}
  .error{color:var(--danger);font-size:13px;min-height:18px;margin-top:2px}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th,td{padding:10px 8px;text-align:left;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
  .num{text-align:right;font-variant-numeric:tabular-nums}
  td.num{font-variant-numeric:tabular-nums}
  tbody tr:last-child td{border-bottom:0}
  .del{background:none;color:var(--muted);border:0;font-size:16px;cursor:pointer;padding:2px 6px}
  .del:hover{color:var(--danger);background:none}
  .edit{background:none;color:var(--muted);border:0;font-size:15px;cursor:pointer;padding:2px 6px}
  .edit:hover{color:var(--gold-soft);background:none}
  tr.editing{background:#23210f}
  tr.editing td:first-child{box-shadow:inset 3px 0 0 var(--gold)}
  .empty{color:var(--muted);text-align:center;padding:18px 0;font-size:14px}
  .actions{display:flex;gap:8px;flex-wrap:wrap}
  .io-msg{font-size:13px;color:var(--gold-soft);min-height:18px;margin:0 0 10px}
  .io-msg:empty{margin:0}
  .totals{background:linear-gradient(135deg,#1d1a10,#181b22);border-color:#3a3015}
  .total-grid{display:flex;gap:32px;flex-wrap:wrap}
  .total-grid>div{display:flex;flex-direction:column}
  .big{font-size:30px;font-weight:700;color:var(--gold-soft);font-variant-numeric:tabular-nums}
  .unit{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-top:2px}
  @media(max-width:520px){.total-grid{gap:20px}.big{font-size:24px}}
</style>
</head>
<body>
<main>
  <h1>Kerala Gold Holdings Calculator<span class="badge">24K</span></h1>
  <p class="sub">Weight on hand from purchases, using daily All-Kerala 24K rates (__MIN__ to __MAX__).</p>

  <section class="card">
    <h2>Add purchase</h2>
    <div class="form-row">
      <label>Date
        <input type="date" id="date" min="__MIN__" max="__MAX__" value="__MAX__">
      </label>
      <label>Update
        <select id="update"></select>
      </label>
    </div>
    <div id="indicator" class="indicator"></div>
    <div class="form-row">
      <label>Amount (&#8377;)
        <input type="number" id="amount" min="0" step="any" placeholder="e.g. 1000000" inputmode="decimal">
      </label>
      <button id="add">+ Add purchase</button>
      <button id="cancel" class="ghost" style="display:none">Cancel</button>
    </div>
    <div id="formError" class="error"></div>
  </section>

  <section class="card">
    <div class="card-head">
      <h2>Purchases</h2>
      <div class="actions">
        <button id="import" class="ghost">Import CSV</button>
        <button id="export" class="ghost">Export CSV</button>
        <button id="clear" class="ghost">Clear all</button>
      </div>
    </div>
    <input type="file" id="file" accept=".csv,text/csv" hidden>
    <div id="ioMsg" class="io-msg"></div>
    <table>
      <thead><tr><th>Date</th><th>Upd</th><th class="num">&#8377;/g</th><th class="num">Amount &#8377;</th><th class="num">Grams</th><th></th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
    <p id="empty" class="empty">No purchases yet. Add one above.</p>
  </section>

  <section class="card totals">
    <h2>Total holdings</h2>
    <div class="total-grid">
      <div><span class="big" id="totalGrams">0.000</span><span class="unit">grams</span></div>
      <div><span class="big" id="totalPavan">0.000</span><span class="unit">pavan (8 g)</span></div>
    </div>
  </section>
</main>

<script>
const DATA = __DATA__;
const MIN = "__MIN__", MAX = "__MAX__";
const KEY = "gold_purchases_v1";
const RUPEE = "\\u20B9";

const $ = id => document.getElementById(id);
const dateEl=$("date"), updEl=$("update"), indEl=$("indicator"),
      amtEl=$("amount"), errEl=$("formError"), rowsEl=$("rows"), emptyEl=$("empty"),
      addBtn=$("add"), cancelBtn=$("cancel"), fileEl=$("file"), ioMsgEl=$("ioMsg");

let purchases = load();
let editIndex = null;

function load(){ try{ return JSON.parse(localStorage.getItem(KEY)) || []; }catch(e){ return []; } }
function save(){ localStorage.setItem(KEY, JSON.stringify(purchases)); }
const fmtINR = n => Math.round(n).toLocaleString("en-IN");
const fmtG = n => n.toLocaleString("en-IN",{minimumFractionDigits:3,maximumFractionDigits:3});
const ratesFor = d => DATA[d] || null;

function populateUpdates(){
  const rates = ratesFor(dateEl.value);
  updEl.replaceChildren();
  if(!rates){ updEl.disabled = true; refreshIndicator(); return; }
  updEl.disabled = false;
  rates.forEach((r,i)=>{
    const o=document.createElement("option");
    o.value=i;
    o.textContent = (rates.length>1 ? (i+1)+" of "+rates.length : "1") + "  " + RUPEE + fmtINR(r) + "/g";
    updEl.appendChild(o);
  });
  refreshIndicator();
}

function refreshIndicator(){
  const d=dateEl.value, rates=ratesFor(d);
  indEl.replaceChildren();
  if(!rates){ indEl.textContent = "No rate for this date — pick within the dataset range."; return; }
  const i=+updEl.value||0, r=rates[i];
  const upd = rates.length>1 ? ("update "+(i+1)+" of "+rates.length) : "single rate";
  const bDate=document.createElement("b"); bDate.textContent=d;
  const bRate=document.createElement("b"); bRate.textContent=RUPEE+fmtINR(r)+"/g";
  indEl.append("24K on ", bDate, " ("+upd+"): ", bRate);
}

function resetFormMode(){
  editIndex=null;
  addBtn.textContent="+ Add purchase";
  cancelBtn.style.display="none";
}

function submitForm(){
  errEl.textContent="";
  const d=dateEl.value, rates=ratesFor(d);
  if(!rates){ errEl.textContent="Pick a valid date within the dataset."; return; }
  const i=+updEl.value||0, rate=rates[i];
  const amt=parseFloat(amtEl.value);
  if(!(amt>0)){ errEl.textContent="Enter an amount greater than 0."; return; }
  const rec={date:d, upd:i+1, n:rates.length, rate, amount:amt};
  if(editIndex!==null){ purchases[editIndex]=rec; resetFormMode(); }
  else { purchases.push(rec); }
  save(); render();
  amtEl.value=""; amtEl.focus();
}

function editRow(idx){
  const p=purchases[idx];
  dateEl.value=p.date;
  populateUpdates();
  updEl.value=String(p.upd-1);
  refreshIndicator();
  amtEl.value=p.amount;
  editIndex=idx;
  addBtn.textContent="Save changes";
  cancelBtn.style.display="";
  render();
  amtEl.focus();
  dateEl.closest(".card").scrollIntoView({behavior:"smooth", block:"start"});
}

function cancelEdit(){
  resetFormMode(); amtEl.value=""; errEl.textContent=""; render();
}

function removeRow(idx){
  purchases.splice(idx,1);
  if(editIndex!==null){
    if(editIndex===idx){ resetFormMode(); amtEl.value=""; }
    else if(editIndex>idx){ editIndex--; }
  }
  save(); render();
}

function clearAll(){
  if(!purchases.length) return;
  if(confirm("Remove all purchases?")){ purchases=[]; resetFormMode(); amtEl.value=""; save(); render(); }
}

function showMsg(m){ ioMsgEl.textContent=m; }

function today(){
  const d=new Date(), p=n=>String(n).padStart(2,"0");
  return d.getFullYear()+"-"+p(d.getMonth()+1)+"-"+p(d.getDate());
}

function exportCSV(){
  if(!purchases.length){ showMsg("Nothing to export yet."); return; }
  const header="date,update_no,amount,rate_per_gram,grams";
  const lines=purchases.map(p=>[p.date,p.upd,p.amount,p.rate,(p.amount/p.rate).toFixed(3)].join(","));
  const csv=header+"\\n"+lines.join("\\n")+"\\n";
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="gold-purchases-"+today()+".csv";
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(a.href);
  showMsg("Exported "+purchases.length+" purchase(s).");
}

function parseCSV(text){
  const rows=text.replace(/\\r/g,"").split("\\n").filter(l=>l.trim().length);
  if(!rows.length) return {recs:[],skipped:0};
  const clean=s=>s.trim().replace(/^"|"$/g,"");
  let start=0, di=0, ui=1, ai=2;
  const head=rows[0].split(",").map(s=>clean(s).toLowerCase());
  if(head.includes("date")){
    start=1; di=head.indexOf("date");
    ui=head.indexOf("update_no"); if(ui<0) ui=head.indexOf("update");
    ai=head.indexOf("amount");
  }
  const recs=[]; let skipped=0;
  for(let r=start;r<rows.length;r++){
    const c=rows[r].split(",").map(clean);
    const date=c[di], rates=ratesFor(date);
    const upd=parseInt(c[ui<0?1:ui],10)||1;
    const amt=parseFloat(c[ai<0?2:ai]);
    if(!rates || upd<1 || upd>rates.length || !(amt>0)){ skipped++; continue; }
    recs.push({date, upd, n:rates.length, rate:rates[upd-1], amount:amt});
  }
  return {recs, skipped};
}

function handleFile(file){
  const reader=new FileReader();
  reader.onload=()=>{
    let res;
    try{ res=parseCSV(String(reader.result)); }
    catch(e){ showMsg("Could not read that file."); return; }
    const {recs, skipped}=res;
    if(!recs.length){ showMsg("No valid rows found"+(skipped?(" ("+skipped+" skipped)"):"")+"."); return; }
    if(purchases.length && !confirm("Replace current "+purchases.length+" purchase(s) with "+recs.length+" imported?")) return;
    purchases=recs; resetFormMode(); amtEl.value=""; save(); render();
    showMsg("Imported "+recs.length+" purchase(s)"+(skipped?(", skipped "+skipped+" invalid"):"")+".");
  };
  reader.onerror=()=>showMsg("Could not read that file.");
  reader.readAsText(file);
}

function makeCell(text, isNum){
  const td=document.createElement("td");
  if(isNum) td.className="num";
  td.textContent=text;
  return td;
}

function render(){
  rowsEl.replaceChildren();
  let g=0;
  purchases.forEach((p,idx)=>{
    const grams=p.amount/p.rate; g+=grams;
    const tr=document.createElement("tr");
    tr.appendChild(makeCell(p.date,false));
    tr.appendChild(makeCell(p.n>1 ? p.upd+"/"+p.n : "1", false));
    tr.appendChild(makeCell(fmtINR(p.rate), true));
    tr.appendChild(makeCell(fmtINR(p.amount), true));
    tr.appendChild(makeCell(fmtG(grams), true));
    const tdAct=document.createElement("td");
    tdAct.style.whiteSpace="nowrap";
    const editBtn=document.createElement("button");
    editBtn.className="edit"; editBtn.title="Edit"; editBtn.dataset.edit=idx; editBtn.textContent="\\u270E";
    const delBtn=document.createElement("button");
    delBtn.className="del"; delBtn.title="Remove"; delBtn.dataset.del=idx; delBtn.textContent="\\u2715";
    tdAct.appendChild(editBtn); tdAct.appendChild(delBtn);
    tr.appendChild(tdAct);
    if(idx===editIndex) tr.classList.add("editing");
    rowsEl.appendChild(tr);
  });
  emptyEl.style.display = purchases.length ? "none" : "block";
  $("totalGrams").textContent = fmtG(g);
  $("totalPavan").textContent = fmtG(g/8);
}

dateEl.addEventListener("change", populateUpdates);
updEl.addEventListener("change", refreshIndicator);
addBtn.addEventListener("click", submitForm);
cancelBtn.addEventListener("click", cancelEdit);
amtEl.addEventListener("keydown", e=>{ if(e.key==="Enter") submitForm(); });
$("clear").addEventListener("click", clearAll);
$("export").addEventListener("click", exportCSV);
$("import").addEventListener("click", ()=>{ fileEl.value=""; fileEl.click(); });
fileEl.addEventListener("change", ()=>{ if(fileEl.files[0]) handleFile(fileEl.files[0]); });
rowsEl.addEventListener("click", e=>{
  const del=e.target.closest(".del"); if(del){ removeRow(+del.dataset.del); return; }
  const ed=e.target.closest(".edit"); if(ed){ editRow(+ed.dataset.edit); }
});

populateUpdates();
render();
</script>
</body>
</html>
"""

html = (TEMPLATE
        .replace("__DATA__", DATA_JSON)
        .replace("__MIN__", MIN)
        .replace("__MAX__", MAX))

with open("index.html", "w") as f:
    f.write(html)

print(f"index.html written: {len(html):,} bytes")
print(f"dates: {len(dates)} ({MIN} .. {MAX}); total rate entries: {sum(len(v) for v in data.values())}")
print(f"multi-update days: {sum(1 for v in data.values() if len(v)>1)}")
