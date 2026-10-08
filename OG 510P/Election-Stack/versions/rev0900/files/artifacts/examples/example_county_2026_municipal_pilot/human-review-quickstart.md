# Example County human-review handoff quickstart

**Synthetic example only. This is not live election evidence.**

Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`  
Archive version: `v900`  
Scenarios covered: `10`  
Human-review modes: `10`  
Retention dispositions: `8`

## Operator command

```bash
python3 tools/human_review_handoff_pack.py --json
```

## What this pack adds

- `human-review-matrix.json` maps each evaluator scenario to recovery IDs, reviewer IDs, public boundary language, and non-claims.
- `reviewer-worksheet-index.csv` lists the reviewer roles and worksheet templates needed for each scenario.
- `scenario-recovery-crosswalk.json` is a JSON copy of the crosswalk for tools that do not want to parse CSV.

## Boundary

This handoff pack helps reviewers preserve evidence, redaction rationale, dissent, and public boundary language. It is not outcome certification, not proof of intent or fraud, not legal advice, and not live deployment evidence.
