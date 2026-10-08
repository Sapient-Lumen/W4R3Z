# Control-plane report

GlassTTY needs one fused operator-facing snapshot that combines runtime health, next-action readiness, support-review debt, support-bundle publication pressure, published-support posture, and compact truth-surface warnings.

## Purpose

`python scripts/control-plane-report.py --pretty` should answer three questions at once:

1. Is the bridge/control plane healthy enough to do useful work?
2. What is the single best next action right now?
3. Which support records/workflow rows deserve review or promotion work next?
4. Are any frozen truth surfaces stale or non-citation-ready right now?

## Inputs

- `doctor.py` output
- `readiness-report.py` output derived from the same doctor report
- `docs/support-records/*.md`
- `support-bundle-queue.py` output derived from `docs/support-bundles/*/*.json`
- `published-support-surface.py` output derived from the queue plus support records
- `truth-surface-warnings.py` output derived from the current truth-surface register
- `support-source-baseline.py` output derived from `SUPPORT-SOURCE-LOCK.json`, support records, and support bundles

## Expected output sections

### health
A compact summary of runtime and readiness truth.
Examples:
- readiness grade
- primary next kind/command
- validation completeness
- latest smoke posture
- best profile summary
- socket/native-host hints

### support overview
A fused summary of support-record posture.
Examples:
- record counts by status
- rollout counts by priority
- workflow-tier counts
- per-surface strongest/weakest rows

### review queue
An explicit queue of the next support-truth rows worth touching.
Each item should make visible:
- surface
- workflow
- lane
- current tier
- rollout priority
- record status
- caveat or blocker summary
- promotion requirement
- next action
- rationale

## Why this matters

Doctor/readiness tell us whether the lab is usable. Support records tell us what the project is allowed to claim. A future implementer should not have to merge those mentally every session.

## Working rule

The control-plane report is not a replacement for doctor, readiness, or support records. It is the fused review surface that makes them operational together.

## Truth-surface warnings
A compact queue of stale, foreign-root, or non-citation-ready truth families.
This is intentionally smaller than the full lineage register and is meant for fast operator attention routing.

## Support-bundle queue
A compact queue of candidate/held/published-ready bundles that tells future sessions whether support evidence is merely named, intentionally blocked, or ready to strengthen support language.


## Support publish gate lane

rev0130 adds a compact publish-gate lane to the control-plane report. This is deliberately narrower than the support-bundle queue: it answers whether a bundle may honestly clear `published-ready` or `published`, not merely whether a bundle exists or is waiting for review.

## Support-source baseline lane

rev0131 adds a compact source-authority lane to the control-plane report. It does not replace the publish gate; it tells the operator whether bundles are still missing required approved source refs or are citing authority outside the named hierarchy before publication pressure is even considered.
