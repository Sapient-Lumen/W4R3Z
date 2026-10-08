# CELL-206 — Tail-Risk Report Refactor

Priority: **P0**  
Status: **implemented_refactor**  
Idea: `IDEA-0206`  
Sources: SRC-0127

## Cheap first run

Run tools/tail_risk_report.py and expose lossy probes missing catastrophic-tail/exactness contracts.

## Metrics

- lossy-like count
- tail-ready count
- missing tail contracts

## Required baselines

- existing metric index
- tail-risk report

## Stop condition

If the report finds no missing contracts after hardening, keep as smoke/audit only.
