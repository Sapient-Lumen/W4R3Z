# ADR-0292: Time requirement degraded-time response stays explicit and proof-bundle-bound

- Status: Accepted
- Date: 2026-03-23

## Context

`adrs/ADR-0058-trustworthy-time-posture-by-profile.md` already fixed the large product-shape default:
DeriveBSD does not silently normalize weak time for expiry-sensitive work.

But the archive still left one smaller and more implementation-blocking loophole open in `docs/266-open-questions-and-risk-register.md`:

> when time is degraded, what exactly may a workflow do, and how do we keep that answer out of daemon defaults, ad-hoc UI prompts, or incident folklore?

Without a typed answer, every sensitive workflow can quietly invent its own behavior:

- update verification might continue on a vague “clock seems close enough” guess
- credential issuance or secret release might reuse stale sync state because the last daemon log looked healthy
- support and forensics surfaces might claim a workflow was time-gated without being able to point at the exact proof that justified proceeding under degraded conditions

The archive already has the right ingredients:

- `time-requirement` expresses workflow-specific bounds
- `time-proof-bundle` expresses authenticated source observations and quorum state
- `time.sync.snapshot` expresses current sync posture

What was missing was one explicit boundary connecting them.

## Decision

1. **Degraded-time behavior is part of `time-requirement`, not backend/UI folklore.**
   Every `time-requirement` must now state explicit policy for degraded and unsynced time.

2. **The typed response surface is `time-requirement.degraded_response`.**
   It carries:
   - `on_degraded`
   - `on_unsynced`

3. **Allowed degraded-time actions stay intentionally small.**
   `on_degraded` may be:
   - `deny`
   - `repair-only`
   - `allow-if-proof-fresh`
   - `allow-breakglass-only`

   `on_unsynced` may be:
   - `deny`
   - `repair-only`
   - `allow-breakglass-only`

   Unsynced time does **not** get a normal `allow-if-proof-fresh` path.

4. **`allow-if-proof-fresh` binds to a real `time-proof-bundle`, not to daemon confidence text.**
   When a workflow proceeds under `allow-if-proof-fresh`, the evaluating `time.sync.snapshot` must carry the digest of the `time-proof-bundle` used for that decision.

5. **Fresh proof means policy-matching, in-quorum, and recent.**
   The proof bundle must:
   - match the active `time-source-policy` digest
   - have `agreement.in_quorum = true`
   - be recent enough for the workflow’s `time-requirement.bounds.max_age_seconds`

6. **Unsynced time never proceeds silently.**
   Ordinary workflow behavior under `unsynced` is either denial, repair, or an explicit breakglass lane. “Just continue anyway” is not part of the reviewed contract.

## Consequences

- Sensitive workflows can no longer hide degraded-time behavior in implementation-private conditionals.
- Support and forensics surfaces can point from the workflow requirement to the exact snapshot and proof bundle that justified proceeding.
- A/B/C/D can still choose different defaults, but those defaults now compile down to one explicit contract instead of four families of folklore.
- `time-proof-bundle` becomes useful evidence for controlled degraded operation without becoming the routine support-handoff truth surface.

## Why this is narrow enough

This ADR does **not** settle:

- exact quorum/skew defaults by class
- the final signed offline-time token envelope
- workstation UI wording or alert cadence
- fleet-wide monitor/escalation heuristics when sources disagree for long periods

It only closes the smallest high-leverage boundary that blocks coherent implementation:

- degraded-time response is explicit,
- proof-bundle use is typed,
- and unsynced time cannot silently redefine security-sensitive behavior.
