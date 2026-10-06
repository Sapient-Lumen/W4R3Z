# ADR-0156: Publish-session redacted locators and separate secret handoff

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 moved temporary sharing onto `net.publish.session` so B/C users no longer had to
normalize shadow tunnels or casual public listeners.
ADR-0153 then made audience/publicness explicit.
ADR-0154 then made the session explicitly reboot-cleared and `new-session-with-fresh-authority`.
ADR-0155 then kept public/org/support locators session-scoped instead of durable.

One expensive ambiguity still remained:

**where does the actual bearer material go when a publish session uses `single-use-secret` or `shared-secret` auth?**

Current relay products deliberately span both sides of that line:
- some paths are identity-gated and keep the locator clean,
- some paths support shared secrets or basic-auth style gates,
- and many operator workflows regress to pasting the full bearer URL into chat, logs, tickets, or screenshots.

If DeriveBSD leaves that implicit, `net.publish.session` risks becoming a secret-exfiltration
object: the supposedly forensics-friendly receipt ends up carrying the usable query token,
path secret, or unwrap handle that actually grants access.

The archive already has a typed secret lane (`secret.receipt`).
Temporary sharing needs one small answer that preserves B/C ergonomics without turning receipts,
URL hints, and support bundles into bearer-material spill surfaces.

## Decision

1. `net.publish.session.published_endpoint.url_hint` and `path_prefix` remain **locator-only hints**.
   They must not carry embedded bearer material, query-string secrets, or fragments.

2. `net.publish.session.published_endpoint` now conditionally supports `secret_handoff` with:
   - `delivery = separate-secret-receipt`
   - `secret_receipt_digest`

3. `secret_handoff` is **required** when `published_endpoint.audience.authn_mode` is one of:
   - `single-use-secret`
   - `shared-secret`

4. `secret_handoff` means the usable secret travels through the existing secret lane and the
   publish-session receipt stores only the digest join to that handoff evidence.
   `net.publish.session` does **not** store the raw secret, wrapping token, or other bearer value.

5. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** may still use secret-gated temporary sharing,
     but the secret must travel separately from the locator/evidence surface.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** do not get to normalize “copy the full
     secret URL from the logs/ticket” as an operational access model.

6. `published_endpoint.audience.validation_hint` remains evidence-only metadata describing how the recipient
   should present or validate the secret (for example, a header name or validation scheme).
   It is not the secret itself.

## Consequences

- Publish-session receipts and support bundles can stay queryable without becoming bearer spill.
- Query-string token links, fragment-bearing share URLs, and other secret-in-locator patterns are no
  longer part of the blessed temporary-sharing contract.
- Existing secret infrastructure (`secret.receipt`) becomes the join point for secret-gated publish
  sessions instead of forcing a new subsystem.
- Human/operator UX can still choose convenient wrapping or delivery mechanisms later, but the
  archive now says where the authority boundary lives.

## Why this is narrow enough

This ADR does **not** define:
- the exact secret broker/provider,
- the exact unwrap UX,
- the exact secret format,
- or whether a provider validates the secret itself versus the origin validating it.

It only fixes the missing boundary: usable publish-session secret material travels on the secret
lane, while `net.publish.session` stays a redacted session/evidence envelope rather than a bearer
object.
