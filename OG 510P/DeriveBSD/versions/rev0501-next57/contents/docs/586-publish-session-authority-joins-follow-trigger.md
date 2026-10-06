# Publish-session authority joins follow trigger

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says temporary sharing is leased, bounded, and evidence-shaped.
The archive also already fixed the support-peer lane so `support-session` sharing must join an exact
`support.session` digest.

One smaller ambiguity still remained in the rest of the authority object.

> once `authority.trigger` is typed, what keeps the joined digest fields from mixing authority lanes or
> from leaving `trusted-ui`, `policy`, and `operator-session` publication without the exact digest that
> explains why the share was allowed?

If the archive leaves that open, one receipt can say `trigger = trusted-ui` while only carrying
`policy_decision_digest`, or can carry multiple authority digests at once and force support/UI/export
to guess which lane actually justified the share.

See `adrs/ADR-0176-publish-session-authority-joins-follow-trigger.md`.

## Boundary

Publish-session authority joins now follow **`authority.trigger` exactly**.

### Non-maintenance trigger lanes have one matching join

For publish sessions that use the existing non-maintenance authority triggers, the exact joined digest is
now fixed:

- `trusted-ui` → `consent_receipt_digest`
- `policy` → `policy_decision_digest`
- `operator-session` → `operator_session_digest`
- `support-session` → `support_session_digest`

That keeps the authority story queryable without inventing a larger transaction object.

### Digest fields are inverse evidence too

If a publish session carries one of those digest fields, it must also carry the matching
`authority.trigger`.

That means a receipt can no longer say `policy_decision_digest` while claiming `trusted-ui`, or say
`operator_session_digest` while claiming `policy`.

### Mixed authority lanes are out of bounds

A publish session authority object should not carry parallel `consent_receipt_digest`,
`policy_decision_digest`, `operator_session_digest`, or `support_session_digest` values at once.

The lane that justified the share should be singular and obvious.
If multiple governance steps happened earlier, they should join upstream into the chosen authority lane
rather than making `net.publish.session.authority` explain several competing causes.

### `maintenance` stays reserved

`authority.trigger = maintenance` remains reserved for a future dedicated maintenance-window authority
join.
This doc does **not** let maintenance borrow `consent_receipt_digest`, `policy_decision_digest`,
`operator_session_digest`, or `support_session_digest` as placeholder proof. That reserved-trigger posture is now wired into the schema and guardrails too; see `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md`.

## What this prevents

### No trusted-UI share backed only by policy or operator folklore

If a share says it came from trusted UI, it now has to point at the exact consent receipt.

### No operator-session share without the exact operator session

If a share says it was created in an operator session, the receipt now has to name that exact session
through `operator_session_digest`.

### No multi-digest authority guessing game

Support/UI/export no longer need to guess whether a share was “really” a consent lane, a policy lane,
or a support lane because several digest families were all present at once.

## Why this is the right floor now

This is intentionally small.
It does **not** define the future maintenance-window evidence object, a richer approval transaction, or
a broader cross-lane workflow language.
It only keeps the existing authority trigger vocabulary and existing digest families from drifting apart.

That is enough to make eventual implementation and forensics more coherent without widening the
architecture.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_authority_join_contract.py`
- `tools/check_publish_session_maintenance_trigger_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`
- `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`
- `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`

Last updated: 2026-03-19r320
