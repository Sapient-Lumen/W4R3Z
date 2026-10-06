# ADR-0176: Publish-session authority joins follow trigger

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 introduced `net.publish.session` so temporary sharing could stop collapsing into shadow
tunnels or casual public listeners.
ADR-0154 then made those shares bounded and reboot-cleared.
ADR-0159 tightened the `support-session` lane so support-peer publication had to join an exact
`support.session` digest.

One smaller but still expensive ambiguity remained in the rest of the authority surface:

**once `authority.trigger` is typed, what keeps the joined digest fields from mixing authority lanes or
from leaving `trusted-ui`, `policy`, and `operator-session` publication without the exact evidence join
that explains why the share was allowed?**

Without one more narrow decision, a publish session can still say `trigger = trusted-ui` while only
carrying `policy_decision_digest`, can say `trigger = operator-session` without naming the exact
operator session, or can carry multiple authority digests at once and leave support/export surfaces to
guess which lane actually justified the share.

DeriveBSD does not need a larger transaction object here, but it does need the existing authority
lane vocabulary to mean one thing at a time.

## Decision

1. `net.publish.session.authority.trigger` now chooses the **joined authority digest lane** for all
   non-maintenance publish sessions.

2. The matching join is now exact:
   - `trusted-ui` → `consent_receipt_digest`
   - `policy` → `policy_decision_digest`
   - `operator-session` → `operator_session_digest`
   - `support-session` → `support_session_digest`

3. Those digest fields also become inverse evidence:
   - if `consent_receipt_digest` is present, `trigger` must be `trusted-ui`;
   - if `policy_decision_digest` is present, `trigger` must be `policy`;
   - if `operator_session_digest` is present, `trigger` must be `operator-session`;
   - if `support_session_digest` is present, `trigger` must be `support-session`.

4. Mixed authority-digest lanes are out of bounds in the same publish-session authority object.
   A publish session does not carry both consent and policy proof, or both operator-session and
   support-session proof, as parallel justifications.

5. `maintenance` remains reserved for a future dedicated maintenance-window authority evidence join.
   This ADR does not invent that join or let maintenance borrow another lane's digest as a placeholder.

## Consequences

- Trusted-UI publication now has to point at the exact consent receipt that justified it.
- Non-interactive/policy publication now has to point at the exact policy decision instead of vague
  daemon or admin folklore.
- Operator-session publication now has to point at the exact operator session that bounded it.
- Support/export surfaces no longer have to guess which of several digest fields actually explains the
  publish-session authority lane.

## Alternatives considered

- **Leave authority joins free-form beside `authority.trigger`.** Rejected because it keeps the
  authority lane expensive to explain and easy to drift.
- **Require one generic approval digest field for every trigger.** Rejected because it hides which
  existing evidence family actually justified the share.
- **Invent a larger publish-session authority transaction object now.** Rejected as too wide for this
  round.
