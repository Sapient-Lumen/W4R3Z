# Publish-session local-service URI hints stay loopback-shaped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixes the outward relay/publication side of temporary sharing.
One smaller ambiguity remained at the local source.

> if the receipt already says the source listener stayed local-first, can `local_service.service_uri_hint` still point somewhere non-local or carry credential-bearing localhost text?

If the archive leaves that open, the same receipt can claim `bind_scope = loopback-only` while its local debugging hint quietly names a LAN/public endpoint, embeds userinfo, or hides query/fragment material that support exports were never meant to treat as secret handoff.

See `adrs/ADR-0170-publish-session-local-service-uri-hints-stay-loopback-shaped.md`.

## Boundary

If `local_service.service_uri_hint` is present, it now has to stay a **loopback-shaped, secret-clean local hint**.

### Absolute URI with authority only

`service_uri_hint` remains optional.
If it appears, it must be an absolute URI-shaped hint with an authority component.
That keeps the field reviewable as an actual URI instead of turning it into another free-form string next to typed protocol and bind-scope state.

### Loopback-shaped host only

If `service_uri_hint` appears, its authority host must stay loopback-shaped:

- `localhost`,
- any name under `.localhost`,
- or an IP loopback literal such as `127.0.0.1` or `::1`.

That keeps the hint subordinate to `bind_scope = loopback-only` / `broker-held-loopback` instead of quietly naming a LAN host, public hostname, or tailnet identity.

### Secret-clean authority and suffixes

If `service_uri_hint` appears, it must not carry:

- userinfo,
- query,
- or fragment.

This keeps the field a debugging/support hint rather than a second secret-delivery lane hidden inside a localhost-looking URI.

### Obvious scheme-bearing protocols should stay honest

For the protocols where the archive already expects an obvious URI scheme, the URI scheme must follow `local_service.protocol`:

- `http` stays on the `http` URI scheme
- `https` stays on the `https` URI scheme
- `ssh` stays on the `ssh` URI scheme

That is intentionally small.
It does **not** standardize richer local endpoint objects or every possible protocol taxonomy.
It only closes the most expensive obvious contradictions.

## What this prevents

### No outward drift on the local side

A receipt can no longer claim the source stayed loopback-only while `service_uri_hint` points at a LAN/public hostname.

### No credential-bearing localhost folklore

A receipt can no longer hide userinfo, query tokens, or fragments inside a localhost URI and leave support/UI guessing whether that string is safe to display.

### No protocol-vocabulary contradiction for common URI-shaped lanes

An `http` source can no longer carry `ssh://...` as its local hint, or vice versa.

## Why this is the right floor now

This is a narrow coherence cut.
It does not invent a new subsystem.
It just makes the local-source hint tell the same local-first story the rest of `net.publish.session` already tells.

That is enough to keep temporary-sharing receipts more trustworthy for implementation, support, and deterministic export.

## Wire-up points

- `spec/net.publish.session.schema.json`
- `spec/examples/net.publish.session.json`
- `tools/check_publish_session_local_service_hint_contract.py`
- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`

## Related

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/32-curated-references.md`

Last updated: 2026-03-19r310
