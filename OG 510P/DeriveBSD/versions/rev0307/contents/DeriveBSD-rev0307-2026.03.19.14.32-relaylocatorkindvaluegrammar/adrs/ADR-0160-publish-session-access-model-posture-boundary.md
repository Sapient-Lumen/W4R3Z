# ADR-0160: Publish-session access-model posture boundary

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 introduced `net.publish.session` so temporary sharing could stop collapsing into shadow
 tunnels or casual public listeners.
ADR-0153 then made audience/publicness explicit.
ADR-0154 through ADR-0159 tightened lifetime, locator, secret, and support-session authority
 posture.

One small but still implementation-expensive ambiguity remained:

**is every temporary share the same kind of share, or does the archive need to say when a share is
 URL-shaped versus peer/session-shaped?**

Without that boundary, the archive can say `support-peer` while still allowing
 `published_endpoint.access_model = relay-url`.
That quietly turns a support handoff back into “here is a tunnel URL” folklore even though the
 authority is supposed to stay session-shaped.
Likewise, callback/public-link shares can drift onto peer/session wording without the evidence
 surface ever saying whether the share was meant to be opened as a URL or joined through a support
 peer session.

Current ecosystems already split this space:
- temporary internet sharing tools describe a unique public URL for public callback/demo flows,
- while remote-support tools describe support/session codes or peer sessions rather than a generic
  shareable public URL.

DeriveBSD needs that distinction in the archive without choosing a single provider protocol.

## Decision

1. `net.publish.session.published_endpoint.access_model` remains small, but it is no longer free-form
   across all audience classes.

2. If either of the following is true:
   - `published_endpoint.audience.class = public-link`
   - `published_endpoint.audience.class = public-webhook`

   then `published_endpoint.access_model` must be `relay-url`.

3. If any of the following is true:
   - `published_endpoint.exposure_scope = support-peer`
   - `published_endpoint.audience.class = support-session-peer`
   - `published_endpoint.audience.authn_mode = support-session`

   then `published_endpoint.access_model` must be `peer-relay`.

4. This ADR deliberately does **not** fully decide the access-model matrix for every remaining
   audience.
   In particular, `organization-users`, `named-recipients`, and `tailnet` remain open for later
   tightening once the archive needs to choose among URL-shaped, relay-app, or reverse-forward UX.

5. This ADR does **not** change the already-accepted audience/publicness, lifetime, locator,
   secret-handoff, or support-session authority posture.
   It only makes the access-model proof surface agree with those earlier decisions.

## Consequences

- Public callback/demo publication stays visibly URL-shaped in receipts and support bundles.
- Support-peer temporary sharing stays session/peer-shaped instead of regressing to a generic tunnel
  URL with support prose attached.
- The archive gets a smaller, more honest implementation target: access model now carries enough
  meaning to shape UX and receipts without pretending every provider behaves the same.

## Why this is narrow enough

This ADR does **not** define:
- a provider API,
- a browser or native-app UX,
- how reverse-forward should work,
- or a universal peer relay protocol.

It only prevents the archive from using one access-model label to mean incompatible publication
 stories.
