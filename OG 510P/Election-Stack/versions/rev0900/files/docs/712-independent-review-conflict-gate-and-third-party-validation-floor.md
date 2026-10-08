# 712 — Independent review conflict gate and third-party-validation floor

**Track:** Shared

This pass adds a gate between **self-tested synthetic release readiness** and any phrase that could sound like independent validation.

The archive already has digest checks, negative controls, custody/provenance gates, redaction gates, accessibility/language gates, and local-pilot no-go logic. That still leaves a live-use failure mode: a maintainer, adopter, or public reader may treat a release that passes its own gates as if it has been independently validated.

v837 closes that gap with a deterministic independent-review/conflict pack.

## Added artifacts

- `artifacts/registries/independent-review-conflict-policy.csv` defines required review-policy rows.
- `tools/independent_review_conflict_pack.py` builds a matrix, burndown, reviewer-role preview, and no-go notice.
- `scripts/check_independent_review_conflict_pack.py` fails the release if the pack drifts or loses non-claim language.
- `artifacts/templates/independent-review-conflict-disclosure-worksheet.md` gives reviewers a field worksheet.
- `artifacts/checklists/independent-review-conflict-checklist.md` gives maintainers a pre-publication checklist.
- `artifacts/reports/independent-review-no-go-notice.md` is the public boundary notice.

## What the gate blocks

The gate blocks live-pilot promotion, third-party-validation language, public-review summaries, challenge-session claims, and legal/admissibility-adjacent claims unless local evidence records exist.

The rows cover reviewer independence, conflict disclosure, qualification and method limits, artifact selection, reproducibility transcript, dissent, public summary approval, privacy and safety constraints, adversarial challenge bounds, legal/records boundary review, reviewer access and chain records, remediation/retest closure, public non-claims, and the independent-review gate itself.

## Boundary

This layer is intentionally conservative. It is **not** third-party validation, not certification, not live-pilot authorization, not current voter instruction, not public-release authorization, not an admissibility opinion, not authorization to test live systems, and not legal advice.

A future live pilot should replace the synthetic rows with named reviewers, scope, conflict disclosures, transcripts, findings, retest records, reviewer-approved public language, and local exceptions.
