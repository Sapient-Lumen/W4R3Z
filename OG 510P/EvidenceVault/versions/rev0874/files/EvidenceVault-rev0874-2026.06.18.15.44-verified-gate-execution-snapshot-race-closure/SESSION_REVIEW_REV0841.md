# EvidenceVault rev0841 session review: missing pieces, waste, and correction path

Created: 2026-06-12T15:06-04:00 America/New_York

Scope: deep read of the uploaded rev0840 overlay/patch bundle plus standards research. This is a review and hygiene overlay; it does **not** declare the datacube publication-ready.

## Highest-priority conclusions

1. **Keep the publication block.** The rights gate is doing the right thing. Missing root `LICENSE`/`COPYING`/final `NOTICE`, at least one missing local license reference target, and NOASSERTION SBOM/RO-Crate posture are real blockers.
2. **Fix overlay identity and portability before the next public-facing bundle.** The canonical tree audit says no cloud/container absolute paths, but the shipped overlay had cloudtainer-local input paths in `CHECKS/input-artifacts.sha256`; the cumulative patch also preserves many historical `/mnt/data` and `/home/oai` references.
3. **Separate canonical-release identity from overlay/patch identity.** This bundle is an overlay, while `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, `MANIFEST.sha256`, and SBOM still describe rev0826 canonical surfaces. That can be valid, but it must be explicit enough that no operator validates the wrong artifact.
4. **Stop repeating heavy scans.** The rev0840 gate log reports a 38-step gate taking about 329.49s, with `rebuild_indexes.py` about 106.25s. Dedupe and inventory scans are repeated across build, rebuild, and validate phases.
5. **Finish subprocess isolation.** The rebuild refactor uses subprocess refreshes, but `rebuild_indexes.py` still imports/runs some material builders in-process later. Move it fully to orchestration plus JSON handoff.

## Corrected in rev0841

- `CHECKS/input-artifacts.sha256` now records input archive basenames instead of `/mnt/data/...` absolute paths.
- Added `CHECKS/patch-bundle-identity-rev0841.json` to make the overlay/canonical split explicit.
- Added this review in Markdown and JSON.
- Added `AUDIT/OVERLAY_ABSOLUTE_PATH_REFERENCE_AUDIT_REV0841.*` so the overlay itself is audited, not only the canonical tree.
- Refreshed `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` for this revised overlay bundle.

## Deliberately not changed in rev0841

- The canonical patch streams under `PATCHES/` were not rewritten; changing their content would invalidate the existing patch-hash and validation story.
- `MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, `SBOM/spdx.json`, and rights ledgers were left as canonical/reviewed surfaces, not silently reinterpreted as rev0841 canonical release files.
- No license or NOTICE content was invented.

## Parsed local metrics

```json
{
  "dedupe_report": {
    "duplicate_copies": 460,
    "duplicate_extra_bytes": 3762513,
    "files_scanned": 4584,
    "unique_blobs": 4124
  },
  "gate_log": {
    "build_dedupe_report_mentions": 3,
    "gate_seconds": 329.49,
    "gate_steps": 38,
    "rebuild_indexes_seconds": 106.25,
    "validate_dedupe_report_mentions": 2
  },
  "manifest_index_overlay_shape": {
    "index_paths_missing_from_overlay": 4553,
    "index_paths_present_in_overlay": 33,
    "index_rows": 4586,
    "manifest_lines": 4588,
    "manifest_paths_missing_from_overlay": 4553,
    "manifest_paths_present_in_overlay": 35
  }
}
```

## Findings

### rev0841-f01-overlay-absolute-path-audit-gap — high — portability/privacy

The canonical-tree absolute path audit reports no cloud/container absolute paths, but the overlay artifact itself shipped CHECKS/input-artifacts.sha256 with /mnt/data source paths and the cumulative patch with /mnt/data and /home/oai provenance paths.

Evidence:
- AUDIT/ABSOLUTE_PATH_REFERENCE_AUDIT.md status: no_cloud_container_absolute_paths_found
- CHECKS/input-artifacts.sha256 originally contained two /mnt/data/... input archive paths
- PATCHES/rev0826-to-rev0840-cumulative.patch contains many historical absolute-path references in diff headers/body

Change this turn: CHECKS/input-artifacts.sha256 was normalized to basenames. The cumulative patch was intentionally left unchanged because rewriting it would change the validated patch payload.

Recommended next change: Run a separate overlay-artifact audit before packaging, classify historical patch provenance separately, and produce future patches from relative source-controlled roots.

### rev0841-f02-overlay-vs-canonical-identity-ambiguity — high — release identity

The ZIP name and README are rev0840/0841 overlay artifacts, while RELEASE_MANIFEST.json, ro-crate-metadata.json, SBOM namespace, and archive identity still describe rev0826 canonical surfaces. That is probably intentional for a patch bundle, but it is easy for a downstream operator to validate the wrong thing.

Evidence:
- README.md: overlay/patch bundle, not signed canonical release
- RELEASE_MANIFEST.json revision: rev0826
- ro-crate-metadata.json root name/version: EvidenceVault rev0826
- MANIFEST.sha256 and INDEX/files.json describe thousands of canonical paths that are absent from this overlay-only bundle

Change this turn: Added CHECKS/patch-bundle-identity-rev0841.json and clarified README/CHANGE_SUMMARY language.

Recommended next change: Split canonical release identity from overlay bundle identity everywhere: canonical manifest, patch-bundle manifest, and package-level provenance should be distinct objects with explicit subject digests.

### rev0841-f03-rights-block-is-correct-but-unfinished — high — publication rights

The publication block is appropriate and should remain in place. Missing root LICENSE/COPYING/NOTICE, one missing local license reference target, and NOASSERTION posture mean no public release should proceed yet.

Evidence:
- RIGHTS/component_license_ledger.json status: publication_blocked_pending_rights_decision
- RIGHTS/license_evidence_scan.json aggregate_findings include referenced_license_file_missing
- RO-Crate and SPDX inventory remain NOASSERTION

Change this turn: No license was invented and no rights blocker was bypassed.

Recommended next change: Decide license/copyright text per component, add root LICENSE and NOTICE or component-specific notices, resolve the PACT local LICENSE reference, and refresh SPDX/RO-Crate rights metadata from the same ledger.

### rev0841-f04-rights-gate-staleness-risk — medium — publication rights

publication_rights_gate.py checks the ledger and root rights files directly, but local license-reference integrity is mostly trusted through the ledger/audit surfaces. A stale false-negative ledger could miss a newly broken local LICENSE reference if root license files exist.

Evidence:
- scripts/publication_rights_gate.py loads RIGHTS/component_license_ledger.json and checks actual root LICENSE/COPYING/NOTICE
- Missing local reference evidence lives in RIGHTS/license_reference_integrity_audit.json / license_evidence_scan surfaces

Change this turn: Recorded as a required hardening item; no gate code was changed in this review-only revision.

Recommended next change: Make the gate run a cheap fresh local-license-reference scan or require a digest-pinned, non-stale license_reference_integrity audit tied to the current tree digest.

### rev0841-f05-rebuild-and-gate-waste — medium — performance / cloudtainer cost

The validation flow is doing expensive whole-tree scans repeatedly in a small overlay workflow. This is not catastrophic at current size, but it is already visible and will scale poorly.

Evidence:
- VALIDATION/gate_rev0840_clean.log parsed summary: {'gate_steps': 38, 'gate_seconds': 329.49, 'rebuild_indexes_seconds': 106.25, 'build_dedupe_report_mentions': 3, 'validate_dedupe_report_mentions': 2}
- DEDUPE_REPORT summary parsed: {'files_scanned': 4584, 'unique_blobs': 4124, 'duplicate_copies': 460, 'duplicate_extra_bytes': 3762513}
- The gate runs build_dedupe_report.py, rebuild_indexes.py triggers another dedupe build, and validate_dedupe_report.py scans again.

Change this turn: Captured the waste pattern for prioritization.

Recommended next change: Introduce a content-addressed cache for heavy scans, persist per-file hash/size/mtime indexes, let validators consume generated summaries, and run full rescans only when tree digests or relevant builder code changes.

### rev0841-f06-subprocess-isolation-incomplete — medium — validator architecture

The rev0839 subprocess-refresh audit is directionally good, but rebuild_indexes.py still imports and runs some material builders in-process after the subprocess phase. That preserves a class of interpreter-state/shutdown-state risks the refactor was meant to avoid.

Evidence:
- scripts/rebuild_indexes.py uses subprocess for a refresh phase
- scripts/rebuild_indexes.py later imports build_dedupe_report and build_spdx_inventory in-process

Change this turn: Recorded as a correction path.

Recommended next change: Move all material-surface builders to subprocess calls with JSON handoff, including dedupe and SPDX, and make rebuild_indexes.py a coordinator rather than a mixed coordinator/importer.

### rev0841-f07-sbom-is-file-inventory-not-release-sbom — medium — SBOM / provenance

The SPDX document is useful as a file inventory, but it is not yet a strong release SBOM: packages are absent, everything is NOASSERTION, and the namespace uses example.invalid/rev0826 while the distributed artifact is a later overlay.

Evidence:
- SBOM/spdx.json has package count 0, files only, NOASSERTION licenses
- SPDX documentNamespace is tied to example.invalid/evidencevault/rev0826/spdx/file-inventory

Change this turn: No SBOM rewrite was attempted.

Recommended next change: Add component/package records and CONTAINS relationships, update the SPDX license-list metadata when regenerating, and use a unique namespace tied to the actual artifact digest/revision.

### rev0841-f08-ro-crate-profile-needs-overlay-bridge — medium — RO-Crate / metadata

The RO-Crate profile is acceptable as a selected/distribution metadata bridge, but it currently speaks mostly as rev0826 while the user-facing artifact is a rev0840/0841 overlay. The next release should describe both the canonical dataset and the overlay/patch artifact, or keep them in separate crates.

Evidence:
- ro-crate-metadata.json root dataset name/version: EvidenceVault rev0826
- RO_CRATE_PROFILE/README.md states selected governance/integrity/rights surfaces are modeled, not every file

Change this turn: Recorded the split; no RO-Crate rewrite was done.

Recommended next change: Add a patch-bundle Dataset entity, explicit isBasedOn/hasPart links to patches and validation logs, and rights/license contextual entities once legal decisions are made.

### rev0841-f09-citation-and-scholarly-metadata-missing — low — citation / publication

The bundle has papers and RO-Crate/SPDX surfaces, but no obvious CITATION.cff or equivalent citation landing metadata for users to cite the dataset/code/papers coherently.

Evidence:
- No root CITATION.cff in the overlay bundle
- RO-Crate root remains rev0826 and rights-blocked

Change this turn: Recorded as publication-readiness work.

Recommended next change: Add CITATION.cff, AUTHORS/CONTRIBUTORS, and a release DOI/Zenodo mapping only after the rights decision is finalized.

### rev0841-f10-dry-run-preview-under-blocked-rights — low — operator ergonomics

The rights gate correctly blocks publication commands before side effects, but this also means operators cannot easily preview what a blocked queue item would do. A separate explicit non-mutating explain mode would help without weakening the gate.

Evidence:
- scripts/publish_queue_item.py calls assert_publication_rights_ready before queue mutation or preview
- rev0840 fixed dry-run mutation by moving dry-run return before write operations

Change this turn: No behavior changed.

Recommended next change: Add --explain-blocked or --plan-only that emits candidate paths/hashes and rights blockers, never writes, and never claims publishability.

### rev0841-f11-manifest-validation-ergonomics — low — operator ergonomics

MANIFEST.sha256 and INDEX/files.json describe canonical full-tree surfaces, not the overlay bundle. That is valid for a patch overlay but should be impossible to mistake for an overlay-file manifest.

Evidence:
- Parsed overlay presence summary: {'manifest_lines': 4588, 'manifest_paths_present_in_overlay': 35, 'manifest_paths_missing_from_overlay': 4553, 'index_rows': 4586, 'index_paths_present_in_overlay': 33, 'index_paths_missing_from_overlay': 4553}
- CHECKS/overlay-manifest.json is the correct overlay-file manifest but is easy to miss next to MANIFEST.sha256

Change this turn: Updated CHECKS/overlay-manifest.json and added explicit README warnings.

Recommended next change: Rename or annotate canonical MANIFEST.sha256 as canonical-tree manifest in overlay bundles, and put overlay-manifest verification first in the README.

### rev0841-f12-no-signed-attestation-yet — medium — supply chain / provenance

The artifact has hashes, patches, and validation logs, but no signed attestation that binds artifact digest, builder, inputs, and build recipe. That limits downstream confidence even when checks pass.

Evidence:
- CHECKS/input-artifacts.sha256 and patch hash sidecars exist
- No in-toto/SLSA provenance envelope or signature was found in the overlay root

Change this turn: Recorded as a supply-chain gap.

Recommended next change: Emit in-toto/SLSA provenance for each zip, with subject digest, input artifact digests, builder image/tool versions, build command, and validation summary; sign it outside the ephemeral cloudtainer.

## Standards research notes used in this review

- RO-Crate should describe data for distribution/reuse/publishing/preservation and does not require every file to be modeled when directory or selected-entity modeling is clearer.
- SPDX document namespaces should be unique absolute URIs per document/version, and license-list metadata should be refreshed when regenerating an SPDX document.
- in-toto/SLSA-style attestations are the right next layer for binding artifact digests, inputs, builder, and recipe.
- CITATION.cff is the lightweight missing bridge for human/machine-readable citation metadata once rights are settled.
