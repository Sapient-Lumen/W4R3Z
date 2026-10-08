# Counterparty Artifact Custody and Authority Handoff

rev0201 targets the next live-receipt failure point: the moment an external-looking artifact enters the cube. The archive now has request packets, response records, intake records, import gates, replay reports, recomputation, and class-local firewalls. The remaining practical risk is that a pasted email, screenshot, forwarded copy, redacted snippet, or unsigned institutional note could be treated as live counterparty evidence before raw custody and authority are proven.

The rev0201 rule is strict: **artifact received is not artifact admitted**.

## What this pass adds

The new `counterparty-artifact-custody-record` object sits before response-record creation and before import-gate evaluation. It captures the raw artifact path or locator, hash, size, collection context, sealed/public boundary, authority claim, dependency group, retention state, redaction state, and import readiness. It is designed to accept a real artifact later without weakening the current reliance posture.

The included artifact is deliberately an institutional dry-run text file. It has a real SHA-256 hash and a custody record, but the custody record says the artifact has zero live weight. That is intentional: the point is to test the custody chain, not to pretend a live counterparty has appeared.

## Core rules

**Artifact received is not artifact admitted.** A raw object, screenshot, forwarded email, or copied text cannot create a response record or intake record until custody, hash, locator, authority, dependency, and sealed/public boundary checks pass.

**Hash match is necessary but not sufficient.** A correct hash proves integrity of a captured object. It does not prove live counterparty authority, non-host collection context, receipt-class sufficiency, consent, waiver, WRSR closure, or cross-critical quorum.

**Authority proof is class-specific.** A result-return steward may validate result-return choreography without becoming a first-touch witness, compute-floor witness, representative, RERB reviewer, reserve witness, namespace witness, or anti-capture witness.

**Redacted copies are not raw custody.** Public or subject-readable redactions can support notice, but raw sealed custody must remain available for import and contradiction review.

**Custody failure is a failed gate, not disappearance.** A hash mismatch, authority gap, stale locator, dependency conflict, or redaction-only artifact must be preserved in the public failed-gate summary without exposing sealed details or treating silence as waiver.

## Refactor effect

The receipt stack now has a pre-admission custody layer:

1. request packet,
2. counterparty artifact custody record,
3. non-host response artifact envelope,
4. response record,
5. intake record,
6. actual import gate,
7. live import replay,
8. class-local replay,
9. quorum recomputation and failed-gate publication.

rev0201 also tightens the front-door audit so `docs/README.md` cannot drift behind the active operational head.

## Current reliance posture

No live counterparty artifact exists in this archive. The rev0201 dry-run artifact proves the custody mechanism and the rejection path. It does not change `independent_receipts_present`, does not satisfy result-return, and does not move cross-critical reliance out of stayed posture.

## rev0202 rollback hook

rev0202 adds `docs/30-transition/import-challenge-rollback-and-reliance-reversal.md` and the `receipt-import-challenge-and-rollback-record` object. Custody admission is now paired with a post-admission challenge path: challenge pending means reliance stayed, rollback beats narrative, and authority contest is not waiver.


## rev0203 computed-floor hook

rev0203 adds a generated live-floor snapshot and artifact admission checklist. Custody readiness stays pre-admission until the computed floor, import gate, and challenge/rollback path agree; admission checklist is not admission.
