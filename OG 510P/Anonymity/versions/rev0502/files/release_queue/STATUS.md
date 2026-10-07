# Release Queue Status

_Generated from `release_queue/QUEUE_INDEX.json`, `release_queue/REVIEW_INVENTORY.json`, `release_queue/LATEST_DECISION.json`, and `release_queue/DECISION_INDEX.json`. Do not edit by hand; rerun `python3 publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces`._

## Current queue summary

- Candidates: 6
- Hold notes: 52 explicit paper-level holds in queue directories
- Published-ready: 22
- New post-policy published entries: 0
- Reviewable unpublished papers inventoried: 105
- Standalone-series review-first papers: 29
- Early synthesis foundations (review later): 31
- Late synthesis tail (defer by default): 45

## Current posture

- Latest decision note: `release_queue/decisions/2026.03.22-0213-bossfight-c-verifierbundle-cutover-no-publication.md`
- Latest decision heading: 2026.03.22 — Boss Fight~C verifier-bundle card cutover and reopen ladder (no publication)
- Latest decision kind: archive/control-surface pass
- Latest decision publication action: none
- Latest decision summary: This drafting pass tightens the replayable verifier-bundle companion itself rather than widening the repeated-use accountant root, the practical anonymous-DHT dial sheet, the optional evidence-table addendum, the evaluator-notarization layer, the claim-object dossier, or the release-lineage receipts. The goal is to let later terse Anonymous-DHT papers cite one exact verdict about when the same public verifier-bundle card still names the live replay contract, when reusing the same primal/dual numbers after checker-version or schema drift forces a new card, and which neighboring paper owns the next widening step. The pass does not change publication state.
- Total recorded decision notes: 264
- Default safe action when compact surfaces disagree: no publication until the trust surfaces agree again.

## Legacy/public distinction

- Legacy already-published work remains public under the Mathematics-era wiki links listed in `published/LEGACY_PUBLISHED_LINKS.md`.
- New releases, when they eventually happen, must use the Anonymity naming rule.

## Next safe kinds of work

1. review one paper from the Candidate queue or one hold rationale from the synthesis tail,
2. strengthen a trust / integrity / transfer surface,
3. refine a crosswalk or release-process surface,
4. or record one cautious queue move with a new written decision note.

## Additional orientation

- `release_queue/REVIEW_INVENTORY.md` is the source-of-truth paper list for future review turns.
- `publishing/FAMILY_TRIAGE.md` explains why some families should be reviewed later even if they are important internally.
- `publishing/CONTROL_SURFACES.md` answers "which file should I trust for this question?" without relying on memory.
- `reports/lifecycle_gate_status.json` answers "which compact surface matters right now?" before the operator widens into longer docs.
- `DATACUBE_TRANSFER_LEDGER.md` answers "did we already steal this idea from another datacube, and why?".

## Fast machine surfaces

- `release_queue/LATEST_DECISION.json` gives the latest decision in a compact machine-readable form.
- `release_queue/DECISION_INDEX.json` gives the cumulative machine-readable decision history.
- `reports/lifecycle_gate_status.json` gives the compact stage-by-stage gate status.
