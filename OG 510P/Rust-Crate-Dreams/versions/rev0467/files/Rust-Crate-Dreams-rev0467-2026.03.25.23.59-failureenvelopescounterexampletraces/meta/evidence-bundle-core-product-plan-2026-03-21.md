# Evidence Bundle Core Kit — product plan (2026-03-21)

This note sharpens **P-0256 Evidence Bundle Core Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0256** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to become a universal attestation format, a registry/distribution platform, or a remote transparency service.
It should provide one boring, reviewable **bundle substrate contract** above today’s ZIP, DSSE, Sigstore, OCI, and transparency/publication building blocks.

`0.1` should make five things first-class:

1. **container basis** — why deterministic-pack claims are justified;
2. **entry lineage** — where each entry came from and what transformations occurred;
3. **attestation lane** — which signature/attestation material is present and whether it was generated here or imported;
4. **publication route** — whether the bundle stays local or is prepared for OCI / SCITT / other publication;
5. **share-safety posture** — whether the bundle is private, redacted-shareable, encrypted, or still manual-review-only.

## What `0.1` should provide other people

- one compact `bundle-manifest.json`
- one compact `profile-contract.json`
- one compact `container-basis.receipt.json`
- one compact `entry-lineage.report.json`
- one compact `attestation-lane.receipt.json`
- one compact `publication-route.receipt.json`
- one compact `share-safety.receipt.json`
- one compact `redaction-receipt.json`
- one compact `verification-report.json`
- one compact `diff-report.json`
- one compact `bundle.summary.md`
- one portable support/review bundle

## Commands worth shipping first

- `cargo evidence init`
- `cargo evidence pack`
- `cargo evidence inspect`
- `cargo evidence verify`
- `cargo evidence explain`
- `cargo evidence diff`
- `cargo evidence redact`
- `cargo evidence classify-share-safety`
- `cargo evidence classify-publication-route`

## What to import, not reinvent

- in-toto statement / envelope semantics
- DSSE serialization/signature semantics
- Sigstore bundle verification material and timestamp/transparency evidence
- OCI `subject` / referrers publication semantics
- SCITT-style external transparency/publication lanes

## Suggested `0.1` doctor warnings

- `deterministic_pack_claim_missing_container_basis`
- `generated_projection_missing_lineage`
- `attestation_lane_imported_but_claimed_as_core_semantics`
- `publication_route_claimed_without_subject_or_reference`
- `shareable_export_missing_share_safety_receipt`
- `redaction_done_but_lineage_not_updated`
- `sigstore_material_present_without_local_policy_explanation`
- `local_verify_green_but_publication_route_unreviewed`

## First proving-ground scenarios

1. **A redacted support export should still classify its share-safety posture explicitly instead of assuming redaction means “safe”.**
2. **An imported Sigstore bundle should sit in the attestation lane, not silently redefine the core bundle contract.**
3. **An OCI subject/referrers publication route should remain optional and separately reviewable from local bundle validity.**
4. **A mixed raw/projection/review pack should make entry lineage explicit so derived summaries do not masquerade as raw evidence.**
5. **A deterministic ZIP claim should carry concrete packing-policy receipts, not just a README promise.**

## What to leave for later

- hosted publication services
- mandatory online transparency checks
- universal key management
- every possible domain profile
- full cross-language SDK parity
- policy engines for every regulated environment

## `0.1` artifact vocabulary to stabilize first

### 1. `container-basis.receipt.json`
Should answer:
- which archive/container format is in use,
- which ordering, timestamp, path, and compression rules were applied,
- and which digest algorithms and canonicalization rules define reproducibility.

### 2. `entry-lineage.report.json`
Should answer:
- whether an entry is raw, projected, generated, imported, copied, or redacted,
- which source entries it depends on,
- and whether the entry is safe to compare semantically or only bytewise.

### 3. `attestation-lane.receipt.json`
Should answer:
- whether the bundle is unsigned, locally signed, or importing external DSSE / COSE / Sigstore material,
- what subject/digest binding is claimed,
- and whether verification depends on external trust roots or timestamps.

### 4. `publication-route.receipt.json`
Should answer:
- whether the bundle is local-only, flat-file export, OCI-attached, transparency-submitted, or staged for later publication,
- which subject association or repository scope is in play,
- and whether publication status is observed, inferred, or manual-review-only.

### 5. `share-safety.receipt.json`
Should answer:
- who may receive the bundle,
- what redaction/encryption/manual-review posture applies,
- what residual leakage classes remain,
- and why the pack is or is not safe to attach to an issue or ticket.

## Definition of success for `0.1`

A maintainer should be able to answer, from one bundle alone:

> What exactly is in this pack, where did each entry come from, what attestation material is present, whether this bundle is only local or also publication-ready, and whether I can safely share it with another team?

If `0.1` can answer that clearly without pretending to own every upstream spec, it is already valuable.
