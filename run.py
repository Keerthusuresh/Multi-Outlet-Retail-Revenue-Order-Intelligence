"""Offline POS analytics. Run from project root: python run.py."""
import csv, sqlite3, json, argparse, re
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from collections import Counter
ROOT=Path(__file__).resolve().parent

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); return [{k.strip(): (v or '').strip() for k,v in row.items()} for row in r]
def date(s):
    for fmt in ('%d/%m/%Y','%Y-%m-%d','%d-%m-%Y'):
        try:return datetime.strptime(s,fmt).date()
        except ValueError:pass
    raise ValueError('Unsupported date '+s)
def money(s):
    v=Decimal(s.replace(',','')); 
    if not v.is_finite(): raise ValueError('Nonfinite money')
    return float(v)
def export(path,cols,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(cols);w.writerows(rows)
def build(raw,out):
    out.mkdir(parents=True,exist_ok=True)
    tx=read(raw/'Transactions.csv'); products=read(raw/'Products.csv')
    required={'Outlet','Date','Time','Net Sales','Tax','Total Amount','Receipt Number','Items','TotalItem','Payment Method','Use Loyalty Card'}
    if not tx or not required.issubset(tx[0]):raise ValueError(f'Unexpected transaction schema; missing {required-set(tx[0] if tx else [])}')
    if not products or not {'Product ID','Product Name','Variant','Category','Price','Description'}.issubset(products[0]):raise ValueError('Unexpected product schema')
    rows=[]; seen={}; dup=0; conflicts=[]; rejected=[]; anomalies=[]
    for i,r in enumerate(tx,2):
        try:
            d=date(r['Date']); t=datetime.strptime(r['Time'],'%H:%M:%S').time(); key=r['Receipt Number']; outlet=r['Outlet'];
            if not key or not outlet:raise ValueError('Missing key/outlet')
            if key in seen:
                if seen[key]==r:dup+=1
                else:conflicts.append((i,key,'Conflicting duplicate receipt'))
                continue
            n,tax,total=map(money,(r['Net Sales'],r['Tax'],r['Total Amount'])); items=int(r['TotalItem']);
            if items<0:raise ValueError('Negative item count')
            if abs(n+tax-total)>1:anomalies.append((key,'Net sales + tax differs from total'))
            if n<=0:anomalies.append((key,'Nonpositive net sales; retained'))
            seen[key]=r; rows.append((key,outlet,str(d),t.hour,n,tax,total,items,r['Payment Method'] or 'Unknown',r['Use Loyalty Card'] or 'Unknown',r['Items']))
        except (ValueError,ArithmeticError,KeyError) as e:rejected.append((i,r.get('Receipt Number',''),str(e)))
    export(out/'rejected.csv',['source_row','receipt','reason'],rejected+conflicts)
    if conflicts:raise ValueError('Conflicting receipt keys; inspect rejected.csv before proceeding')
    if not rows:raise ValueError('No valid transactions')
    cols=['receipt','outlet','date','hour','net_sales','tax','total_amount','item_count','payment_method','loyalty','items']
    export(out/'FactOrders.csv',cols,rows);export(out/'DimOutlet.csv',['outlet'],[(x,) for x in sorted({r[1] for r in rows})]);
    start=min(date(r[2]) for r in rows).replace(day=1);end=max(date(r[2]) for r in rows);end=(end.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)
    dates=[]
    while start<=end:dates.append((str(start),start.strftime('%Y-%m'),start.strftime('%A'),start.weekday()+1));start+=timedelta(days=1)
    export(out/'DimDate.csv',['date','month','weekday','weekday_number'],dates)
    export(out/'quality_flags.csv',['receipt','reason'],anomalies)
    # Product mentions: exact normalized catalog labels, not quantities or attributed revenue.
    norm=lambda x:' '.join(x.casefold().split())
    labels={}; productrows=[]
    for p in products:
        pid=p['Product ID']; label=norm(p['Product Name']+(' ('+p['Variant']+')' if p['Variant'] else ''))
        if not pid or not label or pid in {x[0] for x in productrows}:raise ValueError('Invalid/duplicate product ID')
        labels.setdefault(label,[]).append(pid);productrows.append((pid,p['Product Name'],p['Variant'],p['Category'],money(p['Price'])))
    export(out/'DimProduct.csv',['product_id','product_name','variant','category','catalog_price'],productrows)
    mentions=[]; unmatched=[]
    for r in rows:
        # Strict whole-token matching; delimiters are provisional until raw format inspected.
        tokens=re.split(r'\s*[;|\n]\s*|,\s*(?![^()]*\))',r[10]); found=set()
        for token in tokens:
            key=norm(token); ids=labels.get(key,[])
            if len(ids)==1:found.add(ids[0])
            elif key:unmatched.append((r[0],token))
        mentions.extend((r[0],p) for p in sorted(found))
    export(out/'BasketMentions.csv',['receipt','product_id'],mentions);export(out/'unmatched_items.csv',['receipt','raw_token'],unmatched)
    db=sqlite3.connect(out/'retail.sqlite');db.executescript('DROP TABLE IF EXISTS orders; CREATE TABLE orders(receipt TEXT PRIMARY KEY,outlet TEXT,date TEXT,hour INTEGER,net_sales REAL,tax REAL,total_amount REAL,item_count INTEGER,payment_method TEXT,loyalty TEXT,items TEXT);');db.executemany('INSERT INTO orders VALUES(?,?,?,?,?,?,?,?,?,?,?)',rows);db.execute('CREATE INDEX idx_orders_date_outlet ON orders(date,outlet)');db.commit()
    db.executescript('DROP TABLE IF EXISTS basket_mentions; CREATE TABLE basket_mentions(receipt TEXT, product_id TEXT, PRIMARY KEY(receipt,product_id));');db.executemany('INSERT INTO basket_mentions VALUES(?,?)',mentions);db.commit()
    queries=sorted((ROOT/'sql').glob('*.sql'))
    for q in queries:
        cur=db.execute(q.read_text());export(out/(q.stem+'.csv'),[c[0] for c in cur.description],cur.fetchall())
    summary={'source_rows':len(tx),'accepted_orders':len(rows),'exact_duplicates_removed':dup,'rejected_rows':len(rejected),'outlets':len({r[1] for r in rows}),'net_sales':round(sum(r[4] for r in rows),3),'quality_flags':len(anomalies),'product_catalog_rows':len(products),'matched_receipts':len({r[0] for r in mentions}),'unmatched_tokens':len(unmatched),'first_date':min(r[2] for r in rows),'last_date':max(r[2] for r in rows)}
    assert len(tx)==len(rows)+dup+len(rejected)
    assert abs(db.execute('SELECT SUM(net_sales) FROM orders').fetchone()[0]-summary['net_sales'])<0.002
    db.close();(out/'validation.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,default=ROOT/'data/raw');p.add_argument('--out',type=Path,default=ROOT/'output');a=p.parse_args();build(a.raw,a.out)
