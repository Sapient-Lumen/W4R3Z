# ADR-0178: Publish-session support-session triggers stay support-peer-shaped

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0159 fixed the first half of the support handoff boundary:
if a publish session says `support-peer`, or uses `support-session-peer` / `support-session`
audience posture, it must join an exact `support.session` digest.
ADR-0176 then made authority joins singular and exact by requiring
`authority.trigger = support-session` to carry `authority.support_session_digest`.

One smaller but still expensive ambiguity remained:

**what keeps a receipt from claiming `authority.trigger = support-session` for an ordinary
`public-webhook`, `public-link`, or `organization-users` share?**

Without one more narrow decision, a public callback or audience-bound human share can still borrow
support-session authority vocabulary while staying `relay-url` shaped and internet-facing. That
reopens the exact confusion the archive has been trying to retire: was this a real support peer
handoff, or just a generic URL share with support-flavored proof attached after the fact?

DeriveBSD does not need a larger maintenance/support transaction object here, but it does need the
existing support-session authority lane to stay tied to the existing support-peer share shape.

## Decision

1. `net.publish.session.authority.trigger = support-session` now implies the full support-peer share
   shape.

2. When the trigger is `support-session`, the publish session must also carry:
   - `published_endpoint.exposure_scope = support-peer`
   - `published_endpoint.access_model = peer-relay`
   - `published_endpoint.audience.class = support-session-peer`
   - `published_endpoint.audience.authn_mode = support-session`

3. This is the inverse of ADR-0159's earlier boundary.
   The archive now keeps both directions aligned:
   - support-peer share posture implies support-session authority; and
   - support-session authority implies support-peer share posture.

4. This ADR does **not** invent a broader remote-assistance workflow language or make all support
   actions relay publication.
   It only keeps the existing publish-session support authority lane from justifying non-support
   share shapes.

## Consequences

- Support-session authority can no longer justify a generic `relay-url` callback/demo share.
- Support/export surfaces no longer have to guess whether `support-session` means a real support peer
  handoff or just a public share that borrowed support vocabulary.
- Future maintenance/support evidence can grow separately without weakening the current support-peer
  floor.

## Alternatives considered

- **Leave `authority.trigger = support-session` usable on any share shape.** Rejected because it
  lets public or ordinary audience-bound shares quietly masquerade as support handoffs.
- **Invent a separate support publication object.** Rejected as too wide for this round.
- **Rely only on prose that support-session should usually mean support-peer.** Rejected because the
  archive already has the typed vocabulary needed to make this exact.
