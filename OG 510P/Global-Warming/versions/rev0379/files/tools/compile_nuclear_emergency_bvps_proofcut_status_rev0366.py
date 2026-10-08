#!/usr/bin/env python3
"""Compile BVPS evidence contract + ledgers into a proofcut status board.

This is intentionally conservative: fixture rows are counted separately and never
credit a real evidence class. Awaiting ledger rows without hashes do not count as
candidate evidence.
"""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REAL_CREDIT_STATES = {'candidate_received','accepted_as_evidence_not_closure','adjudication_pending'}
QUARANTINE_STATES = {'quarantined_needs_review','rejected_or_out_of_scope'}
FORBIDDEN = {'readiness_closure','passed_exercise','certified_ready','local_readiness_proved','alert_success_assumed','protective_action_success_assumed'}

def rows(path: Path) -> list[dict[str,str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return [{k:(v or '').strip() for k,v in row.items()} for row in csv.DictReader(f)]

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--contract', default='cube/nuclear-emergency-bvps-evidence-packet-contract-rev0365.csv')
    ap.add_argument('--real-ledger', default='cube/nuclear-emergency-bvps-chain-of-custody-intake-ledger-rev0365.csv')
    ap.add_argument('--fixture-ledger', default='cube/nuclear-emergency-bvps-evidence-intake-fixture-ledger-rev0365.csv')
    ap.add_argument('--out', default='cube/nuclear-emergency-bvps-proofcut-status-rev0366.csv')
    args=ap.parse_args()
    contracts=rows(ROOT/args.contract)
    real_rows=rows(ROOT/args.real_ledger) if (ROOT/args.real_ledger).exists() else []
    fixture_rows=rows(ROOT/args.fixture_ledger) if (ROOT/args.fixture_ledger).exists() else []
    out=[]
    for i,c in enumerate(contracts,1):
        cls=c.get('artifact_class','')
        rel=[r for r in real_rows if r.get('artifact_class')==cls]
        fix=[r for r in fixture_rows if r.get('artifact_class')==cls]
        real_credit=[]; quarantined=[]; malformed=[]
        for r in rel:
            blob=' '.join(r.values()).lower()
            if any(f in blob for f in FORBIDDEN): malformed.append(r)
            if r.get('fixture_only','no').lower()=='yes':
                continue
            has_hash=bool(r.get('sha256')) and bool(r.get('size_bytes'))
            state=r.get('packet_state','')
            if has_hash and state in REAL_CREDIT_STATES:
                real_credit.append(r)
            elif state in QUARANTINE_STATES:
                quarantined.append(r)
        gate='candidate_evidence_present_no_closure' if real_credit else ('quarantined_or_deficient_no_credit' if quarantined or malformed else 'blocked_no_real_candidate_evidence')
        missing='no' if real_credit else 'yes'
        allowed='candidate evidence may be discussed only with scope, hash, source/custodian, and open-deficiency limits' if real_credit else 'only say awaiting real/anonymized evidence or fixture-only no-credit where applicable'
        next_action='adjudicate without readiness closure' if real_credit else c.get('artifact_description','collect artifact')[:140]
        out.append({
            'proofcut_status_id':f'PCSTAT-0366-{i:03d}',
            'artifact_class':cls,
            'linked_contract_id':c.get('contract_id',''),
            'linked_gap_id':c.get('linked_gap_id',''),
            'minimum_required_metadata':c.get('minimum_required_metadata',''),
            'real_candidate_rows':str(len(real_credit)),
            'fixture_rows':str(len(fix)),
            'quarantined_or_malformed_rows':str(len(quarantined)+len(malformed)),
            'missing_real_evidence':missing,
            'current_gate_state':gate,
            'allowed_statement':allowed,
            'forbidden_statement':'readiness closure; exercise passed; certified ready; alert success assumed; protective action success assumed',
            'claim_effect':'no_readiness_closure',
            'next_action':next_action,
        })
    out_path=ROOT/args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    print(f'PASS proofcut_status rows={len(out)} real_candidate_rows={sum(int(r["real_candidate_rows"]) for r in out)} out={out_path}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
