# Publish-session maintenance triggers stay digest-empty until a dedicated lane exists

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already tightened the authority object in one direction:
non-maintenance triggers now carry exactly one matching joined digest lane.

One smaller ambiguity still remained:

> if `authority.trigger = maintenance` is only reserved for future work,
> what keeps a receipt from borrowing `consent_receipt_digest`, `policy_decision_digest`,
> `operator_session_digest`, or `support_session_digest` as placeholder proof anyway?

If the archive leaves that open, maintenance stays reserved only in prose while the schema still
allows a receipt to smuggle another authority lane under a different trigger label.

See `adrs/ADR-0180-publish-session-maintenance-triggers-stay-digest-empty.md`.

## Boundary

`authority.trigger = maintenance` now stays **digest-empty** with respect to the existing joined
publish-session authority lanes.

### Maintenance does not borrow another authority lane

If a publish session uses `authority.trigger = maintenance`, it must not carry any of:

- `consent_receipt_digest`
- `policy_decision_digest`
- `operator_session_digest`
- `support_session_digest`

That keeps the reserved maintenance trigger from quietly aliasing trusted-UI, policy,
operator-session, or support-session authority.

### Digest absence is intentional here

This is not “missing evidence” in the accidental sense.
It is the archive saying that the dedicated maintenance-window join does not exist yet,
so the reserved trigger must stay visibly unfilled instead of borrowing another lane's digest family.

### Existing maintenance lifetime posture still applies

A maintenance-triggered publish session is still lease-shaped and bounded:

- it still carries `authority.lease_id`
- it still carries `authority.expires_at`
- and it still requires `maintenance-window-end` in `lifecycle.end_conditions`

So this cut does not widen maintenance authority.
It only stops digest borrowing.

## What this prevents

### No maintenance label pasted over a policy digest

A receipt can no longer say `authority.trigger = maintenance` while actually joining only
`policy_decision_digest`.

### No maintenance placeholder built out of operator or support evidence

Maintenance-triggered shares can no longer smuggle `operator_session_digest` or
`support_session_digest` and force support/export surfaces to guess which lane “really” applied.

### No accidental compatibility contract for future maintenance work

By keeping maintenance digest-empty now, the archive avoids teaching future implementations that the
maintenance lane is just an alias for one of the already-typed authority families.

## Why this is the right floor now

This is intentionally small.
It does **not** define the future maintenance-window evidence object, a maintenance approval
transaction, or a broader share-orchestration protocol.
It only makes the already-stated reserved-trigger posture real.

That is enough to keep the current authority vocabulary coherent while leaving room for a later,
separate maintenance lane if the product truly needs one.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_maintenance_trigger_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/586-publish-session-authority-joins-follow-trigger.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/586-publish-session-authority-joins-follow-trigger.md`
- `docs/587-publish-session-authority-stays-lease-addressable.md`
- `docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md`

Last updated: 2026-03-19r320
