# ADR-0181: Publish-session validation hints stay webhook-only

- Status: Accepted
- Date: 2026-03-20

## Context

ADR-0164 already made `public-webhook` temporary sharing explicit in one direction:
when a publish session says `published_endpoint.audience.class = public-webhook`,
it must also carry `published_endpoint.audience.validation_hint` so the receipt can say what the
receiver was supposed to validate.

One smaller but still expensive ambiguity remained:

**what keeps a receipt from carrying `published_endpoint.audience.validation_hint` even when the
share class is not `public-webhook` at all?**

Without one more narrow decision, organization-user previews, named-recipient shares, public links,
support-peer handoffs, or tailnet shares can still carry webhook-validation prose and tell two
competing stories about what kind of receiver boundary actually held.

DeriveBSD does not need a broader generic “validation note” field here, but it does need
`validation_hint` to stay the typed webhook-verification clue it already became.

## Decision

1. `published_endpoint.audience.validation_hint` now follows
   `published_endpoint.audience.class` exactly.

2. If `audience.class = public-webhook`, `validation_hint` remains required.

3. If `validation_hint` is present, `audience.class` must therefore be `public-webhook`.

4. Non-webhook share classes (`public-link`, `organization-users`, `named-recipients`,
   `support-session-peer`) must not carry `validation_hint`.

5. This ADR does **not** invent a generic validation-note vocabulary for all publish-session share
   types. If future product work needs some other typed verification clue, it should arrive as a
   new lane-specific field instead of overloading the webhook field.

## Consequences

- Human-share receipts can no longer carry webhook-validation prose “just in case.”
- Support-peer and tailnet-shaped receipts keep their own typed posture instead of borrowing
  callback-verification language.
- Receipts, trusted UI, and support bundles can read `validation_hint` as meaning one thing:
  webhook receiver verification posture.

## Alternatives considered

- **Leave `validation_hint` optional outside `public-webhook`.** Rejected because it lets receipts
  mix callback-verification prose into non-webhook share classes.
- **Treat `validation_hint` as a generic free-form security note.** Rejected because that would turn
  a typed clue back into a spare comment slot.
- **Invent a broader verification-hints object now.** Rejected as too wide for this round.
