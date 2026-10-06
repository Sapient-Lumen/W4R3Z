# ADR-0165: Publish-session endpoint hints follow access model

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0160 made `net.publish.session` choose an explicit access model, ADR-0161 fixed private tailnet
sharing as `reverse-forward`, ADR-0162 fixed ordinary audience-bound human sharing as `relay-url`,
and ADR-0164 kept callback publication explicit about receiver-side validation.

That still leaves one quietly expensive ambiguity:

**once the share shape is explicit, which endpoint hints are canonical for that shape?**

Without one more small decision, a support-session peer handoff can still keep URL-like endpoint hints,
a tailnet/device-name share can still carry URL-only locator language, and a URL-shaped share can omit
its actual host/port floor and collapse into one opaque convenience string.

Current products already split these lanes in practice:
- public temporary publication commonly mints a URL/subdomain,
- private tailnet publication points at a device/service endpoint,
- and remote-support flows center a support/session code rather than a URL endpoint.

DeriveBSD does not need to standardize every UI yet, but it does need a coherent endpoint-hint grammar
for the shapes it has already accepted.

## Decision

1. If `published_endpoint.access_model = relay-url`, then `published_endpoint.hostname` and
   `published_endpoint.port` are required.

2. If `published_endpoint.access_model = reverse-forward`, then `published_endpoint.hostname` and
   `published_endpoint.port` are required, and `url_hint` / `path_prefix` are not valid.

3. If `published_endpoint.access_model = peer-relay`, then `hostname`, `port`, `url_hint`, and
   `path_prefix` are not valid.

4. If `url_hint` or `path_prefix` appears, `published_endpoint.access_model` must be `relay-url`.

5. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** keep three distinct endpoint-hint families:
     `relay-url` → `hostname + port` plus optional URL hints,
     `reverse-forward` → `hostname + port`,
     `peer-relay` → support/session authority without URL/host endpoint hints.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** gain a cleaner evidence boundary for any
     exceptional temporary publication without normalizing a single ambient share grammar.

## Consequences

- URL-shaped publication stays easy to implement, but receipts no longer depend on a single opaque
  `url_hint` string.
- Tailnet/device-name sharing stays private-network-shaped instead of drifting back into URL-only
  tunnel language.
- Support-peer publication stops pretending it has a copyable host/URL endpoint when the real
  authority story is the exact `support.session` join.

## Why this is narrow enough

This ADR does **not** define:
- a final support-session UX vocabulary,
- a typed endpoint registry for every adapter,
- or any new audience classes or transport subsystem.

It only binds the already-accepted endpoint hint fields to the already-accepted access-model split.
