# ADR-0159: Publish-session support-peer shares require support-session authority

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 introduced `net.publish.session` so temporary sharing could stop collapsing into shadow
tunnels or casual public listeners.
ADR-0153 then made audience/publicness explicit, including a `support-session-peer` audience
with `support-session` authn mode.
ADR-0154 then made those shares reboot-cleared and explicitly bounded.

One expensive ambiguity still remained:

**what proves that a support-peer publish session is actually part of a live support session, rather
than just wearing support-flavored audience labels?**

Without that join, a relay-backed handoff can still drift into a freestanding support URL:
- `published_endpoint.exposure_scope = support-peer` could still be authorized by `trusted-ui`,
  `policy`, or `maintenance` instead of the support-session lane,
- the receipt could omit `authority.support_session_digest`,
- and later review/export surfaces would have to infer the human support context from unrelated logs
  or operator folklore.

That would weaken A/D support discipline, blur B/C temporary support ergonomics into generic
relay publication, and leave forensics unable to answer *which support session justified this
support-peer share?*

Remote-support tooling in the broader ecosystem already keeps the support handoff session-shaped:
one-time support codes or explicit support sessions are created, shared, then ended rather than
treated as durable published service endpoints.
DeriveBSD needs the same archive-level answer without standardizing any single vendor protocol.

## Decision

1. `support-peer` publish sessions become a strict **support-session authority lane**.

2. If any of the following is true:
   - `published_endpoint.exposure_scope = support-peer`
   - `published_endpoint.audience.class = support-session-peer`
   - `published_endpoint.audience.authn_mode = support-session`

   then the publish session must also require:
   - `authority.trigger = support-session`
   - `authority.support_session_digest`
   - `lifecycle.end_conditions` containing `support-session-end`

3. If `authority.trigger = support-session`, `authority.support_session_digest` is required even if
   the adapter/provider wording changes elsewhere.

4. Trusted UI consent, operator review, or maintenance approvals that justify a support-peer share
   should join into the `support.session` lane first (or be referenced from it).
   They do **not** become a freestanding alternative authority vocabulary for support-peer publish
   sessions.

5. This decision does not change the existing audience, lifetime, locator, redaction, or secret
   posture rules for `net.publish.session`.
   It only fixes the missing authority join for the support-peer lane.

## Consequences

- Support-peer relay publication becomes queryably tied to one exact `support.session` evidence
  object instead of vague support intent.
- A/D can keep support publication exceptional and forensics-friendly without inventing a separate
  support-ingress subsystem.
- B/C temporary support sharing stays ergonomic, but the proof now names the live support session
  that justified it.
- The archive can answer *which support session created this support-peer share and when did that
  session end?* without reopening ambient logs.

## Why this is narrow enough

This ADR does **not** define:
- a remote-support transport protocol,
- a new identity provider,
- a transcript format,
- or a vendor-specific helpdesk integration.

It only makes the support-peer temporary-sharing lane subordinate to the already-existing
`support.session` authority family.
