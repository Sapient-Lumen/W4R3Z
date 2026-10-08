#!/usr/bin/env python3
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
res=list(csv.DictReader(open(ROOT/'cube/nuclear-emergency-bvps-warroom-packout-validator-result-rev0344.csv', newline='', encoding='utf-8')))
packets=list(csv.DictReader(open(ROOT/'cube/nuclear-emergency-bvps-eventday-warroom-integrated-status-rev0344.csv', newline='', encoding='utf-8')))
errs=[]
if len(res)!=54: errs.append(f'expected 54 validator rows, got {len(res)}')
if len(packets)!=60: errs.append(f'expected 60 integrated packet rows, got {len(packets)}')
if any(r['status']!='pass' for r in res): errs.append('failed validator row present')
if any(r['auto_closure']!='no' for r in res): errs.append('auto closure detected')
if errs:
    print('\n'.join('FAIL: '+e for e in errs)); sys.exit(1)
print('pass: rev0344 warroom packout validator')
