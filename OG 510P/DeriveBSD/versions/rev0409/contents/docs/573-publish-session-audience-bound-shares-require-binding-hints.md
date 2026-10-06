# Publish-session audience-bound shares require binding hints

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says **who** a temporary share is for and **what shape** that share
keeps:
- public callback/demo publication stays `relay-url` shaped,
- support-peer handoff stays `peer-relay` shaped,
- private tailnet sharing stays `reverse-forward` shaped,
- and ordinary human shares stay `relay-url` shaped too.

One ambiguity still remained inside the audience wording itself.

> if a publish session says `organization-users`, `named-recipients`, or `provider-identity`, what
> names the actual binding hint that made that audience real?

If the archive leaves that implicit, the audience label is still doing too much work by itself.
Receipts and support bundles can see that a share was *supposed* to be audience-bound, but they
still cannot say which IdP posture or recipient binding actually held the boundary.

See `adrs/ADR-0163-publish-session-audience-bound-shares-require-binding-hints.md`.

## Boundary

Audience-bound publish sessions now require **binding hints**.

### Provider-identity shares must name the IdP posture

If `audience.authn_mode = provider-identity`, then
`audience.identity_provider_hint` is required.

That keeps provider-backed temporary sharing evidence-shaped without standardizing one provider or
one claim vocabulary.
The receipt still stays adapter-neutral; it just stops hiding which identity-provider posture held
that gate.

### Organization-user shares must also name the IdP posture

If `audience.class = organization-users`, then
`audience.identity_provider_hint` is required.

This is intentionally redundant with the provider-identity rule.
It keeps the ordinary organization-user lane from drifting back to "coworkers somehow" when the
archive already decided that `organization-users` is an identity-gated human-share posture.

### Named-recipient shares must name the recipient binding

If `audience.class = named-recipients`, then
`audience.recipient_hint` is required.

This remains evidence-only metadata.
It is not a new contact database, a final roster picker, or a promise that the full recipient list
must be embedded in the receipt.
It only keeps the archive from claiming *named* recipients while leaving the receipt unable to say
what recipient binding it was talking about.

## What this prevents

### No hand-wavy organization-user gates

A share can no longer say `organization-users` while omitting the
`identity_provider_hint` that explains which provider posture actually held the boundary.

### No named recipients without any named binding

A share can no longer say `named-recipients` while omitting `recipient_hint`.
That keeps the phrase from degenerating into "someone got the link somehow".

### No provider-identity folklore

A share can no longer say `provider-identity` while leaving later readers to guess which provider
surface enforced it.
That matters for explain UIs, support bundles, and future adapter contracts.

## Product-shape reading

### A — fleet host

Exceptional audience-bound temporary sharing remains reviewable because the receipt can now say both
that it was identity-gated and what provider posture held the gate.

### B — workstation

Human preview/demo sharing stays ergonomic, but support and forensics no longer have to infer which
IdP or recipient binding made the share bounded.

### C — general OS

Admin/developer temporary sharing stays practical while giving receipts and support bundles one more
exact handle to explain why a share was not fully public.

### D — appliance factory / regulatory

Any exceptional maintenance/lab sharing posture now names its audience-binding hint instead of
relying on vague recipient prose that is hard to defend later.

## What this still does not decide

This boundary still does **not** decide:
- the exact identity-provider protocol,
- the final group/claim vocabulary,
- the final recipient roster shape,
- or whether `named-recipients` always means internal identities.

It only keeps the already-accepted audience postures evidence-shaped by requiring the binding hints
that make those postures explainable. `identity_provider_hint` and `recipient_hint` now also stay
lane-exact as inverse evidence too, so non-IdP and non-recipient lanes cannot borrow them as spare
notes; see `docs/592-publish-session-binding-hints-stay-lane-exact.md`.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- audience posture: `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- human-share posture: `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`

The schema now requires:
- `identity_provider_hint` whenever `authn_mode = provider-identity`
- `identity_provider_hint` whenever `audience.class = organization-users`
- `recipient_hint` whenever `audience.class = named-recipients`

Those binding hints are inverse evidence too:
- if `identity_provider_hint` is present, `authn_mode` must stay `provider-identity`
- if `recipient_hint` is present, `audience.class` must stay `named-recipients`

See `docs/592-publish-session-binding-hints-stay-lane-exact.md`.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`

Last updated: 2026-03-20r322
