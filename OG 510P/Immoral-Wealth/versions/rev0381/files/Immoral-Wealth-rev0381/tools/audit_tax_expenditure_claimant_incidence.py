#!/usr/bin/env python3
"""Audit rev0369 tax-expenditure claimant-incidence migration."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
REV="rev0369"
CASE="tax-expenditure-hidden-public-balance-sheet-rev0319"
ledger=json.loads((ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json").read_text())
rows=[r for r in ledger.get("verified_claim_edges",[]) if r.get("case_id")==CASE]
required={"S574","S575","S576","S577"}
seen={sid for r in rows for sid in r.get("source_ids",[])}
problems=[]
if len(rows)<16: problems.append(f"expected at least 16 tax-expenditure rows, saw {len(rows)}")
if not required.issubset(seen): problems.append(f"missing sources {sorted(required-seen)}")
if any(r.get("verification_status")=="certified_current" for r in rows): problems.append("tax expenditure row incorrectly certified")
score=json.loads((ROOT/"cases"/"tax-expenditure-hidden-public-balance-sheet-rev0319-scoreboard.json").read_text())
if score.get("certification_gates",{}).get("gate_20_public_balance_sheet",{}).get("status") != "blocked": problems.append("gate_20 not blocked")
print(f"rev0369_tax_expenditure_edges={len(rows)}")
print(f"source_ids={sorted(seen & required)}")
print(f"problem_count={len(problems)}")
for p in problems: print("PROBLEM:", p)
if problems: sys.exit(1)
