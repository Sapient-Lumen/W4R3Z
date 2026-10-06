# ADR-0180: Publish-session maintenance triggers stay digest-empty until a dedicated lane exists

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0176 made non-maintenance publish-session authority joins exact:
`trusted-ui`, `policy`, `operator-session`, and `support-session` now each require the matching
digest lane and forbid mixed authority evidence.

That ADR also said `authority.trigger = maintenance` stays reserved for a future dedicated
maintenance-window evidence join.
One smaller but still expensive ambiguity remained:

**what keeps a maintenance-triggered publish session from borrowing**
`consent_receipt_digest`, `policy_decision_digest`, `operator_session_digest`, **or**
`support_session_digest` **as placeholder proof anyway?**

Without one more narrow decision, the archive still teaches that maintenance is reserved in prose
while the schema quietly permits a receipt to say `trigger = maintenance` and smuggle some other
lane's digest under it.
That is exactly the kind of drift that turns a future maintenance lane into folklore instead of a
separate implementable contract.

## Decision

1. `authority.trigger = maintenance` now means the publish-session authority object stays
   **digest-empty** with respect to the existing joined lanes.

2. A maintenance-triggered publish session must therefore not carry any of:
   - `consent_receipt_digest`
   - `policy_decision_digest`
   - `operator_session_digest`
   - `support_session_digest`

3. This ADR does **not** invent the future maintenance-window evidence object.
   It only keeps the reserved trigger from borrowing another lane's digest as a placeholder.

4. Existing lifecycle posture still applies:
   maintenance-triggered sessions remain leased, reboot-cleared, and must carry
   `maintenance-window-end` in `lifecycle.end_conditions`.

## Consequences

- The archive no longer tells two incompatible stories about maintenance: either it has its own
  future authority lane later, or it stays digest-empty now.
- Support/UI/export can treat `maintenance` as intentionally incomplete rather than as a mislabeled
  consent/policy/operator/support receipt.
- Future maintenance work can add a typed evidence join cleanly without having to preserve borrowed
  placeholder semantics.

## Alternatives considered

- **Leave maintenance permissive until the dedicated lane exists.** Rejected because that quietly
  trains implementations to reuse the wrong digest families.
- **Alias maintenance to policy or operator-session for now.** Rejected because those are different
  governance stories and would blur the eventual maintenance contract.
- **Invent the full maintenance evidence lane now.** Rejected as too wide for this round.
