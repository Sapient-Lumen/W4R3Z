# Release go/no-go, source burn-down, and offline drill

**Track:** Shared / Release maintenance

This document adds a maintainer decision layer for v832. It does not replace `docs/162-release-and-ci-evidence-pipeline.md` and does not promote synthetic Example County outputs into live election evidence.

## Purpose

The v831 handoff pack tells a maintainer what changed and what remains synthetic. The v832 go/no-go pack adds an explicit decision boundary:

- GO for a synthetic research release when the archive verifies, generated synthetic outputs are current, and public-boundary language is present.
- NO-GO for live pilot reliance until local configuration, source refresh, live evidence ledgers, external review, and jurisdiction signoff exist.
- NO-GO for certification, current-authority, legal-use, and outcome-proof claims.
- CONDITIONAL for offline verification and operational promotion until a preserved drill transcript exists.

## New files

- `artifacts/registries/release-go-no-go-criteria.csv` — machine-readable decision criteria.
- `tools/release_go_no_go_pack.py` — deterministic report builder.
- `scripts/check_release_go_no_go_pack.py` — release-gate freshness and boundary check.
- `artifacts/checklists/offline-verification-drill-checklist.md` — offline rehearsal checklist.
- `artifacts/reports/release-go-no-go-decision.json` and `artifacts/reports/release-go-no-go-decision.md` — generated decision record.
- `artifacts/reports/source-review-burndown-plan.json` and `artifacts/reports/source-review-burndown-plan.csv` — generated source-review queue.
- `artifacts/reports/offline-verification-drill-plan.md` — generated offline verification drill plan.

## Decision discipline

The pack intentionally separates four questions that are often conflated:

1. Is the archive internally consistent enough to publish as a synthetic research release?
2. Is the stack ready for live pilot reliance?
3. Are the unpinned sources current enough to support voter-facing public-authority statements?
4. Are the outputs usable for certification, legal, or outcome-proof claims?

Only the first question can be answered GO by this archive alone. The others require external or local evidence that is not present here.

## Source burn-down discipline

The source burn-down report turns the unpinned source-review queue into maintainer lanes. Some lanes overlap by design. For example, an official website can also be an accessibility source and an election-authority source. The report labels each lane with a `lane_type` so counts are not silently summed.

Release-blocking lanes are narrow:

- expired unpinned review windows
- missing `review_by` dates

Due-soon lanes are not proof that a source is wrong. They are a scheduling signal that a maintainer should refresh, pin, demote, or replace the reference before relying on it as current authority.

## Offline drill discipline

The offline drill plan is deliberately boring: verify the carrier ZIP, extract with the safe extractor, verify the extracted tree, run the synthetic output pack, run negative controls, and inspect the go/no-go decision. The evidence of a real drill is the preserved transcript, not the existence of this checklist.

## External alignment

This layer keeps the archive aligned with the current standards posture already tracked in `artifacts/registries/standards-crosswalk.csv`: risk-based election infrastructure cybersecurity framing, non-voting election technology assessment as a separate lane, and official AI use as human-reviewed assistance rather than automated rights-affecting determination.

## Non-claims

The v832 go/no-go pack is not live election evidence, not certification, not an outcome proof, not proof of intent or fraud, not a current-authority determination, and not legal advice.
