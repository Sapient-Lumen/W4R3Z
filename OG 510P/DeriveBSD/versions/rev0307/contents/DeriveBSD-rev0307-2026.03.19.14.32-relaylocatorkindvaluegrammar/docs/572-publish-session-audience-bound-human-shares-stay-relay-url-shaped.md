# Publish-session audience-bound human shares stay relay-url-shaped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already fixed three access-model shapes:
- public callback/demo publication stays URL-shaped,
- support-peer handoff stays peer/session-shaped,
- and private tailnet sharing stays reverse-forward/device-name shaped.

One last ambiguity remained in the ordinary human share lane.

> if a publish session already says `organization-users` or `named-recipients`, can it still pretend
> to be a peer-relay or reverse-forward share?

If the archive leaves that open, audience-bound human sharing keeps borrowing support-session or
 private-device vocabulary even though the actual act is still “open this bounded share URL”.

See `adrs/ADR-0162-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`.

## Boundary

Audience-bound human temporary sharing is now explicitly **relay-url shaped**.

If either of the following is true, `published_endpoint.access_model` must be `relay-url`:

- `audience.class = organization-users`
- `audience.class = named-recipients`

That means auth-gated preview/demo shares and recipient-bound human shares now stay on the same
 URL-shaped lane as the already-accepted `public-link` / `public-webhook` postures, while the
 support-peer and tailnet lanes keep their distinct shapes.

## Matrix after this decision

The first useful access-model matrix is now complete:

- `organization-users` → `relay-url`
- `named-recipients` → `relay-url`
- `public-link` → `relay-url`
- `public-webhook` → `relay-url`
- `support-session-peer` → `peer-relay`
- `tailnet-users` → `reverse-forward`

The point is not to overfit providers.
The point is that receipts, trusted UI, support bundles, and policy surfaces now stop flattening
 normal human sharing, support-session handoff, and private tailnet publication into one vague
 “relay share” story.

## What this prevents

### No faux support-session wording for normal human shares

If a share says `organization-users` or `named-recipients`, it can no longer drift onto
 `access_model = peer-relay`.
That keeps ordinary audience-bound preview/demo sharing from looking like a support-session peer
 handoff.

### No private-device wording for ordinary recipient links

If a share says `organization-users` or `named-recipients`, it also cannot drift onto
 `access_model = reverse-forward`.
That keeps the private tailnet/device-name lane from becoming a vague synonym for any non-public
 share.

### No pressure to decide more than we know

This boundary still does **not** decide the final recipient roster model, directory integration,
 external-recipient policy, or whether `named-recipients` always compiles to one exposure scope.
ADR-0163 now adds the minimum binding-hint floor, though: `organization-users` / `provider-identity`
 shares name `identity_provider_hint`, and `named-recipients` shares name `recipient_hint`.
It only closes the remaining shape ambiguity in the already-accepted audience vocabulary.

## Product-shape reading

### A — fleet host

Audience-bound human sharing stays reviewable without teaching fleet publication to masquerade as
 support-session or tailnet posture.

### B — workstation

Ordinary authenticated preview/demo shares stay mentally simple: copy the bounded share URL rather
 than reasoning about peer-relay or private-device forwarding semantics.

### C — general OS

Developer/admin human shares stay distinct from both support-peer handoff and private tailnet
 device publication, which keeps the future UX/evidence model smaller.

### D — appliance factory / regulatory

Exceptional human shares remain easier to review because the receipt now clearly distinguishes URL-
 shaped audience-bound publication from the peer/session and private-device lanes.

## Schema surface

See:

- schema: `spec/net.publish.session.schema.json`
- example: `spec/examples/net.publish.session.json`
- audience posture: `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- access-model posture: `docs/570-publish-session-access-model-posture-boundary.md`
- tailnet posture: `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`

The schema now binds `organization-users` and `named-recipients` to `relay-url`, while the newer
 binding-hint floor also requires `identity_provider_hint` / `recipient_hint` where those audience
 labels would otherwise be hand-wavy. The guardrails validate synthetic ordinary human-share drifts
 so future edits cannot collapse them back into support-peer or tailnet vocabulary or into
 unexplained recipient prose.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/570-publish-session-access-model-posture-boundary.md`
- `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`
- `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`

Last updated: 2026-03-19r303
