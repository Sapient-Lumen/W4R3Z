# Publish-session endpoint hints follow access model

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says **what shape** a temporary share takes:
- `relay-url` for public/demo/webhook and ordinary audience-bound human shares,
- `peer-relay` for support-session-bound peer handoff,
- `reverse-forward` for private tailnet/device-name sharing.

One expensive ambiguity still remained inside that shape split.

> once the share shape is explicit, which endpoint hints are canonical for that shape?

If the archive leaves that open, receipts can still mix URL hints, host+port hints, and support-session
language in ways that make eventual implementation inconsistent.
A support-peer handoff can keep pretending to have a tunnel URL, or a tailnet reverse-forward share can
keep carrying URL-only hints even though the archive already decided it is not a public URL lane.

See `adrs/ADR-0165-publish-session-endpoint-hints-follow-access-model.md`.

## Boundary

Publish-session endpoint hints now follow **access model**.

### `relay-url` requires `hostname + port`

If `published_endpoint.access_model = relay-url`, the receipt must carry:
- `published_endpoint.hostname`
- `published_endpoint.port`

`published_endpoint.url_hint` and `path_prefix` may still appear, but they remain convenience/evidence
hints layered on top of that canonical `hostname + port` floor.
`published_endpoint.hostname` itself now also has to stay host-shaped rather than becoming a pasted URL, `host:port`, or localhost-style name; see `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`.
`published_endpoint.path_prefix` in this lane now also stays normalized, so the typed path floor does
not rely on repeated separators or `.` / `..` cleanup; see `docs/582-publish-session-path-prefixes-stay-normalized.md`.
When they do appear, they now travel together and must serialize that same endpoint tuple; see
`docs/579-publish-session-url-hints-follow-endpoint-tuple.md`.

### `reverse-forward` also requires `hostname + port`

If `published_endpoint.access_model = reverse-forward`, the receipt must also carry:
- `published_endpoint.hostname`
- `published_endpoint.port`

This keeps private tailnet sharing aligned with the device-name/service-port grammar the archive has
already chosen. `published_endpoint.hostname` in this lane now also stays a lowercase host-shaped token instead of a URL-ish or localhost-shaped string; see `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`.
For this lane, `url_hint` and `path_prefix` are not valid. When `path_prefix` does appear in the
`relay-url` lane, it now also stays normalized instead of relying on separator-collapse or dot-segment cleanup; see `docs/582-publish-session-path-prefixes-stay-normalized.md`.
A reverse-forward share is not a URL-shaped publish lane.

### `peer-relay` keeps URL/host hints absent

If `published_endpoint.access_model = peer-relay`, the receipt must **not** carry:
- `hostname`
- `port`
- `url_hint`
- `path_prefix`

That keeps support-session peer handoff honest.
The authority join and peer/session posture explain the share; the receipt does not pretend there is a
stable host:port or URL-shaped endpoint to copy around.

### `url_hint` and `path_prefix` imply `relay-url`

If `published_endpoint.url_hint` or `published_endpoint.path_prefix` appears, the access model must be
`relay-url`.
That prevents tailnet/device-name or support-session peer handoff from drifting back into URL-shaped
receipt language.

## What this prevents

### No support-session handoff pretending to be a host/URL endpoint

A `peer-relay` support share can no longer carry `hostname`, `port`, `url_hint`, or `path_prefix` as if
its real UX were still “copy this URL.”

### No tailnet reverse-forward share pretending to be a public URL

A private tailnet share can no longer keep `url_hint` / `path_prefix` while claiming `reverse-forward`.
The receipt now has to say `hostname + port` instead.

### No URL-shaped publication without the actual endpoint floor

A `relay-url` share can no longer omit `hostname + port` and leave the receipt dependent on a single
opaque `url_hint` string.

## Product-shape reading

### A — fleet host

Exceptional callback/demo publication remains tightly described, while support-peer and private mesh
handoff stop borrowing URL/host grammar they should not normalize.

### B — workstation

Users and support can tell the difference between “open this URL,” “open this tailnet device name and
port,” and “join this support peer session” without reopening relay dashboards or chat transcripts.

### C — general OS

Developer sharing stays practical, but eventual CLI/UI flows now have a smaller and more coherent
endpoint grammar to implement.

### D — appliance factory / regulatory

Evidence for temporary publication becomes easier to audit because each access model now carries one
canonical endpoint-hint family.

## What this still does not decide

This boundary still does **not** decide:
- the final UI wording for support-session peer handoff,
- the final pretty-printing of `hostname + port`,
- or whether stronger typed endpoint objects are worth standardizing later.

It only fixes which existing endpoint hints belong to which already-accepted share shape.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- access-model posture: `docs/570-publish-session-access-model-posture-boundary.md`
- tailnet posture: `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- webhook validation posture: `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`

The schema now requires `hostname + port` for `relay-url` and `reverse-forward`, keeps `url_hint` /
`path_prefix` restricted to `relay-url`, and keeps `peer-relay` free of URL/host endpoint hints. `docs/579-publish-session-url-hints-follow-endpoint-tuple.md` then makes the optional URL-hint family serialize the same `hostname + port + path_prefix` tuple instead of drifting beside it, while `docs/582-publish-session-path-prefixes-stay-normalized.md` and `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md` keep the typed path half normalized and URI-path-safe too so the typed path floor does not rely on repeated separators, dot-segment cleanup, percent-decoding, or raw-space cleanup. Relay-side `relay.remote_locator.kind` then follows access model too; see `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/565-publish-session-session-scoped-locator-posture-boundary.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`
- `docs/579-publish-session-url-hints-follow-endpoint-tuple.md`
- `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`
- `docs/582-publish-session-path-prefixes-stay-normalized.md`
- `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`

Last updated: 2026-03-19r315
