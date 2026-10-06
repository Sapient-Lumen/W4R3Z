# Publish-session support-peer requires support-session authority boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles

`net.publish.session` already fixed seven expensive ambiguities:

- temporary sharing is relay-backed and distinct from durable ingress,
- audience/publicness is explicit,
- shares are reboot-cleared and no-auto-resume,
- public/org/support locators stay session-scoped,
- usable secrets stay off the locator/evidence lane,
- secret handoff lifetime stays inside session authority,
- and `single-use-secret` versus `shared-secret` now has explicit consumption semantics.

One expensive ambiguity still remained:

> when a publish session says it is for a `support-session-peer`, what exact support-session evidence
> proves that?

If the archive leaves that open, a relay-backed support handoff can still be authorized by the
wrong lane, omit the support-session digest, and then fall back to ticket folklore or log archaeology
when operators later need to explain *which support session justified this share?*

See `adrs/ADR-0159-publish-session-support-peer-shares-require-support-session-authority.md`.

## Boundary

Support-peer publish sessions are not just audience-labeled.
They are now an explicit **support-session authority join**.

If any of the following is true:

- `published_endpoint.exposure_scope = support-peer`
- `published_endpoint.audience.class = support-session-peer`
- `published_endpoint.audience.authn_mode = support-session`

then the publish session must also carry:

- `authority.trigger = support-session`
- `authority.support_session_digest`
- `published_endpoint.access_model = peer-relay`
- `lifecycle.end_conditions` containing `support-session-end`

That keeps the support-peer share subordinate to a real `support.session` evidence object instead of
letting a relay provider URL, support operator claim, or ad-hoc trusted UI click become the real
authority story.

## What this prevents

### No support-flavored freestanding URLs

A relay endpoint cannot call itself a support-peer handoff while the actual authority trigger says
`trusted-ui`, `policy`, or `maintenance`.
If the share is truly support-peer, the authority lane must also be `support-session`.

### No missing support-session digest

If `authority.trigger = support-session`, then `authority.support_session_digest` is required.
A support-peer publish session is therefore queryably tied to one exact `support.session` object.

### No support audience drift

If an adapter tries to say `audience.authn_mode = support-session` or
`audience.class = support-session-peer` while keeping `exposure_scope = internet` or some other
generic value, the schema now rejects it.
Support-session wording stays on the support-peer lane. The follow-on access-model boundary in `docs/570-publish-session-access-model-posture-boundary.md` then keeps that lane visibly `peer-relay` shaped instead of URL-shaped.

## Why this stays small

This does **not** add a new subsystem.
The archive already has `support.session`; this boundary just makes `net.publish.session` join that
existing session evidence when the temporary sharing posture is specifically support-peer.

Trusted UI consent or helpdesk workflow can still exist.
They just need to land on or join the `support.session` lane instead of becoming a parallel
authority vocabulary for support-peer shares.

## Product-shape reading

### A — fleet host

Support-peer relay publication remains exceptional, but now it has a crisp proof boundary: the
share must point at the exact `support.session` that justified it.

### B — workstation

A user-visible support share can stay ergonomic, but the durable receipt must still say which
`support.session` it belonged to rather than leaving the context in chat history or operator memory.

### C — general OS

Admin/developer support handoffs keep the same boundary.
`support-session` is a real authority join, not just a UI label on an otherwise generic internet
share.

### D — appliance factory / regulatory

Exceptional maintenance shares stay bounded, reviewable, and tied to one support-session evidence
object for later audits.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- joined support evidence: `spec/support.session.schema.json`

The schema now keeps three things aligned:

- `support-peer` exposure implies `support-session` authority
- `support-session-peer` audience implies `support-peer` exposure
- `authority.trigger = support-session` implies `authority.support_session_digest`

The guardrail then enforces those bindings in the schema, synthetic support-peer examples, and
archive wording.

## Related docs

- `docs/291-remote-assistance-sessions-as-evidence.md`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/461-remote-assistance-posture-by-profile.md`
- `docs/570-publish-session-access-model-posture-boundary.md`

Last updated: 2026-03-19r300
