# Release Queue Status

_Generated from `release_queue/QUEUE_INDEX.json`, `release_queue/REVIEW_INVENTORY.json`, `release_queue/LATEST_DECISION.json`, and `release_queue/DECISION_INDEX.json`. Do not edit by hand; rerun `python3 -B publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces`._

## Current queue summary

- Candidates: 5
- Hold notes: 61 explicit paper-level holds in queue directories
- Locally reviewed / publication-blocked (`published_ready`): 8
- New post-policy published entries: 7
- Reviewable unpublished papers inventoried: 106
- Standalone-series review-first papers: 29
- Early synthesis foundations (review later): 31
- Late synthesis tail (defer by default): 46

## Current posture

- Latest decision note: `release_queue/decisions/2026.06.18-1154-obschannel-counterexamples-modelbinding-validatorcut-no-publication.md`
- Latest decision heading: Observation-channel counterexamples, model binding, and validator cut — no publication
- Latest decision kind: archive/control-surface pass
- Latest decision publication action: none
- Latest decision summary: Rev0900 (`Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`) repairs a release-adjacent inference that treated a scalar observation probability as an independent erasure channel. Equal per-secret reveal rates do not determine the conditional output law: an explicit three-secret cyclic-reveal mechanism has reveal probability one half for every secret, yet leaks one full bit and permits exact recovery with probability two thirds. The scalar-erasure calculation reports only 0.321928094887 bits and exact recovery 5/12, so it is not a certificate for that mechanism.
- Total recorded decision notes: 243
- Default safe action when compact surfaces disagree: no publication until the trust surfaces agree again.

## Legacy/public distinction

- Legacy already-published work remains public under the Mathematics-era wiki links listed in `published/LEGACY_PUBLISHED_LINKS.md`.
- New releases, when they eventually happen, must use the Anonymity naming rule.

## Next safe kinds of work

1. close one theorem/evidence gap in a standalone source,
2. repair one concrete verifier or compile failure,
3. shrink one duplicated hot-path surface without deleting its source of truth,
4. or record one evidence-backed queue move.

## Additional orientation

- `release_queue/REVIEW_INVENTORY.md` is the source-of-truth paper list for future review turns.
- `publishing/REVIEW_ORDER.md` combines review order and family triage, including why high-churn families should be reviewed later.
- `publishing/CONTROL_SURFACES.md` answers "which file should I trust for this question?" without relying on memory.
- `reports/lifecycle_gate_status.json` answers "which compact surface matters right now?" before the operator widens into longer docs.
- `DATACUBE_TRANSFER_LEDGER.md` answers "did we already steal this idea from another datacube, and why?".

## Fast machine surfaces

- `release_queue/LATEST_DECISION.json` gives the latest decision in a compact machine-readable form.
- `release_queue/DECISION_INDEX.json` gives the cumulative machine-readable decision history.
- `reports/lifecycle_gate_status.json` gives the compact stage-by-stage gate status.
