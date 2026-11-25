import unittest,tempfile,sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run import build,export
class PipelineTest(unittest.TestCase):
 def test_fixture(self):
  with tempfile.TemporaryDirectory() as p:
   p=Path(p); raw=p/'raw';raw.mkdir();out=p/'out'
   h=['Outlet','Date','Time','Net Sales','Tax','Total Amount','Receipt Number','Items','TotalItem','Payment Method','Use Loyalty Card']
   a=['A','01/01/2025','09:00:00','100','10','110','R1','Latte (Ice)','1','Cash','0'];b=['A','01/02/2025','09:00:00','150','15','165','R2','Latte (Ice)','1','Cash','1'];c=['B','01/02/2025','10:00:00','50','5','55','R3','Latte (Ice)','1','Card','0']
   export(raw/'Transactions.csv',h,[a,a,b,c]);export(raw/'Products.csv',['Product ID','Product Name','Variant','Category','Price','Description'],[['1','Latte','Ice','Coffee','100','']]);s=build(raw,out)
   self.assertEqual(s['accepted_orders'],3);self.assertEqual(s['exact_duplicates_removed'],1);self.assertEqual(s['net_sales'],300);self.assertEqual(s['matched_receipts'],3)
   with (out/'01_monthly.csv').open() as f:r=list(csv.DictReader(f));self.assertAlmostEqual(float(r[1]['mom_pct']),100);self.assertAlmostEqual(float(r[1]['volume_effect'])+float(r[1]['aov_effect']),100)
if __name__=='__main__':unittest.main()
