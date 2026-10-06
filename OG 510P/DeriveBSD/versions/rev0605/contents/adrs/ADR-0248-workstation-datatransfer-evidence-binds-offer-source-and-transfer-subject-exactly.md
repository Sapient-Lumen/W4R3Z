# ADR-0248: Workstation data-transfer evidence binds offer-source and transfer subject exactly

Status: Accepted  
Date: 2026-03-22

## Context

`adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md` already made the workstation baseline explicit:
there is no ambient shared cross-domain clipboard, transfer is directional, and single-delivery is the boring default.
`adrs/ADR-0247-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md` then fixed one narrower follow-on:
OCR-derived text still leaves searchable foreign inspection only through that same explicit transfer lane, with a plain-text baseline and optional `content_source` provenance join.

One small but important evidence gap still remained:
**the archive says support/export should be able to answer which compartment offered the data and which compartment accepted it, but `ui.datatransfer.*` artifacts only named one `subject` plus an `offer_id`.**

That makes the source side too easy to recover from folklore:

- broker-private state
- direction-specific inference
- UI context that may no longer exist
- support notes instead of typed artifacts

## Decision

1. `ui.datatransfer.grant` and `ui.datatransfer.receipt` now carry exact `offer_source_subject`.
2. `subject` remains the exact holder of the grant/receipt.
3. For `direction = read`, the ordinary interpretation is:
   - `offer_source_subject` = source/exporting compartment
   - `subject` = destination/consuming compartment
4. For `direction = write`, `offer_source_subject` ordinarily equals `subject`, because the source side is creating the offer.
5. OCR-derived text transfer examples should keep the actor pair explicit too:
   - `offer_source_subject` names the inspection viewer
   - `subject` names the destination notes/editor app
   - `content_source` continues to preserve the receipted OCR artifact lineage

Plainly stated: subject remains the exact holder of the grant/receipt.

## Consequences

- The explicit transfer lane can now directly answer which subject offered and which subject received data.
- Cross-domain OCR text copying no longer needs direction folklore to explain the actor pair.
- Support/export surfaces do not need hidden broker history to reconstruct the source side.
- The lane stays compact: no new clipboard subsystem, only a tighter artifact contract.

## Follow-up wiring

- new boundary doc: `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- canonical schemas/examples: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.receipt.json`, `spec/examples/ui.datatransfer.grant.ocr-inspection-text.json`, `spec/examples/ui.datatransfer.receipt.ocr-inspection-text.json`
- workstation docs: `docs/205-data-transfer-portals-clipboard-and-dnd.md`, `docs/538-workstation-cross-domain-datatransfer-floor.md`, `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md`
- guardrail: `tools/check_workstation_datatransfer_subject_exactness.py`
