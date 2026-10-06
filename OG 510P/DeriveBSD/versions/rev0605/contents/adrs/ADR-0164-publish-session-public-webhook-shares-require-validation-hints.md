# ADR-0164: Publish-session public-webhook shares require validation hints

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 moved temporary service sharing onto `net.publish.session` so B/C users no longer had to
normalize shadow tunnels or casual public listeners.
ADR-0153 then made audience/publicness explicit, ADR-0156 kept secret-gated locator hints
redacted, ADR-0160 fixed access-model posture, and ADR-0163 required binding hints for
audience-bound human shares.

One expensive ambiguity still remained in the public callback lane:

**if a publish session says `public-webhook`, what tells later readers how the callback was meant to be validated?**

Current webhook products deliberately make verification explicit: shared-secret signatures,
service-token headers, or signed identity assertions are separate from the URL itself and need
explicit verification logic on the receiving side.

If DeriveBSD leaves that implicit, `public-webhook` becomes a URL-shaped label with no durable clue
about what the receiver was supposed to validate. Receipts and support bundles can see that the
share was not a human preview, but they still cannot say whether the callback depended on an HMAC
header, a signed JWT assertion, or some other explicit validation posture.

The archive already has `audience.validation_hint` on `net.publish.session`. Temporary webhook
publication needs one small answer that keeps callback publication explainable without forcing a
provider-specific webhook subsystem.

## Decision

1. If `net.publish.session.published_endpoint.audience.class = public-webhook`, then
   `published_endpoint.audience.validation_hint` is required.

2. `validation_hint` remains **evidence-only metadata** describing the callback verification
   posture, for example:
   - signature header / scheme
   - service-token header name
   - JWT assertion header / validation surface

3. `validation_hint` is **not** the secret itself, the full provider configuration, or a new
   canonical registry of every webhook scheme. It exists so the receipt can answer
   *what did the receiver have to validate?*

4. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** may still use `public-webhook` temporary
     sharing for explicit callback/demo/integration workflows, but the receipt must say what
     verification posture held the boundary.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** do not get to normalize vague
     “public callback somehow” publication without an explicit validation clue in the evidence.

## Consequences

- Public callback publication becomes explainable enough for trusted UI, receipts, policy review,
  and support bundles without forcing adapter-specific config into the schema.
- The archive keeps distinguishing URL shape from validation posture: `public-webhook` can stay
  `relay-url` shaped while still naming the verification clue that made the callback acceptable.
- Secret-gated webhook publication remains joined to `secret.receipt`; `validation_hint` only says
  how the receiver validates the request, not where the secret lives.

## Why this is narrow enough

This ADR does **not** define:
- the final webhook verification registry,
- the exact header grammar,
- the exact service-token or JWT provider choices,
- or whether future adapters add stronger typed callback-verification objects.

It only fixes the missing boundary: `public-webhook` receipts must carry a validation hint so the
callback posture stops being evidentially hand-wavy.
