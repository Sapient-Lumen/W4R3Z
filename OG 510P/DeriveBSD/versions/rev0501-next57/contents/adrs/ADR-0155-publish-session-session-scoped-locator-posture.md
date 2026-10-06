# ADR-0155: Publish-session session-scoped locator posture

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 moved temporary sharing onto `net.publish.session` so B/C users no longer had to
normalize shadow tunnels or casual public listeners.
ADR-0153 then made audience/publicness explicit.
ADR-0154 then made the session explicitly reboot-cleared and `new-session-with-fresh-authority`.

One expensive ambiguity still remained:

**what prevents temporary sharing from quietly becoming durable publication through stable names?**

Current relay products deliberately span both sides of that line:
- some temporary modes mint a random URL or short-lived share locator,
- some account tiers add reserved domains or stable account hostnames,
- and some production modes attach custom DNS or durable named endpoints.

If DeriveBSD leaves that collapse implicit, `net.publish.session` can still become a poor-man's
`net.listen.*` lane: the operator keeps using the same stable hostname or reserved domain, and the
only thing that changed is that the path is now hidden behind a relay adapter.

The archive needs one small answer that preserves B/C ergonomics without giving A/D or long-lived
service publication a shadow ingress path.

## Decision

1. `net.publish.session.published_endpoint` now requires `locator_posture`.

2. The allowed `locator_posture` values are:
   - `session-scoped`
   - `tailnet-device-name`

3. `locator_posture = session-scoped` means the externally shared locator is minted for this
   publish session and is not the platform's durable naming surface.
   It may be provider-assigned, opaque, or human-visible, but it is not the archive's lane for
   reserved account domains, custom DNS, durable branded subdomains, or other cross-session names.

4. `locator_posture = tailnet-device-name` is the only stable-name exception, and it is only valid
   for `published_endpoint.exposure_scope = tailnet`.
   This captures the private-network device-name case without turning public DNS ownership into the
   temporary-sharing contract.

5. The following bindings are now part of the contract:
   - `exposure_scope = tailnet` implies `locator_posture = tailnet-device-name`
   - `exposure_scope` in `{organization, internet, support-peer}` implies
     `locator_posture = session-scoped`

6. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** use session-scoped relay locators for temporary
     internet/org/support sharing; if someone needs a durable hostname, that is a design signal to
     move onto the `net.listen.*` lane.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** do not get a backdoor durable-ingress lane
     through reserved relay domains or remembered public share hostnames.

7. `hostname`, `url_hint`, `path_prefix`, and `relay.remote_locator` remain hints/evidence only.
   They do not grant durable naming authority.

## Consequences

- Temporary sharing now has a real naming boundary, not just an audience and lifetime boundary.
- Support bundles and explain surfaces can answer whether a published endpoint was session-scoped or
  a private tailnet device name.
- Reserved relay domains, custom DNS, branded subdomains, and other durable endpoint naming stories
  stay on the durable ingress lane instead of reappearing as adapter folklore.
- B/C keep an ergonomic share path, but stable published names now act as a forcing function for a
  more explicit ingress design.

## Why this is narrow enough

This ADR does **not** define:
- the exact URL shape of any provider,
- whether the locator is random versus human-readable within a session,
- a full naming service,
- or how `net.listen.*` will eventually express durable public DNS policy.

It only fixes the missing naming boundary needed to keep relay-backed temporary sharing from
quietly turning back into durable ingress under a different label.
