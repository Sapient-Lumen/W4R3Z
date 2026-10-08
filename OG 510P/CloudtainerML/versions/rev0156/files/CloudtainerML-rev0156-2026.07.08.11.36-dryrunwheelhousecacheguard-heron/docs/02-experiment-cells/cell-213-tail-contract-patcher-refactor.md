# CELL-213 — Tail Contract Patcher Refactor

Priority: **P0**  
Status: **runnable_refactor**  
Idea: `IDEA-0213`  
Sources: SRC-0127, SRC-0195, SRC-0242

## Cheap first run

Run tools/tail_contract_patcher.py on REV0019 probe outputs before tail_risk_report.py.

## Metrics

- surrogate tail contracts
- direct tail fields
- lossy-like artifacts
- audit pass/fail

## Required baselines

- no patch
- direct-tail outputs
- surrogate contract outputs

## Stop condition

If the patcher reduces transparency, make it report-only.
