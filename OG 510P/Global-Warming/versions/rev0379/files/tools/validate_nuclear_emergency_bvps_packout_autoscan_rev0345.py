#!/usr/bin/env python3
import argparse,csv
from pathlib import Path

def read_csv(p):
    with open(p,newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); a=ap.parse_args(); root=Path(a.root)
    rows=read_csv(root/'cube/nuclear-emergency-bvps-packout-autoscan-validator-result-rev0345.csv')
    bad=[r for r in rows if r.get('status')!='pass' or r.get('auto_closure')=='yes']
    print('rows=%d failures=%d' % (len(rows),len(bad)))
    raise SystemExit(1 if bad else 0)
if __name__=='__main__': main()
