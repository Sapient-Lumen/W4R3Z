#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLOCK=ROOT/'cube/nuclear-emergency-bvps-closure-blocker-board-rev0368.csv'
LEDGER=ROOT/'cube/nuclear-emergency-bvps-request-dispatch-ledger-rev0370.csv'
CONTRACT=ROOT/'cube/nuclear-emergency-bvps-response-intake-contract-rev0371.csv'
PROOFMAP=ROOT/'cube/nuclear-emergency-bvps-response-to-proofcut-map-rev0371.csv'
INV=ROOT/'cube/nuclear-emergency-bvps-active-closure-invariants-rev0371.csv'
GAP=ROOT/'cube/nuclear-emergency-bvps-gap-to-request-map-rev0370.csv'
QUEUE=ROOT/'cube/nuclear-emergency-bvps-public-records-request-queue-rev0368.csv'

def read(p):
    with p.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def fail(msg): print('FAIL '+msg); sys.exit(1)
blocks=read(BLOCK); led=read(LEDGER); con=read(CONTRACT); pm=read(PROOFMAP); inv=read(INV); gap=read(GAP); queue=read(QUEUE)
ledger_text=';'.join(r.get('linked_blockers','') for r in led) + ';' + ';'.join(r.get('blocker_id','') for r in gap) + ';' + ';'.join(r.get('blocks_claim','') for r in queue)
contract_text=';'.join(r.get('linked_blockers','') for r in con)
pm_text=';'.join(r.get('blockers_targeted','') for r in pm)
missing=[]
for b in blocks:
    bid=b['blocker_id']
    if bid not in ledger_text or (bid not in contract_text and bid not in pm_text and 'any' not in contract_text):
        missing.append(bid)
if missing: fail('unmapped_blockers='+','.join(missing))
for r in inv:
    if 'closure' not in r['claim_effect'] and 'claim_frozen' not in r['claim_effect'] and 'open' not in r['claim_effect']:
        fail('bad_invariant_claim_effect='+r['invariant_id'])
for r in con+pm:
    if 'readiness_closure' not in r['claim_effect'] and 'no_' not in r['claim_effect'] and 'partial' not in r['claim_effect']:
        fail('weak_claim_effect')
print(f'PASS response_blocker_saturation_rev0371 blockers={len(blocks)} contracts={len(con)} maps={len(pm)}')
