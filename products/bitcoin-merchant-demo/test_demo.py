import json, unittest
from run_demo import ROOT,reconcile,health
class Tests(unittest.TestCase):
    def setUp(self):self.s=json.loads((ROOT/'sample.json').read_text())
    def test_states(self):self.assertEqual([r['status'] for r in reconcile(self.s['invoices'],self.s['payments'])[0]],['PAID','PARTIAL','UNPAID','OVERPAID'])
    def test_exceptions(self):self.assertEqual([r['reason'] for r in reconcile(self.s['invoices'],self.s['payments'])[1]],['DUPLICATE_PAYMENT','UNMATCHED_PAYMENT','UNCONFIRMED'])
    def test_duplicates(self):
        with self.assertRaises(ValueError):reconcile(self.s['invoices']*2,[])
    def test_bad_sats(self):self.assertEqual(reconcile([{'id':'i','due_sats':1}],[{'id':'p','invoice':'i','sats':-1,'confirmed':True}])[1][0]['reason'],'INVALID_SATS')
    def test_alerts(self):self.assertEqual(len(health(self.s['health'])),3)
    def test_healthy(self):self.assertEqual(health({'heartbeat_age_seconds':1,'backup_age_hours':1,'disk_free_percent':50}),[])
if __name__=='__main__':unittest.main()
