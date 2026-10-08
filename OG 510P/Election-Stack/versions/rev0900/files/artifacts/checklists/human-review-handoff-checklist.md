# Human review handoff checklist

**Track:** Shared / Track A pilot readiness

Use this checklist when a verifier, monitor, reviewer, or public-facing operator cannot safely say only "pass" or "fail".

1. Identify the trigger in `artifacts/registries/human-review-handoff-playbook.csv`.
2. Preserve the minimum evidence named in `artifacts/registries/evidence-retention-disposition.csv`.
3. Copy the public boundary sentence before drafting any longer statement.
4. Record reviewer disagreement instead of flattening it into a single narrative.
5. Apply the redaction floor before publication.
6. Escalate if the issue affects eligibility, deadlines, ballot content, public safety, trust roots, or result artifacts.
7. Carry forward the non-claims: not outcome certification, not proof of intent or fraud, not legal advice.

Run:

```bash
python3 scripts/check_human_review_handoff_playbook.py
python3 scripts/check_evidence_retention_disposition.py
python3 scripts/check_scenario_recovery_crosswalk.py
python3 tools/human_review_handoff_pack.py --json
```
