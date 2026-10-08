# CELL-309 — Operator/Router Family Report Refactor

Priority: **P0**  
Status: `audit-refactor`

## Why this exists
tools/operator_route_report.py scans current operator/router/ranker/MoE artifacts and emits a family-specific readiness surface.

## Metrics
- fresh_family_artifacts
- readiness
- cost_fields
- failure_fields
- winner_diversity

## Required baselines
- performance_hardening_report
- native_phase_readiness_report
- screen_regret_report

## Stop condition
If it does not help choose trained escalation, delete it.
