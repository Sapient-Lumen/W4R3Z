# Publish-session authority stays lease-addressable

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

`net.publish.session` already says temporary sharing is leased, reboot-cleared, and evidence-shaped.
The archive also already fixed the trigger/digest lane so authority proof stays singular.

One smaller but still practical ambiguity remained in the authority object itself.

> if temporary sharing is leased, what keeps the receipt from omitting the actual lease handle and
> leaving revoke/query/support flows to rediscover the share through timestamps, relay hints, or
> operator-session folklore?

If the archive leaves that open, `expires_at` still tells readers that some bounded authority window
existed, but the receipt can still omit the compact identifier that says *which* temporary share lease
is live, revocable, or worth investigating.

See `adrs/ADR-0177-publish-session-authority-stays-lease-addressable.md`.

## Boundary

Publish-session authority now stays **lease-addressable**.

### Every publish session carries `authority.lease_id`

`authority.lease_id` is now required in every `net.publish.session` receipt.
That keeps temporary sharing aligned with the archive's broader lease vocabulary instead of treating
publish-session expiry as a loose timestamp with no stable handle.

### `lease_id` answers a different question than trigger/digest joins

- `authority.trigger` and joined digests explain **why** the share was allowed.
- `authority.lease_id` explains **which bounded temporary authority instance** stayed in force.
- `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md` now also keeps that same bounded share instance tied to one stable outward published-endpoint surface instead of letting the lease stay constant while the share meaning drifts.

Those are adjacent but different jobs, and both matter for support, revoke, and export flows.

### This is still a small decision

This doc does **not** invent a richer maintenance-window object, new revocation receipt, or larger
lease registry schema for temporary sharing.
It only requires the existing lease handle to be present so the archive's leased-sharing story is real
in the canonical receipt.

## What this prevents

### No bounded share with no stable revoke/query handle

A publish session can no longer say it expires at some time while leaving support or CLI tooling to
hunt for the share through hostnames, relay locators, or guessed surrounding evidence.

### No support bundle that knows the proof lane but not the share instance

Support bundles and timeline-first handoff can now name both:
- the authority lane that justified publication,
- and the exact lease-shaped share instance that remained live.

That same bounded share instance now also carries a lease-frozen outward surface, so “which lease was live?” and “which copied/shareable endpoint surface did that lease mean?” no longer drift apart; see `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`.

### No drift back to timestamp-only temporary authority

Temporary sharing now stays operationally lease-shaped instead of becoming "a URL plus an expiry
string" that later tooling has to interpret heuristically.

## Why this is the right floor now

This is intentionally narrow.
It improves revoke/query/forensics immediately, and it does so without choosing a larger maintenance
workflow, a richer relay lifecycle object, or a cross-service sharing controller.

That is enough to keep temporary sharing implementable and explainable while preserving room for later
maintenance-window work.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_lease_id_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/586-publish-session-authority-joins-follow-trigger.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`

Last updated: 2026-03-20r324
