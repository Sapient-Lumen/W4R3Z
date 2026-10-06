# ADR-0186: Publish-session notes stay off baseline envelope

- Status: Accepted
- Date: 2026-03-20

## Context

`net.publish.session` is the compact, outward-facing receipt for relay-backed temporary sharing. ADR-0185 already removed backstage diagnostic artifact digests from that bounded envelope, but the schema still allowed free-text `evidence.notes`. That reopened a prose side channel on the same compact receipt: operators, support flows, and UI layers could start depending on ad-hoc commentary instead of the typed audience, authority, access-model, locator, and join surfaces that already exist.

## Decision

Remove free-text `evidence.notes` from `net.publish.session`. The compact publish-session envelope stays note-free. Commentary, operator diagnosis, support context, and other interpretive material belong on stronger evidence joins or neighboring typed receipts, not on the bounded share receipt itself.

## Consequences

- Copyable/share-facing publish-session receipts stay typed and baseline-safe.
- UI, support, export, and audit consumers cannot rely on an ambient prose escape hatch to recover meaning missing from typed fields.
- New temporary-sharing semantics should be added as typed fields, joins, or dedicated follow-on receipts instead of free-text notes.
