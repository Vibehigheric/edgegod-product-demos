"""Synthetic merchant report. No network, secrets, funds or live integrations."""
import csv, hashlib, html, json
from pathlib import Path
ROOT=Path(__file__).parent
def reconcile(invoices,payments):
    ids=[i['id'] for i in invoices]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate invoice IDs')
    totals={}; seen=set(); exceptions=[]
    for p in payments:
        reason=None
        if p['id'] in seen: reason='DUPLICATE_PAYMENT'
        elif p['invoice'] not in ids: reason='UNMATCHED_PAYMENT'
        elif type(p['sats']) is not int or p['sats']<=0: reason='INVALID_SATS'
        elif p['confirmed'] is not True: reason='UNCONFIRMED'
        seen.add(p['id'])
        if reason: exceptions.append({'id':p['id'],'reason':reason})
        else: totals[p['invoice']]=totals.get(p['invoice'],0)+p['sats']
    rows=[]
    for i in invoices:
        due=i['due_sats']
        if type(due) is not int or due<=0: raise ValueError('Invalid invoice amount')
        got=totals.get(i['id'],0)
        state='UNPAID' if got==0 else 'PARTIAL' if got<due else 'PAID' if got==due else 'OVERPAID'
        rows.append({**i,'confirmed_sats':got,'status':state})
    return rows,exceptions
def health(m):
    return [label for key,limit,label in [('heartbeat_age_seconds',120,'STALE_HEARTBEAT'),('backup_age_hours',24,'BACKUP_STALE')] if m[key]>limit]+(['LOW_DISK'] if m['disk_free_percent']<15 else [])
def main():
    s=json.loads((ROOT/'sample.json').read_text()); rows,exceptions=reconcile(s['invoices'],s['payments']); alerts=health(s['health'])
    report={'mode':'SYNTHETIC_DEMO_ONLY','rows':rows,'exceptions':exceptions,'health_alerts':alerts,'telegram':{'mode':'DRY_RUN','sent':False,'message':', '.join(alerts)},'limits':['No live BTCPay, Telegram, node or wallet connection','Export flags are not independent blockchain verification','No tax, security or uptime certification; no subscription activated']}
    out=ROOT/'output';out.mkdir(exist_ok=True)
    with (out/'daily.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'report.json').write_text(json.dumps(report,indent=2))
    (ROOT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>EdgeGod Merchant Demo</title><style>body{max-width:1000px;margin:auto;padding:25px;background:#10231d;color:#edf5ef;font:16px/1.6 system-ui}h1,a{color:#c8ee86}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#1b352b;padding:20px}@media print{body{background:white;color:black}}</style><a href="../../demo.html">All demos</a><h1>Bitcoin Merchant Reporting & Health Monitor</h1><p>SYNTHETIC DEMO ONLY — NO FUNDS — TELEGRAM DRY RUN</p><p>Invoice reconciliation with integer satoshis. No live exchange rates.</p><pre>'+html.escape(json.dumps(report,indent=2))+'</pre><a href="output/daily.csv">Sample daily CSV</a><p>Print → Save as PDF for a print copy. No generated PDF supplied.</p></html>',encoding='utf8')
    files=['run_demo.py','sample.json','index.html','output/daily.csv','output/report.json']
    (out/'manifest.json').write_text(json.dumps({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},indent=2))
    print('Generated synthetic HTML, CSV, JSON and integrity manifest')
if __name__=='__main__':main()
