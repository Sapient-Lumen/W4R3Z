# Publish-session redacted locators and separate secret handoff boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixed four expensive ambiguities:

- temporary sharing is a separate relay-backed lane,
- the audience/publicness posture is explicit,
- the session is reboot-cleared with no auto-resume,
- and public/org/support locators stay session-scoped.

One quieter loophole still remained:

> when the share uses a secret, does the actual bearer material ride inside the URL,
> the publish-session receipt, or some other durable evidence surface?

If the archive leaves that open, support bundles and logs become the real secret distribution path.
See `adrs/ADR-0156-publish-session-redacted-locators-and-separate-secret-handoff.md`.

## The hard decision

Publish-session locators stay **redacted**, and secret-gated temporary sharing must use a **separate secret handoff**.

`net.publish.session.published_endpoint.url_hint` and `path_prefix` are locator-only hints for the `relay-url` lane only.
They may tell the operator where the share lives, but they do not carry query tokens, fragment
secrets, or other embedded bearer material.

When `published_endpoint.audience.authn_mode` is `single-use-secret` or `shared-secret`, the
publish session must carry `published_endpoint.secret_handoff` with:

- `delivery = separate-secret-receipt`
- `secret_receipt_digest`

That keeps the usable secret on the existing secret lane instead of hiding it inside the session
receipt or locator. The follow-on lifetime rule in `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md` then ensures the separate handoff secret cannot outlive the session authority, and `docs/568-publish-session-secret-consumption-semantics-boundary.md` makes the handoff consumption posture explicit through `secret_handoff.consumption_posture`. If the share is `public-webhook`, the receipt may still carry `published_endpoint.audience.validation_hint` so later readers can see what the receiver validates; that hint is evidence-only metadata and still not bearer material.

## Required bindings

### Secret auth modes require a separate handoff join

If `published_endpoint.audience.authn_mode` is one of:

- `single-use-secret`
- `shared-secret`

then `published_endpoint.secret_handoff` is required.
The session envelope records only the digest join to the typed `secret.receipt` evidence.

### Locator hints must stay clean

`published_endpoint.url_hint` and `path_prefix` must stay redacted locator hints.
That means the blessed temporary-sharing lane does **not** use:

- query-string bearer links,
- fragment-carried secrets,
- copy-the-full-secret-URL support tickets,
- or screenshots/log lines that double as the access credential.

Providers may still support those patterns somewhere in the ecosystem.
They are just not what `net.publish.session` means in DeriveBSD. `published_endpoint.audience.validation_hint` may still name a signature header, service-token header, or JWT assertion surface for `public-webhook`, but that validation hint is not bearer material.

## Why this matters operationally

Audience, lifetime, and naming were not enough by themselves.
A session can be audience-bound, reboot-cleared, and session-scoped while still teaching users to
copy a secret-bearing URL out of logs or support bundles.
Once that happens, the archive has turned its own evidence surfaces into an access channel.

This doc keeps the forcing function visible:

- if a share is identity-gated, the locator stays clean and no secret handoff is needed,
- if a share needs a secret, the secret moves through the existing `secret.receipt` lane,
- if that secret exists, its usable lifetime must also stay `session-authority-bounded` rather than surviving the share,
- and if the secret is meant to be one-time, the handoff must say so with `consumption_posture = single-successful-admission` instead of leaving reuse semantics implicit,
- and if a workflow only works by embedding the credential directly into the link, that is not the
  blessed temporary-sharing contract.

## Product-shape posture

### A — fleet host

Do not normalize secret-bearing share URLs in logs, tickets, or runbooks.
If breakglass/support needs a share secret, keep it on the secret lane and keep the publish-session
receipt redacted.

### B — workstation

Temporary sharing stays ergonomic, but the trusted UI should show a clean locator plus a separate
secret-handoff action when one is needed.
That prevents “copy this magic URL” from becoming the real product UX.

### C — general OS

The same rule holds for explicit admin/developer temporary sharing.
Secret-gated callbacks or named-recipient shares are still viable, but the secret must not become a
receipt/log artifact.

### D — appliance factory / regulatory

This keeps support workflows from quietly turning evidence exports or operator documentation into a
secret distribution channel.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- joined secret evidence: `spec/secret.receipt.schema.json`

The schema now requires the following for secret-gated publish sessions:

- `published_endpoint.secret_handoff.delivery = separate-secret-receipt`
- `published_endpoint.secret_handoff.secret_receipt_digest`

It also keeps `url_hint` and `path_prefix` redacted by forbidding query/fragment-bearing locator
hints.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/565-publish-session-session-scoped-locator-posture-boundary.md`
- `docs/575-publish-session-endpoint-hints-follow-access-model.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`
- `docs/568-publish-session-secret-consumption-semantics-boundary.md`
- `docs/272-sealed-secrets-attested-unsealing.md`

Last updated: 2026-03-19r305