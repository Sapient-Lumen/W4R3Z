# Publish-session session-scoped locator posture boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixed three expensive ambiguities:

- temporary sharing is a separate relay-backed lane,
- the audience/publicness posture is explicit,
- and the session is reboot-cleared with no auto-resume.

One quieter loophole still remained:

> can a "temporary" share keep the same durable hostname or reserved public locator across sessions,
> effectively becoming a poor-man's durable ingress story?

If the archive leaves that open, shadow tunnels come back through naming instead of through process
lifetime.
See `adrs/ADR-0155-publish-session-session-scoped-locator-posture.md`.

## The hard decision

Relay-backed publish sessions must keep public/org/support locators **session-scoped**.

`net.publish.session.published_endpoint.locator_posture` now records whether the published locator is:

- `session-scoped`, or
- `tailnet-device-name`

That looks tiny, but it closes the remaining loophole between "bounded temporary share" and
"durable published endpoint with a relay in front".

## Required bindings

### Public/org/support temporary sharing stays session-scoped

If `published_endpoint.exposure_scope` is one of:

- `organization`
- `internet`
- `support-peer`

then `published_endpoint.locator_posture` must be `session-scoped`.

That means the blessed temporary-sharing lane does **not** use:

- reserved relay domains,
- custom DNS,
- branded or operator-chosen public hostnames,
- or other cross-session locator ownership as the real contract surface.

Those can still exist somewhere in the ecosystem.
They are just not what `net.publish.session` means in DeriveBSD.

### Tailnet sharing may use the private device-name lane

If `published_endpoint.exposure_scope = tailnet`, then
`published_endpoint.locator_posture = tailnet-device-name`.

This is the one stable-name exception because it is still a private-network posture and does not
quietly hand the temporary-sharing lane durable public DNS authority. That private stable-name lane
now also stays `reverse-forward` shaped rather than pretending to be a URL-shaped relay share; see
`docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`.

## Why this matters operationally

Audience and lifetime were not enough by themselves.
A session can be leased, audience-bound, and reboot-cleared while still training users to depend on
some remembered public hostname or reserved relay domain. The endpoint-hint grammar is now fixed separately too: URL-shaped shares and tailnet reverse-forward shares carry hostname + port, while peer-relay support handoff does not pretend to have a copied host/URL endpoint; see `docs/575-publish-session-endpoint-hints-follow-access-model.md`. The archive now also freezes the full outward published-endpoint surface for one bounded share, so session-scoped locator posture cannot be paired with same-lease hostname/path/audience drift elsewhere in `published_endpoint`; see `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`.
Once that happens, the relay adapter becomes the real ingress surface and `net.listen.*` is bypassed
in practice.

This doc keeps the forcing function visible:

- if you need a durable public name, that is a signal to design durable ingress,
- if you need a quick share, webhook test, or short demo, the locator stays session-scoped,
- and if you just need private tailnet sharing, the stable private device-name lane is already enough.

## Product-shape posture

### A — fleet host

Do not treat reserved relay domains or stable public share URLs as acceptable service publication.
If a fleet service needs a durable externally known name, move it to the existing listen-broker lane.

### B — workstation

Temporary sharing stays ergonomic, but the URL is expected to be session-shaped.
That prevents preview/demo convenience from hardening into remembered public hostnames as the real
product surface.

### C — general OS

The same rule holds for explicit admin/developer temporary sharing.
Stable callback or public service names are a different design problem and belong on the durable lane.

### D — appliance factory / regulatory

This keeps maintenance/lab relay tooling from quietly becoming the naming authority for shipped
systems or regulated support posture.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`

The schema now requires `published_endpoint.locator_posture` and fixes:

- `tailnet` → `tailnet-device-name` + `reverse-forward`
- `organization` / `internet` / `support-peer` → `session-scoped`
- endpoint hints: `docs/575-publish-session-endpoint-hints-follow-access-model.md` (`relay-url` / `reverse-forward` carry hostname + port)

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`

Last updated: 2026-03-20r324
