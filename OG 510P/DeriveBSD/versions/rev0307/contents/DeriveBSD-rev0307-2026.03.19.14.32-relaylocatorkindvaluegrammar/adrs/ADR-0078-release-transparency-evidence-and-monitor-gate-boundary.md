# ADR-0078: Release transparency evidence and monitor-gate boundary

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already had the right ingredients for transparent publication:

- `release.authority.policy` for who may publish,
- `release.publish.receipt` for the threshold-signed publication decision,
- `release.transparency.entry` for append-only publication evidence,
- `log.checkpoint.receipt` for witnessed checkpoint state,
- `transparency.monitor.snapshot` / `transparency.monitor.alert.event` for monitor outputs.

But the boundary between these objects was still too soft.

The archive still allowed three kinds of drift:

1. `release.transparency.entry` still carried a vague `policy_digest` field that could be read as “whatever publish policy mattered here”, while the real authority object is `release.authority.policy`.
2. `release.publish.receipt` still had older top-level transparency joins, which let publication authority and transparency evidence smear together instead of showing one explicit gate summary.
3. checkpoint receipts and monitor snapshots were useful, but their evidence-only status was not yet carried as typed contract material.

That ambiguity is expensive across all four product shapes:

- **A / fleet host** and **D / appliance factory/regulatory** need mirrored, offline-verifiable checkpoint and monitor evidence without making availability of a transparency service the authority boundary.
- **B / workstation** needs explainable release provenance without turning “the log said so” into “ship it”.
- **C / general-purpose OS** needs room for adapters and optional transparency without weakening explicit publish authority.

## Decision

DeriveBSD will keep **release publication authority** and **release transparency evidence** as separate lanes.

The accepted v0 boundary is:

1. `release.publish.receipt` remains the only authoritative publication decision object.
   It is the threshold/role-signed answer to “was this release published under policy?”.

2. `release.transparency.entry` is **publication evidence only**.
   It records that a `release.capsule` was committed to an append-only log under a specific `release.authority.policy`.
   It does not authorize publication.

3. `log.checkpoint.receipt` is **checkpoint evidence only**.
   It records witnessed/signed log state that can be mirrored for offline verification.
   It does not authorize publication.

4. `transparency.monitor.snapshot` is **monitor-state evidence only**.
   It summarizes what a monitor observed (`summary_status`) and which checkpoint receipt it relied on.
   It does not authorize publication.

5. `release.transparency.entry` must bind `authority_policy_digest` (not a generic `policy_digest`).
   This makes the authority relationship explicit and avoids policy-name folklore.

6. `release.publish.receipt` will carry at most one `transparency_verification` summary object.
   That summary may reference:
   - `release.transparency.entry`
   - `log.checkpoint.receipt`
   - `transparency.monitor.snapshot`

   This is the only place where transparency evidence becomes an allow/reject publication gate summary.

7. `release.authority.policy` may require:
   - a transparency entry,
   - bundled proof,
   - checkpoint receipts,
   - and a clean monitor gate.

   But those remain **gating inputs** to publication review, not publication authority themselves.

## Consequences

### Positive

- Release authority stays threshold-bound and explainable from one authoritative receipt.
- Append-only evidence remains portable and useful offline.
- Monitors stay review robots with receipts, not hidden co-signers.
- The archive stops mixing “logged”, “witnessed”, “monitored”, and “authorized”.

### Negative / trade-offs

- Publication review now has one more explicit join object (`transparency_verification`) instead of scattered top-level fields.
- Checkpoint and monitor evidence must be mirrored/bundled deliberately if offline verification is expected.
- Operators who prefer an ambient transparency backend will see more policy wiring than in simpler ecosystems.

## Non-goals

This ADR does **not** decide:

- witness governance defaults,
- monitor operator diversity policy,
- public vs internal log selection,
- or the final verifier UX for degraded transparency paths.

Those remain follow-on policy decisions.

## Why this shape

This is the smallest hard decision that collapses real archive entropy:

- TUF-style authority remains authority,
- transparency stays append-only evidence,
- monitor outputs stay evidence,
- and the publish receipt becomes the single explainable gate summary.
