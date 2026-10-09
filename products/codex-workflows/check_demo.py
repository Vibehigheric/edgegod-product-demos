import json, math
from pathlib import Path
p=Path(__file__).resolve().parent/'synthetic.json'
d=json.loads(p.read_text()); rows=[r for r in d['rows'] if r['outcome'] is not None]
assert len({r['id'] for r in d['rows']})==len(d['rows'])
assert all(type(r['probability']) in (float,int) and math.isfinite(r['probability']) and 0<=r['probability']<=1 for r in d['rows'])
assert len(rows)==2 and sum(r['outcome'] for r in rows)==1
assert math.isclose(sum((r['probability']-r['outcome'])**2 for r in rows)/len(rows),.14945)
print('PASS: synthetic fixture 1 WIN, 1 LOSS, 1 PENDING; Brier 0.14945. No live AI or provider call.')
