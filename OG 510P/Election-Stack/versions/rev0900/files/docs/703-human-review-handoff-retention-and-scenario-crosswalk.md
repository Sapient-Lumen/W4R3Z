# 703 — Human review handoff, retention, and scenario crosswalk

**Track:** Shared / Track A pilot readiness  
**Release:** v828 (2026-05-22)

## Purpose

v827 made failure handoff public-language-bounded. v828 adds the missing human handoff layer: who reviews a failure, what minimum evidence they preserve, what they redact, how they preserve disagreement, and which non-claims must travel with the public explanation.

## Added surfaces

- `artifacts/registries/human-review-handoff-playbook.csv` — reviewer roles, triggers, required inputs, escalation conditions, public boundary sentences, retention actions, and non-claims.
- `artifacts/registries/evidence-retention-disposition.csv` — minimum preserved fields and redaction floors for packet, notice, verifier, monitoring, safety, AI, key/witness, and source-review evidence families.
- `artifacts/registries/scenario-recovery-crosswalk.csv` — maps every evaluator scenario to trust-recovery IDs and human-review IDs.
- `tools/human_review_handoff_pack.py` — derives the synthetic Example County human-review output pack.
- `artifacts/examples/example_county_2026_municipal_pilot/human-review-matrix.json` — machine-readable reviewer handoff matrix.
- `artifacts/examples/example_county_2026_municipal_pilot/reviewer-worksheet-index.csv` — per-scenario worksheet index.
- `artifacts/examples/example_county_2026_municipal_pilot/scenario-recovery-crosswalk.json` — JSON copy of the crosswalk for tools.
- `artifacts/examples/example_county_2026_municipal_pilot/human-review-quickstart.md` — short operator-facing boundary and commands.

## New release-gate checks

- `scripts/check_human_review_handoff_playbook.py`
- `scripts/check_evidence_retention_disposition.py`
- `scripts/check_scenario_recovery_crosswalk.py`
- `scripts/check_human_review_output_pack.py`

## Non-claim boundary

These additions do not create live deployment evidence, do not certify outcomes, do not prove intent or fraud, and do not provide legal advice. They make review, redaction, disagreement, and retention auditable so a pilot can fail or escalate without improvising public claims.

## Operator loop

```bash
python3 scripts/check_human_review_handoff_playbook.py
python3 scripts/check_evidence_retention_disposition.py
python3 scripts/check_scenario_recovery_crosswalk.py
python3 tools/human_review_handoff_pack.py --write
python3 scripts/check_human_review_output_pack.py
```
