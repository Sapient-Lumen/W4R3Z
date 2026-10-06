# Publish-session secret consumption semantics boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixed six expensive ambiguities:

- temporary sharing is a separate relay-backed lane,
- the audience/publicness posture is explicit,
- the session is reboot-cleared with no auto-resume,
- public/org/support locators stay session-scoped,
- secret-gated locators stay redacted with a separate secret handoff,
- and that separate handoff stays `session-authority-bounded`.

One quieter loophole still remained:

> what does `single-use-secret` actually mean, and how is it different from `shared-secret`
> once the secret has already been handed off?

If the archive leaves that open, support and implementation will improvise incompatible answers.
See `adrs/ADR-0158-publish-session-secret-consumption-semantics.md`.

## The hard decision

Secret-gated publish sessions keep a **separate secret handoff**, and that handoff now also records
an explicit **consumption posture**.

When `published_endpoint.audience.authn_mode` is secret-based,
`published_endpoint.secret_handoff.consumption_posture` must say whether the secret is:

- `single-successful-admission`, or
- `reusable-until-expiry`

This keeps the contract adapter-neutral while refusing to let `single-use-secret` degenerate into
“maybe one click, maybe one TCP session, maybe unlimited until someone notices.”
`secret_handoff` is now reserved to secret authn modes only too, so non-secret lanes cannot carry the same handoff object and muddy whether the receiver was supposed to present a secret at all; see `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`.

## Required bindings

### `single-use-secret` means one successful admission

If `published_endpoint.audience.authn_mode = single-use-secret`, then:

- `published_endpoint.secret_handoff.consumption_posture = single-successful-admission`
- the handoff secret is consumed by the first **successful admission**
- failed or abandoned attempts before success do not count as the use
- and any later access must come from a fresh publish session or a newly issued handoff

That gives B/C recipient handoffs a practical retry story without leaving the secret reusable after
it has already succeeded once.

### `shared-secret` stays reusable until expiry or revoke

If `published_endpoint.audience.authn_mode = shared-secret`, then:

- `published_endpoint.secret_handoff.consumption_posture = reusable-until-expiry`
- the secret may be reused until its bounded expiry or manual revoke
- and ADR-0157 still keeps that reuse window inside `authority.expires_at`

This preserves temporary callback/webhook viability without pretending it was a one-time recipient
handoff.

## Why this matters operationally

ADR-0156 solved *where the secret goes*.
ADR-0157 solved *how long the secret stays valid*.
This doc solves *how many successful admissions the secret buys*.

Without it, the archive still teaches an incoherent pattern:

- the receipt says `single-use-secret`,
- the operator cannot tell whether the first successful open burns it,
- retries after success are guesswork,
- and support cannot distinguish “needs reissue” from “still reusable until expiry”.

That is exactly the kind of small ambiguity that turns a bounded temporary-share lane into folklore.

## Product-shape posture

### A — fleet host

If breakglass/support uses a temporary secret at all, the receipt must say whether it was
`single-successful-admission` or `reusable-until-expiry`. No “single-use in name only” folklore.

### B — workstation

Trusted UI can still make secret handoff ergonomic, but it must show whether the share secret is a
one-success recipient handoff or a reusable temporary callback secret.

### C — general OS

Admin/developer temporary sharing keeps the same boundary. Secret retries after one successful
admission require a new issued handoff instead of silent reuse when the posture was
`single-successful-admission`.

### D — appliance factory / regulatory

This keeps audit/export stories crisp: evidence can distinguish a one-time support handoff from a
reusable temporary secret without inventing a larger provider-specific session family.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- joined secret evidence: `spec/secret.receipt.schema.json`

The schema now requires the following for secret-gated publish sessions:

- `published_endpoint.secret_handoff.consumption_posture`
- `single-use-secret` ⇒ `single-successful-admission`
- `shared-secret` ⇒ `reusable-until-expiry`

The guardrail then enforces those bindings in the canonical example and archive wording.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/223-secrets-and-key-management-as-evidence.md`

Last updated: 2026-03-19r319
