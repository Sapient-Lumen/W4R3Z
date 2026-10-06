# ADR-0249: Workstation data-transfer receipts join exact grants by digest

- Status: Accepted
- Date: 2026-03-22

## Context

The workstation transfer lane is already explicit and single-delivery by default (`docs/538-workstation-cross-domain-datatransfer-floor.md`).
`ADR-0248` then made the transfer artifacts actor-exact by requiring `offer_source_subject` beside `subject`.

But the receipt still stopped one join too early: it could name the actors and the offer id without naming the exact `ui.datatransfer.grant` artifact whose policy constraints governed the transfer.
That left detached support/export/forensics reconstructing policy from `offer_id`, `lease_id`, or broker-side state, which is inconsistent with the archive's broader exact-digest bias.

## Decision

Require `ui.datatransfer.receipt` to carry exact `grant_digest`.

This means:

1. `grant_digest` points to the exact `ui.datatransfer.grant` artifact whose MIME, size, expiry, and delivery posture governed the transfer.
2. `offer_id` and `lease_id` remain operational correlates, but they are not the portable source of truth for policy reconstruction.
3. Detached tooling should use the joined grant artifact when answering which transfer rules applied.

## Consequences

### Positive

- Transfer evidence becomes portable and self-describing.
- OCR-derived excerpt transfers now have a fully exact evidence chain: source artifact, source subject, receiving subject, and consumed grant artifact.
- Future explicit multi-delivery exceptions remain analyzable without forcing a bigger transfer-management subsystem first.

### Negative / costs

- Receipts become slightly wider.
- Implementations must keep the grant artifact digest available at receipt-minting time.

## Rejected alternatives

- **Rely on `offer_id` + `lease_id` only:** too much broker-memory and reuse folklore.
- **Put more policy summary directly on the receipt instead of joining the grant:** duplicates the artifact that already exists and invites divergence.
- **Design the whole multi-delivery/replay subsystem now:** too large for this iteration; the exact grant join solves the current coherence gap without forcing that bigger choice yet.

## Related

- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
