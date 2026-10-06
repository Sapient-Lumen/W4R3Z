# Publish-session public-webhook shares require validation hints

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says when temporary sharing is callback-shaped instead of human-share
shaped: `audience.class = public-webhook` keeps the lane explicitly internet-facing and
`relay-url` shaped.

One ambiguity still remained inside that webhook lane itself.

> if a publish session says `public-webhook`, what tells later readers how the callback was
> actually supposed to be validated?

If the archive leaves that implicit, `public-webhook` is still doing too much work by itself.
Receipts and support bundles can see that a callback share existed, but they still cannot say
whether the receiver expected an HMAC signature header, a service-token header, or a signed JWT
assertion.

See `adrs/ADR-0164-publish-session-public-webhook-shares-require-validation-hints.md`.

## Boundary

Public-webhook publish sessions now require **validation hints**.

### Public-webhook shares must name the verification posture

If `audience.class = public-webhook`, then
`audience.validation_hint` is required.

This remains evidence-only metadata.
It is not the secret itself, the full adapter config, or a new provider-specific webhook registry.
It only keeps the archive from claiming a callback-validation posture while leaving the receipt
unable to say what the receiver was actually supposed to validate.

### Shared-secret webhooks still keep the secret elsewhere

If `public-webhook` also uses `authn_mode = shared-secret`, then the usable secret still travels on
`published_endpoint.secret_handoff.secret_receipt_digest`.
`validation_hint` only says how the callback is validated, such as a signature-header posture.

That keeps the receipt explainable without turning the validation clue into bearer material.

### Validation hints now stay webhook-only too

If `published_endpoint.audience.validation_hint` is present, the share must therefore also be `public-webhook`.

That keeps the field from drifting into a generic spare security-note slot on `public-link`, `organization-users`, `named-recipients`, or `support-session-peer` receipts. See `docs/591-publish-session-validation-hints-stay-webhook-only.md`.

### Provider-identity webhooks still need both clues

If `public-webhook` uses `authn_mode = provider-identity`, then the receipt still needs
`identity_provider_hint` from ADR-0163 **and** `validation_hint` from this boundary.

Those two hints answer different questions:
- `identity_provider_hint` says which provider posture held the gate
- `validation_hint` says what verification surface the receiver was meant to check

## What this prevents

### No callback lane with invisible verification

A share can no longer say `public-webhook` while omitting the validation clue that makes the
callback posture meaningful to operators, support bundles, and policy review.

### No confusing URL shape with security posture

A URL-shaped callback share is not automatically a bearer-URL share.
Requiring `validation_hint` keeps `public-webhook` from quietly collapsing into “public URL and
hope the receiver knows what to do.”

### No secret material hidden in the hint

`validation_hint` names the verification posture, not the secret value.
The usable secret still lives on the separate secret-receipt lane.

## Product-shape reading

### A — fleet host

Any exceptional callback publication now has to name the verification clue that made it bounded
enough to justify the exception.

### B — workstation

Webhook testing stays practical, but receipts and support bundles no longer have to infer the
callback verification posture from browser tabs, relay dashboards, or app code comments.

### C — general OS

Admin/developer callback workflows stay viable while giving trusted UI and forensics an explicit
handle for how the receiver was supposed to validate requests.

### D — appliance factory / regulatory

Any exceptional maintenance/lab callback posture now names its verification clue instead of
relying on vague “this webhook was secure somehow” prose.

## What this still does not decide

This boundary still does **not** decide:
- the final validation-hint vocabulary,
- the final provider-specific webhook adapters,
- the final service-token / JWT / signature registry,
- or whether stronger typed callback-validation objects are worth standardizing later.

It only keeps the already-accepted `public-webhook` posture evidence-shaped by requiring the hint
that makes that callback posture explainable.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- audience posture: `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- secret-handoff posture: `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`

The schema now requires `audience.validation_hint` whenever
`audience.class = public-webhook`.
If `audience.validation_hint` is present, the share must therefore also be `public-webhook`; see `docs/591-publish-session-validation-hints-stay-webhook-only.md`.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`

Last updated: 2026-03-20r321
