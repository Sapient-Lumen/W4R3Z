#!/usr/bin/env python3
"""One-shot BVPS evidence-intake live watchdog for rev0361.
It checks the static package surfaces and prints capture-ready / claim-frozen status only.
It does not run in the background and never emits readiness closure.
"""
import csv, json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REV='rev0361'

def read_csv(path):
    with open(path,newline='',encoding='utf-8') as f: return list(csv.DictReader(f))

def main():
    checks=[]
    checks.append(('manifest_rev', json.load(open(ROOT/'manifest.json',encoding='utf-8')).get('revision')==REV))
    checks.append(('cube_manifest_rev', json.load(open(ROOT/'cube/manifest.json',encoding='utf-8')).get('revision')==REV))
    checks.append(('watchdog_validator_exists', (ROOT/'cube/nuclear-emergency-bvps-watchdog-validator-result-rev0361.csv').exists()))
    checks.append(('loss_caps_60', len(read_csv(ROOT/'cube/nuclear-emergency-bvps-watchdog-loss-cap-board-rev0361.csv'))==60))
    checks.append(('claim_freeze_20', len(read_csv(ROOT/'cube/nuclear-emergency-bvps-watchdog-claim-freeze-board-rev0361.csv'))==20))
    db=ROOT/'cube/datacube-rev0361-emergency.sqlite'
    ok=False
    if db.exists():
        con=sqlite3.connect(db); ok=con.execute('pragma integrity_check').fetchone()[0]=='ok'; con.close()
    checks.append(('sqlite_integrity_ok', ok))
    result='capture-ready / claim-frozen' if all(v for _,v in checks) else 'hold / repair required'
    print(json.dumps({'revision':REV,'result':result,'checks':checks,'readiness_claim':'none'}, indent=2))
    return 0 if all(v for _,v in checks) else 2
if __name__=='__main__':
    raise SystemExit(main())
