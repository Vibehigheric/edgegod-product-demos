import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from audit import audit, load, run, digest

BASE=dict(sport='NFL',event_id='SYNTHETIC-G1',event_date='2026-01-01',subject_id='SYNTHETIC-P1',team_id='SYNTHETIC-A',opponent_id='SYNTHETIC-B',market='receiving_yards',side='OVER',line='49.5',period='FULL_GAME',participation_rule='APPEARANCE_REQUIRED',ot_rule='INCLUDED',cutoff='2026-01-01T18:00:00Z',feature_asof='2026-01-01T17:00:00Z',model_id='SYNTHETIC-M1',probability=.6,status='FINAL',actual=60)
ASOF='2026-01-02T00:00:00Z'
def codes(rows):return [x['code'] for x in audit(rows,ASOF)['findings']]

class AuditTests(unittest.TestCase):
    def row(self,**kw):return dict(BASE,**kw)
    def test_clean(self):self.assertEqual(audit([BASE],ASOF)['status'],'PASS')
    def test_published_example_hashes(self):
        e=Path(__file__).parent/'examples';report=e/'problem-report'
        saved=json.loads((report/'audit.json').read_text())
        self.assertEqual(saved['input_sha256'],digest((e/'problems.csv').read_bytes()))
        for name,h in json.loads((report/'manifest.json').read_text()).items():
            self.assertEqual(h,digest((report/name).read_bytes()))
    def test_duplicates_numeric_line(self):self.assertIn('DUPLICATE_TARGET',codes([BASE,self.row(line=49.50)]))
    def test_conflict(self):self.assertIn('CONFLICTING_DUPLICATE',codes([BASE,self.row(actual=2)]))
    def test_models_separate(self):self.assertNotIn('DUPLICATE_TARGET',codes([BASE,self.row(model_id='OTHER')]))
    def test_periods_separate(self):self.assertNotIn('DUPLICATE_TARGET',codes([BASE,self.row(period='H1',ot_rule='EXCLUDED')]))
    def test_missing_identity(self):self.assertIn('MISSING_IDENTITY:subject_id',codes([self.row(subject_id='')]))
    def test_final_missing(self):self.assertIn('FINAL_OUTCOME_MISSING',codes([self.row(actual=None)]))
    def test_zero_final_valid(self):self.assertEqual(codes([self.row(actual=0)]),[])
    def test_dnp_not_zero_or_loss(self):self.assertEqual(codes([self.row(status='DNP',actual=None)]),['NOT_RESOLVED:DNP'])
    def test_nonfinal_actual(self):self.assertIn('NONFINAL_ACTUAL_PRESENT',codes([self.row(status='PENDING',actual=0)]))
    def test_probability_invalid(self):
        for v in [-.1,1.1,'NaN','Infinity',True,None]:self.assertIn('INVALID_PROBABILITY',codes([self.row(probability=v)]))
    def test_timezone_required(self):self.assertIn('INVALID_TIMESTAMP:cutoff',codes([self.row(cutoff='2026-01-01T18:00:00')]))
    def test_offset_comparison(self):self.assertNotIn('POST_CUTOFF_FEATURE',codes([self.row(feature_asof='2026-01-01T12:00:00-05:00')]))
    def test_leakage(self):self.assertIn('POST_CUTOFF_FEATURE',codes([self.row(feature_asof='2026-01-01T19:00:00Z')]))
    def test_stale(self):self.assertIn('STALE_FEATURE_AT_CUTOFF',codes([self.row(feature_asof='2025-12-29T00:00:00Z')]))
    def test_ot_conflict(self):self.assertIn('PERIOD_OT_CONFLICT',codes([self.row(period='REGULATION')]))
    def test_same_teams(self):self.assertIn('TEAM_OPPONENT_CONFLICT',codes([self.row(opponent_id=BASE['team_id'])]))
    def test_missing_column(self):
        r=copy.copy(BASE);del r['market'];self.assertTrue(codes([r])[0].startswith('MISSING_COLUMNS'))
    def test_bad_date_and_line(self):
        c=codes([self.row(event_date='2026-02-30',line='abc')]);self.assertIn('INVALID_EVENT_DATE',c);self.assertIn('INVALID_LINE',c)
    def test_immutable_report_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.json';p.write_text(json.dumps([BASE]));before=p.read_bytes();out=Path(d)/'result'
            r=run(p,out,ASOF,expected_sha256=digest(before));self.assertEqual(before,p.read_bytes());self.assertTrue((out/'report.html').exists())
            with self.assertRaises(FileExistsError):run(p,out,ASOF)
            with self.assertRaises(ValueError):run(p,Path(d)/'bad',ASOF,expected_sha256='0'*64)
    def test_bad_json_and_csv(self):
        with tempfile.TemporaryDirectory() as d:
            for name,body in [('a.json','[{"x":1,"x":2}]'),('b.json','[NaN]'),('a.csv','x,x\n1,2\n'),('b.csv','x,y\n1\n')]:
                p=Path(d)/name;p.write_text(body)
                with self.assertRaises(ValueError):load(p)
    def test_cli_failure_exit_and_artifact(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.json';p.write_text(json.dumps([self.row(probability=9)]));out=Path(d)/'out'
            r=subprocess.run([sys.executable,str(Path(__file__).with_name('audit.py')),str(p),'--output',str(out),'--asof',ASOF],capture_output=True)
            self.assertEqual(r.returncode,1);self.assertEqual(json.loads((out/'audit.json').read_text())['status'],'FAIL')

if __name__=='__main__':unittest.main()
