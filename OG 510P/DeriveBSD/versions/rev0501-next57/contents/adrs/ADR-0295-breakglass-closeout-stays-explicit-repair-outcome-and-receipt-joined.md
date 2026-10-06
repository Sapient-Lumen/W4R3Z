# ADR-0295: breakglass closeout stays explicit, repair-outcome-shaped, and exact receipt-joined

Status: Accepted
Date: 2026-03-23

## Context

The archive already fixes three important emergency-session boundaries:

- breakglass is a lease-shaped authority lane, not a sticky override,
- later ordinary attestation-gated authority must consume a fresh post-breakglass attestation receipt,
- and interactive shell/console sessions carry exact `tty.session.recording` proof starting at `session-open-before-first-prompt`.

But the closeout story still had a hole: a breakglass session could end after a repair attempt, yet the authoritative breakglass receipt had no typed place to say whether the session was observation-only, left a repair waiting for a later confirmation, confirmed a repair, rolled it back, or failed. That invited ticket prose such as “recovery completed” or “fixed during breakglass” to become the real source of truth.

That is too weak for A/B/C/D. Fleet hosts, workstations, general-purpose installs, and factory/regulatory images all need emergency closeout to say exactly what sort of repair state exists without making the shell transcript or operator notes the authoritative artifact.

## Decision

`breakglass.receipt` now carries an explicit `repair_outcome` object.

- `repair_outcome.status` is the authoritative closeout summary for work materially attempted under the breakglass session.
- The first reviewed status set is:
  - `observation-only`
  - `repair-pending-confirmation`
  - `repair-confirmed`
  - `repair-rolled-back`
  - `repair-failed`
- Any non-`observation-only` status must carry exact `repair_outcome.authoritative_receipt_digests`. Those digests point at the authoritative derived-operation receipts (for example `config.receipt`) that prove what actually happened under breakglass.
- Session exit, lease expiry, transcript availability, or ticket notes do **not** count as repair proof.
- `repair_outcome` is closeout truth, not ordinary authority. Ordinary post-breakglass resumption still follows the already-accepted fresh-attestation boundary.

## Consequences

Good:

- emergency closeout no longer hides repair state in prose,
- support bundles and evidence queries can distinguish observation-only sessions from pending-confirm, confirmed, rolled-back, or failed repair attempts,
- and the archive can tell one coherent story from emergency shell to derived repair receipt to later ordinary resumption.

Costs:

- implementations must emit a small extra typed summary when breakglass materially touches state,
- and checkers/examples must keep the exact digest joins honest as canonical examples evolve.

## Follow-on

Still open as implementation detail:

- how UI / CLI closeout should present these statuses in stressful incidents,
- how much post-session rollback guidance should be automated per profile,
- and which classes of derived-operation receipt deserve first-class rendering in support/export tools.
