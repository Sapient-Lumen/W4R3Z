# ADR-0354: Removable-media local fallback post-detach denial receipts are typed and negative-tested

- Status: accepted
- Date: 2026-05-22
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0353-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md`, `spec/removable.media.local.post_detach.revocation.tombstone.schema.json`, `docs/293-attribute-indexed-metadata-and-live-queries.md`

## Context

ADR-0353 added exact-digest revocation tombstones so stale query, export, and digest-rehydration handles fail closed after revocation or expiry. A tombstone still leaves an audit gap: if a stale handle is later presented, the system needs a redacted receipt proving that the handle was denied because of the tombstone. Without such a receipt, a stale-handle path can become either a silent black hole or a support/debug path that leaks raw handle, path, filename, recipient, host, or receipt metadata.

## Decision

Add `spec/removable.media.local.post_detach.denial.receipt.schema.json` with kind `removable.media.local.post_detach.denial.receipt`, the canonical example `spec/examples/removable.media.local.post_detach.denial.receipt.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-denial-receipt/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded`, `sha256:6868686868686868686868686868686868686868686868686868686868686868`, and `known-bad-post-detach-denial-receipt-shapes-must-fail-validation` in the r509 revocation tombstone, r508 export bundle, r507 query projection, r506 recovery evidence, r504 post-detach contract backend evidence, canonical content import plan/receipt, and post-detach preopen map.

A denial receipt is required for stale query-handle, export-approval, digest-rehydration, remote-locator, or managed-copy attempts after tombstone visibility. It records a redacted, exact-digest denial event; it does not grant retry authority, does not create a successor handle, and does not claim erasure of offline copies.

## Consequences

- Deny-after-revocation becomes auditable instead of disappearing as a generic authorization failure.
- Query/support surfaces can show a redacted denial summary by digest and reason code without raw stale handles or locators.
- The rehydration broker must emit denial evidence when a digest join is blocked by a tombstone.
- Retry requires a fresh lease and fresh policy decision; stale handles cannot become renewal handles.
- Negative fixtures make common denial mistakes executable: missing tombstone causality, allowed stale export/rehydration, raw handle/locator leakage, host identity or filename leakage, missing monotonic sequence, unbounded retry, and successor authority without a fresh lease all fail validation.

## Alternatives considered

- **Let tombstones alone be enough.** Rejected because later stale-use attempts need denial evidence for UX, support, and audit.
- **Log raw handles for debugging.** Rejected because that reintroduces the exact metadata leak r507-r509 worked to suppress.
- **Treat denial as a renewal prompt.** Rejected because retry/renewal is fresh authority and must be mediated by a new lease.

## Follow-up

- Teach the first query/export/rehydration brokers to emit `removable.media.local.post_detach.denial.receipt` whenever a tombstone causes denial.
- Add UX copy that distinguishes “denied because future authority was revoked” from “file or copy no longer exists.”
- Consider a generic evidence-denial receipt only after this lane proves exact-digest denial receipts are usable.

## Links

- boundary doc: `docs/765-removable-media-local-fallback-post-detach-denial-receipts-are-typed-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.denial.receipt.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.denial.receipt.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-denial-receipt/`
- revocation tombstone: `docs/764-removable-media-local-fallback-post-detach-revocation-tombstones-are-typed-and-negative-tested.md`

Last updated: 2026-05-22r510
