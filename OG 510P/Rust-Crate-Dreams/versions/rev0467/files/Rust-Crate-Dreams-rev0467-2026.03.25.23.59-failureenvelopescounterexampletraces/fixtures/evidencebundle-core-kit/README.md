# Evidence Bundle Core Kit fixtures

These fixtures exist to make **P-0256 Evidence Bundle Core Kit** concrete.

The goal is to make the proposal answer a compact receiver-facing question:

> what files should another maintainer, reviewer, or tool actually receive, how were they produced, and which of them can be safely shared or published?

## Minimal pack for 0.1

- `bundle-manifest.schema.json` — the stable entry index, profile identity, subjects, and relationship graph.
- `profile-contract.schema.json` — what a domain profile requires or permits above the core.
- `container-basis.receipt.schema.json` — why deterministic container claims are valid.
- `entry-lineage.report.schema.json` — whether each entry is raw, projected, generated, imported, copied, or redacted.
- `attestation-lane.receipt.schema.json` — what signature/attestation material is present and how it was imported.
- `publication-route.receipt.schema.json` — whether the bundle stays local or is staged for OCI / transparency / publication.
- `share-safety.receipt.schema.json` — whether the export is private, redacted-shareable, encrypted, or manual-review-only.
- `redaction-receipt.schema.json` — what content was removed, replaced, or preserved as placeholders.
- `verification-report.schema.json` — why the bundle verified or failed to verify.
- `diff-report.schema.json` — how two bundles differ semantically.

## Design rules

- Keep the **core substrate** small and reusable.
- Treat **DSSE / COSE / Sigstore material** as importable lanes, not as proof that the whole bundle problem is solved.
- Keep **local shareable bundles** first-class even when signatures or publication are absent.
- Preserve whether verification failed because of **missing files**, **digest mismatch**, **policy mismatch**, **signature failure**, or **unsupported external trust material**.
- Keep profile-specific meaning in profile contracts, not in the core manifest.

## Intended first scenarios

1. `redacted_support_export` — a locally produced support bundle removes secrets but preserves enough structure for another maintainer to diff and inspect it.
2. `publishable_signed_profile` — a domain profile emits a signed/exportable bundle that carries DSSE/Sigstore-related material without making publication infrastructure part of the core contract.

## Archive naming note

The fixture root is currently `fixtures/evidencebundle-core-kit/`.
That legacy spelling is retained intentionally for compatibility with older entries and index references until a deliberate bulk rename happens.

## Additional first scenarios

3. `deterministic_zip_claim_needs_container_basis_receipt` — a pack that claims reproducibility without concrete pack-policy receipts should not be treated as reviewable.
4. `mixed_raw_projection_review_entries_require_lineage_report` — generated summaries and normalized projections must not masquerade as raw evidence.
5. `sigstore_bundle_import_is_attestation_lane_not_core_manifest` — imported Sigstore material belongs in the attestation lane, not in the core manifest semantics.
6. `oras_subject_referrer_publication_is_optional_route` — local bundle validity and OCI publication route remain distinct truths.
7. `redacted_support_bundle_needs_share_safety_receipt` — redaction does not automatically mean a pack is safe to attach broadly.
