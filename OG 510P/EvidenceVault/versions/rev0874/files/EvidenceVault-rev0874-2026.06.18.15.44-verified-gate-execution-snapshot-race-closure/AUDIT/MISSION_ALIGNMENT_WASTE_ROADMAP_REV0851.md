# Mission alignment, missing pieces, and cloudtainer waste roadmap — rev0851

- Created: `2026-06-16T15:51:30Z` (`2026-06-16T11:51:30-0400` America/New_York)
- Role: overlay/patch review bundle, not a canonical release
- Status: `mission_alignment_review_publication_block_preserved`

## Heart of the mission

EvidenceVault should be a trustworthy research-object vault. Its job is not merely to make a ZIP pass validators; it is to preserve evidence, papers, code snapshots, curated artifacts, claims, obligations, rights decisions, provenance, and replay context so a future reader can determine what was claimed, what evidence supports it, what may be redistributed, and how the release was produced.

The current overlay machinery is useful when it protects that mission. It becomes waste when it adds another layer of internal proof while the decisive publication blockers remain human rights clearance, artifact identity, signed provenance, and clear operator ergonomics.

## Parsed local evidence

```json
{
  "absolute_path_marker_files": 39,
  "absolute_path_marker_hits": 2895,
  "absolute_path_marker_top5": [
    {
      "hits": 2689,
      "path": "PATCHES/rev0826-to-rev0840-cumulative.patch"
    },
    {
      "hits": 45,
      "path": "PATCHES/rev0849-to-rev0850-overlay.patch"
    },
    {
      "hits": 45,
      "path": "PATCHES/rev0840-to-rev0841-overlay.patch"
    },
    {
      "hits": 18,
      "path": "AUDIT/OVERLAY_ABSOLUTE_PATH_REFERENCE_AUDIT_REV0841.json"
    },
    {
      "hits": 16,
      "path": "PATCHES/rev0846-to-rev0847-overlay.patch"
    }
  ],
  "canonical_manifest_lines_carried": 4588,
  "canonical_manifest_paths_missing_from_overlay": 4553,
  "canonical_manifest_paths_present_in_overlay": 35,
  "dedupe_duplicate_copies": 460,
  "dedupe_duplicate_extra_bytes": 3762513,
  "dedupe_files_scanned": 4584,
  "dedupe_unique_blobs": 4124,
  "index_rows_carried": 4586,
  "largest_patch": {
    "bytes": 5831935,
    "path": "PATCHES/rev0826-to-rev0840-cumulative.patch"
  },
  "overlay_bytes_actual_pre_rev0851": 13993385,
  "overlay_files_actual_pre_rev0851": 177,
  "overlay_manifest_file_count_pre_rev0851": 175,
  "patch_bytes_pre_rev0851": 6750098,
  "patch_count_pre_rev0851": 12,
  "rights_blockers": [
    "missing_root_license_or_notice",
    "missing_local_license_reference_targets"
  ],
  "rights_component_count": 9,
  "rights_observed_bytes": 97348463,
  "rights_observed_files": 4045,
  "rights_status": "publication_blocked_pending_rights_decision",
  "spdx_document_namespace": "https://example.invalid/evidencevault/rev0826/spdx/file-inventory",
  "spdx_file_inventory_files": 4585,
  "spdx_package_count": 0
}
```

## What is missing

1. Owner-approved rights decisions: root `LICENSE`/`NOTICE`, component conclusions, copyright text, and the missing PACT local license target decision.
2. A first-class patch-bundle identity separate from canonical dataset identity. The overlay carries rev0826 canonical metadata and rev0851 overlay evidence at the same time.
3. A signed external attestation. Current in-toto/SLSA-shaped files are useful but unsigned and cloudtainer-local.
4. A release-grade SBOM. The carried SPDX file is a large file inventory with zero packages, not yet a component/package BOM.
5. Citation/authorship/DOI bridge surfaces for eventual publication.
6. An overlay-local command surface. The canonical `Makefile` is carried but is not a complete runnable surface in this overlay-only ZIP.
7. A resource budget. Repeated full-tree scans and duplicate generated surfaces are already visible cloudtainer waste.

## Findings and changes

### rev0851-f01-heart-is-evidence-preservation-not-publication-throughput — strategic — mission

Finding: The durable mission is to preserve a research/evidence object with verifiable provenance, claims, sources, papers, and publication gates; the current overlay work is valuable only insofar as it protects that evidence object.

Recommended change: Move the next sessions from additional micro-hardening toward a rights/identity/provenance closure plan with explicit stop conditions for infrastructure-only work.

### rev0851-f02-publication-block-remains-the-central-blocker — blocker — rights

Finding: The bundle correctly remains blocked: no owner-approved root LICENSE/COPYING/NOTICE exists, component conclusions are NOASSERTION, and the carried ledger still records one missing local rights target.

Recommended change: Resolve the human rights decision first: owner-approved root license/notice, component license conclusions, PACT missing LICENSE target decision, then regenerate RIGHTS, SPDX, and RO-Crate from one source of truth.

### rev0851-f03-overlay-command-surface-ambiguity — high — operator ergonomics

Finding: The carried canonical Makefile is misleading inside the overlay: `scripts/validate_makefile_surface.py` fails immediately because canonical scripts such as scripts/build_papers.sh are absent from the overlay ZIP.

Recommended change: Treat OVERLAY_COMMANDS.md as the overlay command surface and eventually split canonical Makefile validation from overlay command validation.

### rev0851-f04-overlay-vs-canonical-identity-still-split — high — identity

Finding: The ZIP is rev0851/rev0850 overlay lineage, while RELEASE_MANIFEST.json, RO-Crate, MANIFEST.sha256, and SPDX still describe rev0826 canonical surfaces. This is understandable for a patch bundle but still easy to misread.

Recommended change: Add or promote a PATCH_BUNDLE_MANIFEST/RO-Crate overlay Dataset entity; keep canonical dataset identity and overlay package identity as separate signed subjects.

### rev0851-f05-sbom-is-inventory-not-supply-chain-bom — medium — SBOM

Finding: The carried SPDX file inventory has 4585 file records, 0 package records, and a rev0826 example.invalid namespace. It is useful inventory evidence, not a release-grade package/component SBOM.

Recommended change: After rights closure, regenerate SPDX with packages/components, relationships, license conclusions, copyright text, and an artifact-specific namespace.

### rev0851-f06-cloudtainer-waste-from-repeated-scans-and_duplicate_payloads — medium — performance

Finding: Prior validation logs reported a roughly 329.49s gate with rebuild_indexes around 106.25s, while DEDUPE_REPORT records 460 duplicate copies and 3,762,513 duplicate extra bytes. Repeating whole-tree scans in an overlay workflow is wasteful.

Recommended change: Add content-addressed scan cache/checkpoints, separate overlay-targeted checks from canonical full-tree checks, and consume generated summaries instead of rescanning when inputs are unchanged.

### rev0851-f07-historical_absolute_paths_are_quarantined_not_fixed — medium — portability/privacy

Finding: There are 2895 cloudtainer/path marker hits across 39 files, mostly in the historical cumulative patch. This is currently documented rather than fixed to avoid rewriting validated historical patches.

Recommended change: When the next canonical patch cycle is cut, regenerate cumulative patches from relative roots and classify historical provenance paths separately from active payload paths.

### rev0851-f08-citation_and_authorship_bridge_missing — low — citation

Finding: No root CITATION.cff/AUTHORS/CONTRIBUTORS/DOI bridge is present in the overlay. That is acceptable while rights are blocked, but it is missing for eventual publication.

Recommended change: After rights decisions, add CITATION.cff, AUTHORS/CONTRIBUTORS, and a DOI/release mapping that distinguishes canonical dataset releases from overlay patches.

## Speculative read

The project looks like it has been using validator work as a safe substitute for rights work. That is psychologically understandable: code can be improved inside the cloudtainer, while license decisions require a human owner/upstream review. But from rev0851 onward, more micro-hardening should be treated as secondary unless it directly supports rights closure, identity separation, or signed reproducibility.

The other strong pattern is overlay/canonical ambiguity. It has been documented repeatedly, but the carried `Makefile`, `MANIFEST.sha256`, `INDEX/files.*`, SPDX, and RO-Crate still make the overlay look more canonical than it is. The fix is not another warning paragraph alone; the fix is a separate overlay manifest/RO-Crate entity/command surface that is impossible to confuse with the canonical dataset.

## Research notes

- RO-Crate 1.2 Introduction: https://www.researchobject.org/ro-crate/specification/1.2/introduction.html — RO-Crate is meant to aggregate and describe data for distribution, reuse, publishing, preservation, and archiving.
- SPDX overview: https://spdx.dev/about/overview/ — SPDX is a standard for SBOM information including provenance, license, security, and related information.
- SPDX NoAssertionLicense: https://spdx.github.io/spdx-spec/v3.0.1/model/ExpandedLicensing/Individuals/NoAssertionLicense/ — NOASSERTION means no assertion is made about the actual license value.
- Citation File Format: https://citation-file-format.github.io/ — CITATION.cff is human- and machine-readable citation metadata for software and datasets.
- SLSA Provenance v1.0: https://slsa.dev/spec/v1.0/provenance — Provenance attests that a build platform produced artifacts through a build definition.
- GO FAIR Principles: https://www.go-fair.org/fair-principles/ — Reusable data needs well-described metadata so it can be replicated or combined.
- REUSE Specification 3.3: https://reuse.software/spec-3.3/ — REUSE aims for comprehensive, unambiguous, human- and machine-readable copyright and licensing information per file.
- Software Heritage: https://www.softwareheritage.org/ — Software Heritage preserves source code for present and future generations.
- GitHub Docs: Referencing and citing content: https://docs.github.com/repositories/archiving-a-github-repository/referencing-and-citing-content — Zenodo can archive repository releases and issue DOIs for them.

## Next session priorities

1. Build a rights-decision packet from `RIGHTS/license_evidence_scan.json` and `RIGHTS/component_license_ledger.json`, with no invented licenses.
2. Add a `PATCH_BUNDLE_MANIFEST.json` or RO-Crate overlay Dataset entity that has its own subject digest, inputs, patches, and validation logs.
3. Introduce a content-addressed cache for expensive scans and an overlay-only validation runner.
4. Add an explicit `--explain-blocked` or `--plan-only` publication mode that never mutates and never claims publishability.
5. Prepare citation/authorship metadata after rights decisions, not before.
