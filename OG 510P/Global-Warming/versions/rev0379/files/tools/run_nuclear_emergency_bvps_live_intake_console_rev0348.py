#!/usr/bin/env python3
"""Scan BVPS live-intake quarantine lanes and emit rev0348 console CSVs.

This scanner intentionally never assigns closure. It classifies folders/files as
empty, hold, rejected, candidate-for-adjudication, context, or reopen only.
"""
import csv, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUBE = ROOT / 'cube'
BASE = ROOT / 'field-kits' / 'bvps-rev0347' / 'live-intake-quarantine'
GATE = CUBE / 'nuclear-emergency-bvps-live-intake-quarantine-gate-rev0347.csv'
OUT = CUBE / 'nuclear-emergency-bvps-live-intake-console-rev0348.csv'
INDEX = CUBE / 'nuclear-emergency-bvps-live-intake-autoscan-file-index-rev0348.csv'
ROLES = ['incoming','quarantine','accepted_for_adjudication','rejected','retired_synthetic','review']

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def payload_files(folder: Path):
    if not folder.exists():
        return []
    return [p for p in folder.rglob('*') if p.is_file() and p.name != 'README.md']

def main():
    with GATE.open(newline='', encoding='utf-8') as f:
        gate_rows = list(csv.DictReader(f))
    console=[]; index=[]
    for row in gate_rows:
        pkt=row['packet_id']; branch=row['branch_gate']
        counts={}; total=0; missing=[]
        for role in ROLES:
            folder = BASE / pkt / role
            files = payload_files(folder)
            counts[f'{role}_payload_files'] = len(files)
            total += len(files)
            if not folder.exists():
                missing.append(str(folder.relative_to(ROOT)))
            for p in files:
                index.append({'packet_id':pkt,'branch_gate':branch,'lane':role,'relative_path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':sha256(p),'auto_closure_allowed':'no'})
        if missing:
            state='filesystem_broken_missing_folder'; decision='reject_until_folder_repaired'
        elif total == 0:
            state='empty_ready_to_receive_no_evidence'; decision='loss_cap_active_no_payload'
        elif counts['accepted_for_adjudication_payload_files']:
            state='accepted_folder_has_payload_candidate_only'; decision='candidate_for_adjudication_not_closure'
        elif counts['incoming_payload_files'] or counts['quarantine_payload_files']:
            state='payload_present_in_intake_or_quarantine_hold'; decision='hold_no_upgrade'
        elif counts['rejected_payload_files']:
            state='rejected_payload_present_no_credit'; decision='rejected_closure_attempt'
        else:
            state='payload_present_unknown_lane_no_credit'; decision='hold_no_upgrade'
        console.append({'packet_id':pkt,'branch_gate':branch,'packet_name':row['packet_name'],'state':state,'gate_decision':decision,'total_payload_files':total,'loss_cap_active':'yes','auto_closure_allowed':'no','public_claim_effect':'blocks readiness language'})
    with OUT.open('w', newline='', encoding='utf-8') as f:
        fieldnames=list(console[0].keys())
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(console)
    with INDEX.open('w', newline='', encoding='utf-8') as f:
        fieldnames=['packet_id','branch_gate','lane','relative_path','size_bytes','sha256','auto_closure_allowed']
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(index)
    print(f'wrote {OUT} ({len(console)} packets), {INDEX} ({len(index)} payload files)')

if __name__ == '__main__':
    main()
