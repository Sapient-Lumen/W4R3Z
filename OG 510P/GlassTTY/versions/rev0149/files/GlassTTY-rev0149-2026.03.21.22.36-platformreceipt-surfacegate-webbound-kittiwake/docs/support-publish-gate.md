# Support publish gate

The support-bundle queue tells us **what named evidence objects exist**.
The published-support surface tells us **what is citable now**.
The support publish gate owns the narrow boundary between those two truths.

## Why this exists

A held or candidate bundle is already useful.
It means GlassTTY gathered coherent evidence without pretending publication is justified.

What was still too soft before rev0130 was the actual promotion boundary.
A bundle could be moved into `published-ready` or `published` by directory motion alone.
That made it too easy to confuse:

- queue presence,
- review intent,
- current support-record posture,
- direct live workflow evidence,
- and citable publication state.

## Current rule

A bundle should clear the publish gate only when all of the following are true:

- the support-bundle manifest itself is valid
- the transition is allowed by the explicit queue-state graph
- the support record for that surface is publishable (`backfilled-from-evidence` or `current`)
- `claim_scope.publication_blockers` is empty
- `publication_decision.why` is empty
- the bundle contains direct live / route / history / workflow evidence artifacts instead of only repo-current prose or fixture references
- the bundle cites the required approved source refs for that surface and does not cite unknown or non-approved authority keys
- the support-source lock review is current and the required source refs are not stale under the current review-age policy

For `published`, not only `published-ready`, the bundle must also carry a **current publish guard** proving that the support record, support-surface snapshot, published-support surface, and revision receipt still match the heads it was reviewed against.

## Expected-head guard

The publish guard is GlassTTY's compact compare-and-set boundary for support publication.
It records the hashes of the heads the bundle was reviewed against.
If those heads drift later, GlassTTY should surface that the bundle is stale against current truth rather than silently treating it as still-current publication authority.

## Output surfaces

- `python scripts/support-publish-gate.py --pretty`
- `python scripts/support-publish-gate.py capture --output-dir validation/latest/support-publish-gate`
- `python scripts/support-publish-gate.py write-root`
- rooted snapshot: `SUPPORT-PUBLISH-GATE.json`

## Transition discipline

`python scripts/support-bundle-transition.py ...` now fails closed for moves into `published-ready` or `published` unless the gate passes or the operator explicitly uses `--allow-failed-gate`.
Each transition also emits a receipt into `validation/latest/support-bundle-transition/` plus append-only transition history.

## Current doctrine

This is intentionally stricter than the queue itself.
A queue tells future sessions what is under review.
A publish gate tells future sessions what may honestly become stronger support language **right now**.

rev0132 keeps the live-evidence boundary and adds a freshness boundary on top of source authority: a bundle may not clear the gate with good captures and nominally approved refs alone if the lock or required refs are stale under the repo's review policy.
