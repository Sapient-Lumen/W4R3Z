# CELL-322 — Trained Escalation Report Refactor

Priority: P0

Status: audit-refactor

Question: Can the cube clearly separate trained tiny evidence from symbolic/native wind tunnel evidence?

Cheap first run: Run tools/trained_escalation_report.py; check that trained artifacts have separate metrics/guards.

Metrics: trained_current_artifacts, primary_metric_ready, guarded

Required baselines: probe_metric_index, performance_promotion_report, novelty_salience_audit

Stop condition: Keep only if it prevents symbolic toy evidence from being overstated.
