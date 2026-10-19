"""EdgeGod Sports Data Audit Kit. Offline, standard-library JSON/CSV auditing."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import html
import io
import json
from pathlib import Path

VERSION = '1.0.0'
IDENTITY = ('sport', 'event_id', 'event_date', 'subject_id', 'team_id', 'opponent_id',
            'market', 'side', 'line', 'period', 'participation_rule', 'ot_rule')
REQUIRED = IDENTITY + ('cutoff', 'feature_asof', 'model_id', 'probability', 'status', 'actual')
STATES = {'FINAL', 'PENDING', 'DNP', 'POSTPONED', 'ABANDONED', 'UNRESOLVED', 'VOID'}
EXCLUDED = STATES - {'FINAL'}

def number(v):
    if isinstance(v, bool):
        raise ValueError('Boolean is not a number')
    try:
        n = Decimal(str(v))
    except InvalidOperation as exc:
        raise ValueError('Invalid number') from exc
    if not n.is_finite():
        raise ValueError('Non-finite number')
    return n

def stamp(v):
    try:
        d = datetime.fromisoformat(str(v).replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('Invalid timestamp') from exc
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError('Timezone required')
    return d

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def load(path):
    raw = Path(path).read_bytes()
    text = raw.decode('utf-8-sig')
    if Path(path).suffix.lower() == '.csv':
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError('Missing or duplicate CSV headers')
        rows = list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in rows):
            raise ValueError('Malformed CSV row width')
    elif Path(path).suffix.lower() == '.json':
        def pairs(items):
            result = {}
            for k, v in items:
                if k in result:
                    raise ValueError('Duplicate JSON key')
                result[k] = v
            return result
        rows = json.loads(text, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON')))
    else:
        raise ValueError('Use .csv or .json')
    if not isinstance(rows, list) or not rows or not all(isinstance(x, dict) for x in rows):
        raise ValueError('Expected a nonempty array of records')
    return raw, rows

def audit(rows, asof=None, max_age_hours=24):
    """Canonical research rows: one model forecast per exact target, not book aliases."""
    asof = stamp(asof) if asof is not None else datetime.now(timezone.utc)
    max_age = number(max_age_hours)
    if max_age < 0:
        raise ValueError('Age threshold must be nonnegative')
    findings = []
    seen = {}
    states = {}
    def add(row, code, severity='ERROR'):
        findings.append(dict(row=row, code=code, severity=severity))
    for i, r in enumerate(rows, 1):
        missing = [k for k in REQUIRED if k not in r]
        if missing:
            add(i, 'MISSING_COLUMNS:' + ','.join(missing))
            continue
        identity_ok = True
        for k in IDENTITY + ('model_id',):
            if r[k] is None or not str(r[k]).strip():
                add(i, 'MISSING_IDENTITY:' + k)
                identity_ok = False
        try:
            date = datetime.strptime(str(r['event_date']), '%Y-%m-%d').date()
            if date.isoformat() != str(r['event_date']):
                raise ValueError()
        except ValueError:
            add(i, 'INVALID_EVENT_DATE')
        if r['team_id'] == r['opponent_id']:
            add(i, 'TEAM_OPPONENT_CONFLICT')
        if r['side'] not in {'OVER', 'UNDER', 'WIN', 'YES', 'NO'}:
            add(i, 'UNSUPPORTED_SIDE')
        if r['period'] not in {'FULL_GAME', 'REGULATION', 'H1', 'H2', 'Q1', 'Q2', 'Q3', 'Q4', 'P1', 'P2', 'P3'}:
            add(i, 'UNSUPPORTED_PERIOD')
        if r['ot_rule'] not in {'INCLUDED', 'EXCLUDED', 'NOT_APPLICABLE'}:
            add(i, 'UNKNOWN_OT_RULE')
        if r['period'] != 'FULL_GAME' and r['ot_rule'] == 'INCLUDED':
            add(i, 'PERIOD_OT_CONFLICT')
        try:
            line = str(number(r['line']).normalize()) if r['line'] != 'NA' else 'NA'
            if r['side'] in {'OVER', 'UNDER'} and line == 'NA':
                add(i, 'LINE_REQUIRED')
        except ValueError:
            add(i, 'INVALID_LINE'); line = str(r['line'])
        try:
            p = number(r['probability'])
            if not 0 <= p <= 1:
                raise ValueError()
        except ValueError:
            add(i, 'INVALID_PROBABILITY')
        state = str(r['status'])
        states[state] = states.get(state, 0) + 1
        if state not in STATES:
            add(i, 'INVALID_STATUS')
        actual_empty = r['actual'] is None or str(r['actual']).strip() == ''
        if state == 'FINAL':
            if actual_empty:
                add(i, 'FINAL_OUTCOME_MISSING')
            else:
                try:
                    number(r['actual'])
                except ValueError:
                    add(i, 'INVALID_ACTUAL')
        elif state in EXCLUDED:
            add(i, 'NOT_RESOLVED:' + state, 'INFO')
            if not actual_empty:
                add(i, 'NONFINAL_ACTUAL_PRESENT', 'WARNING')
        times = {}
        for field in ('cutoff', 'feature_asof'):
            try:
                times[field] = stamp(r[field])
            except ValueError:
                add(i, 'INVALID_TIMESTAMP:' + field)
        if len(times) == 2:
            if times['feature_asof'] > times['cutoff']:
                add(i, 'POST_CUTOFF_FEATURE')
            if times['feature_asof'] > asof:
                add(i, 'FEATURE_IN_FUTURE')
            age = (times['cutoff'] - times['feature_asof']).total_seconds() / 3600
            if age > float(max_age):
                add(i, 'STALE_FEATURE_AT_CUTOFF', 'WARNING')
        if identity_ok:
            key = tuple(line if k == 'line' else str(r[k]).strip() for k in IDENTITY) + (str(r['model_id']),)
            if key in seen:
                add(i, 'DUPLICATE_TARGET')
                old = seen[key]
                if any(str(old[k]) != str(r[k]) for k in ('probability', 'status', 'actual')):
                    add(i, 'CONFLICTING_DUPLICATE')
            else:
                seen[key] = r
    errors = sum(x['severity'] == 'ERROR' for x in findings)
    return dict(version=VERSION, rows=len(rows), errors=errors, status='FAIL' if errors else 'PASS',
                outcome_states=states, findings=findings, asof=asof.isoformat(),
                max_age_hours=float(max_age),
                limits='Structural audit only. No official identity verification, result grading, settlement, source authentication, model accuracy or licensing certification.')

def run(input_path, output, asof=None, max_age_hours=24, expected_sha256=None):
    raw, rows = load(input_path)
    if expected_sha256 and digest(raw) != expected_sha256.lower():
        raise ValueError('INPUT_HASH_MISMATCH')
    result = audit(rows, asof, max_age_hours)
    result['input_sha256'] = digest(raw)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    (out/'audit.json').write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
    trs = ''.join('<tr><td>'+str(x['row'])+'</td><td>'+html.escape(x['severity'])+'</td><td>'+html.escape(x['code'])+'</td></tr>' for x in result['findings'])
    (out/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Sports Data Audit</title><style>body{font:16px system-ui;margin:30px;color:#16334a}td,th{padding:9px;border:1px solid #bbb}table{border-collapse:collapse}</style><h1>Sports Data Audit: '+result['status']+'</h1><p>'+str(result['rows'])+' rows; '+str(result['errors'])+' structural errors.</p><p>'+html.escape(result['limits'])+'</p><table><tr><th>Row</th><th>Severity</th><th>Finding</th></tr>'+trs+'</table><p>Input SHA256: '+result['input_sha256']+'</p></html>', encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}, indent=2))
    if Path(input_path).read_bytes() != raw:
        raise RuntimeError('INPUT_CHANGED_DURING_AUDIT')
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input');p.add_argument('--output', required=True)
    p.add_argument('--asof');p.add_argument('--max-age-hours', type=float, default=24)
    p.add_argument('--expected-sha256')
    a = p.parse_args()
    try:
        r = run(a.input, a.output, a.asof, a.max_age_hours, a.expected_sha256)
    except (ValueError, OSError, RuntimeError) as exc:
        p.exit(2, str(exc)+'\n')
    print(json.dumps({'status':r['status'],'rows':r['rows'],'errors':r['errors']}))
    return 1 if r['errors'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
