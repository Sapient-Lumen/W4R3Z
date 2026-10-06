# Publish-session published endpoint surface stays lease-frozen

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says temporary sharing is leased, reboot-cleared, session-scoped on
public/org/support locators, and typed enough that `hostname`, `port`, `url_hint`, `path_prefix`,
audience, and access-model posture tell one coherent story.

One smaller ambiguity still remained across revisions of the same share:

> once a temporary share is copied, bookmarked, or handed to support, what keeps the same
> `authority.lease_id` from quietly changing the outward published endpoint surface and still
> pretending to be the same bounded share?

If the archive leaves that open, one lease-shaped share can still drift underneath copied URLs,
support references, and audit trails.

See `adrs/ADR-0184-publish-session-published-endpoint-surface-stays-lease-frozen.md`.

## Boundary

`published_endpoint.continuity_posture` now stays `lease-frozen`.

### One publish-session lease means one outward published-endpoint surface

For one `net.publish.session`, the outward published-endpoint surface stays frozen for the life of
that bounded share.

That means the canonical outward share story already carried in `published_endpoint` —
`exposure_scope`, `access_model`, `hostname`, `port`, `url_hint`, `path_prefix`, audience posture,
locator posture, and any secret-handoff shape when present — does not silently change underneath the
same lease.

### Material outward change requires a fresh session and fresh authority

If the outward published-endpoint surface materially changes, DeriveBSD now treats that as a **new**
temporary share.
It must mint a fresh:

- `session_id`
- `authority.lease_id`

instead of quietly mutating the old bounded share in place.

### This stacks with, rather than replaces, the earlier temporary-sharing cuts

This decision does **not** replace the earlier ones.
Publish sessions still stay:

- reboot-cleared with `resume_policy = new-session-with-fresh-authority`
- `session-scoped` on public/org/support locators
- lease-addressable through `authority.lease_id`
- tuple-coherent inside the `relay-url` lane

This cut only says those already-typed outward fields now remain stable for the lifetime of one
bounded share.

## What this prevents

### No same-lease repointing of copied share URLs

A copied URL or support reference can no longer keep the same bounded lease identity while the
underlying hostname/path/audience posture quietly changes.

### No stealth surface mutation hidden behind lease continuity

The archive no longer has to guess whether “same lease” meant “same share” or only “same relay tool
instance with a different outward surface.”

### No bookmark/support ambiguity about which share was actually live

Support/export/revoke surfaces can now treat one `authority.lease_id` as one stable outward share
surface instead of reconstructing which version of a moving endpoint the lease was supposed to mean.

## Why this is the right floor now

This is intentionally small.
It does **not** define redirect chains, aliases, or durable public-name reuse for temporary
sharing.
It only forbids same-lease outward-surface drift.

That is enough to make copied-share semantics, support bundles, and future implementation more
coherent without widening the architecture.

For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_surface_continuity_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/587-publish-session-authority-stays-lease-addressable.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/565-publish-session-session-scoped-locator-posture-boundary.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/587-publish-session-authority-stays-lease-addressable.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`

Last updated: 2026-03-20r324
