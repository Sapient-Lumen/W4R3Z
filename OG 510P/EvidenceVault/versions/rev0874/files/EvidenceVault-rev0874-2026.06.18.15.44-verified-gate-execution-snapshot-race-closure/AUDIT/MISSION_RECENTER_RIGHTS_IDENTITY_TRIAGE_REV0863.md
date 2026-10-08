# Mission recenter, rights, identity, and cloudtainer waste triage — rev0863

- Created: `2026-06-17T20:23:47Z` (`2026-06-17T16:23:47-04:00` America/New_York)
- Role: mission/right/identity triage overlay, not a canonical release
- Status: `mission_recentered_publication_block_preserved`

## Heart of the mission

EvidenceVault is a **proof-carrying evidence vault**. Its job is to preserve claims, payload identities, papers, provenance, rights decisions, and verifier context so a future reader can check what is claimed, what supports it, what may be redistributed, and which checks are merely local overlay checks.

The mission is not to make an impressive chain of validators. The validator chain is useful only when it prevents false claims, preserves evidence identity, or moves the bundle closer to lawful, citable, reproducible publication.

## Local evidence parsed this turn

```json
{
  "absolute_path_marker_files_rev0862": 29,
  "absolute_path_marker_hits_rev0862": {
    "/home/oai": 50,
    "/mnt/data": 2720,
    "/tmp/": 36,
    "file:///": 4
  },
  "actual_overlay_bytes_rev0862": 18871668,
  "actual_overlay_files_rev0862": 476,
  "canonical_base_revision_declared_by_release_manifest": "rev0826",
  "canonical_manifest_lines_carried": 4588,
  "canonical_manifest_paths_missing_from_overlay": 4553,
  "canonical_manifest_paths_present_in_overlay": 35,
  "currently_uploaded_evidencevault_zip_count_in_this_cloudtainer": 1,
  "duplicate_copies_rev0862": 1,
  "duplicate_extra_bytes_rev0862": 2747,
  "duplicate_groups_rev0862": 1,
  "makefile_surface_known_missing_script": "scripts/build_papers.sh",
  "overlay_commands_first_heading_rev0862": "# EvidenceVault overlay command surface \u2014 rev0855",
  "readme_first_heading_rev0862": "# EvidenceVault rev0855 streamfold sumcheck payload-gate overlay bundle",
  "rev0862_cloudtainer_zip_receipt_candidate_archive_count": 12,
  "rev0862_cloudtainer_zip_receipt_matches_found": 0,
  "rights_component_count": 9,
  "rights_missing_or_outside_local_license_reference_count": 1,
  "rights_root_license_or_notice_present": false,
  "rights_status": "publication_blocked_pending_rights_decision",
  "spdx_document_namespace": "https://example.invalid/evidencevault/rev0826/spdx/file-inventory",
  "spdx_file_records": 4585,
  "spdx_package_records": 0,
  "streamfold_full_payload_bytes_expected": 25066,
  "streamfold_full_payloads_expected": 17,
  "streamfold_full_payloads_missing": 17,
  "streamfold_minimum_payload_bytes_expected": 7751,
  "streamfold_minimum_payloads_expected": 4,
  "streamfold_minimum_payloads_missing": 4,
  "unique_blob_count_rev0862": 475,
  "uploaded_bundle_sha256": "266fc3876b0b09c0b8eb2182061ac386120873a502aa0ca7928a89129cf0833a"
}
```

## What is missing

1. Owner-approved rights decisions: root `LICENSE`/`NOTICE`, component conclusions, and the missing PACT local license target decision.
2. A stable overlay/patch-bundle identity separate from the carried rev0826 canonical release metadata. rev0863 adds `PATCH_BUNDLE_MANIFEST.json` as a first repair.
3. A signed external attestation. The current in-toto/SLSA-shaped statements are useful local records but are not externally signed release attestations.
4. A release-grade SBOM. The carried SPDX file is still a file inventory with zero package records.
5. A citation/authorship/DOI bridge, after rights and authorship decisions.
6. A stop condition for proofcore hardening while the active streamfold payload bytes remain absent.

## Findings and recommended changes

### `rev0863-f01-heart-is-proof-carrying-evidence-preservation` — strategic — mission

Finding: The heart of EvidenceVault is a proof-carrying evidence vault: preserve claims, payload identities, papers, provenance, rights decisions, and verifier context so future readers can distinguish evidence integrity from mathematical proof and publication permission.

Recommended change: Make rights, identity, and provenance closure the default session agenda; proofcore hardening should be justified only when it directly reduces payload recovery risk or prevents overclaiming.

### `rev0863-f02-rights-remain-the-publication-blocker` — blocker — rights

Finding: Rights remain blocked: no root LICENSE/COPYING/NOTICE exists, all 9 components remain NOASSERTION, and one local license reference target is missing or outside the archive.

Recommended change: Use RIGHTS/RIGHTS_DECISION_PACKET_REV0863.* as the next human-owner packet; do not add a license file unless the owner/upstream decision is explicit.

### `rev0863-f03-overlay-canonical-identity-confusion-is-still-severe` — high — identity

Finding: The ZIP is a rev0862 overlay, while RELEASE_MANIFEST.json and ro-crate-metadata.json still describe rev0826 canonical surfaces. The README and command file also opened at rev0855 before this revision.

Recommended change: Add and maintain PATCH_BUNDLE_MANIFEST.json as the overlay package identity, and keep canonical dataset identity separate from overlay review identity.

### `rev0863-f04-proofcore-work-drifted-after-rev0851-warning` — high — portfolio-focus

Finding: rev0851 warned that validator work could become a substitute for decisive blockers. rev0852 through rev0862 added useful proofcore/payload-search layers, but the active streamfold lane still has 17/17 full payloads missing and the minimum 4-file recovery set missing.

Recommended change: Introduce a stop condition: no new proofcore lane unless it either admits real candidate bytes, removes a false claim, or shortens the rights/identity/provenance closure path.

### `rev0863-f05-command-surface-trap-can-waste-operator-time` — high — operator-ergonomics

Finding: The carried canonical Makefile is not the overlay entrypoint; scripts/build_papers.sh is absent, so the makefile surface is known to fail in this overlay-only ZIP.

Recommended change: Keep OVERLAY_COMMANDS.md as the authoritative overlay entrypoint and keep its newest revision at the top; do not ask operators to start with make gate.

### `rev0863-f06-cloudtainer-negative-search-is-historical-not-portable` — medium — payload-recovery

Finding: The rev0862 ZIP search receipt records 12 EvidenceVault ZIP artifacts scanned during construction, but this current uploaded cloudtainer view exposes only the rev0862 uploaded ZIP. The receipt is useful historical evidence, not a reproducible claim about the current workspace.

Recommended change: For future candidate archives, attach source artifacts or at least a candidate-source ledger with basenames, SHA-256 digests, and acquisition notes; rerun archive search when sources are actually present.

### `rev0863-f07-sbom-is-inventory-not-release-grade-bom` — medium — SBOM

Finding: The carried SPDX surface has 4585 file records and 0 package records under an example.invalid rev0826 namespace. It is a file inventory, not a package/component SBOM with concluded licenses.

Recommended change: After rights closure, regenerate SPDX around components/packages, relationships, license conclusions, copyright text, and a real artifact namespace.

### `rev0863-f08-citation-and-authorship-bridge-still-missing` — medium — citation

Finding: There is still no root CITATION.cff/AUTHORS/CONTRIBUTORS/DOI bridge for eventual public consumption.

Recommended change: Stage a citation/authorship worksheet, but do not publish a final CITATION.cff until rights and authorship are resolved.

### `rev0863-f09-historical-patch-and-path-noise-should-be-frozen` — medium — cloudtainer-waste

Finding: Current duplicate payload waste is low, but the bundle still carries a 5.8 MB cumulative patch and thousands of local path markers across historical surfaces. Revalidating those surfaces every session can distract from closure work.

Recommended change: Freeze historical patch-chain evidence, keep only targeted active checks in normal sessions, and regenerate cumulative/historical artifacts only during a formal canonical patch cycle.


## Speculative read

The project looks like it has been doing high-quality **comfort work**: validators, parent replay, transcript framing, symlink controls, archive locators. Those are not useless; several are genuinely protective. But rev0851 already named the danger: code can be improved inside the cloudtainer while rights and identity closure require human decisions. From rev0852 through rev0862, the project mostly returned to what the cloudtainer can do alone.

The healthiest next move is to treat proofcore as a guardrail, not the main road. A new proofcore lane should require one of three triggers: real candidate payload bytes, removal of a dangerous false claim, or direct support for publication identity/provenance closure.

## Research notes

- RO-Crate: https://www.researchobject.org/ro-crate/specification/1.2/introduction.html — EvidenceVault should keep using RO-Crate-like metadata, but the overlay ZIP needs its own Dataset/patch-bundle identity rather than relying on a carried rev0826 canonical RO-Crate surface.
- SPDX NOASSERTION: https://spdx.github.io/spdx-spec/v3.0.1/model/ExpandedLicensing/Individuals/NoAssertionLicense/ — NOASSERTION is an honest unknown/withheld/undetermined value, not a license grant and not publication clearance.
- REUSE licensing metadata: https://reuse.software/spec-3.3/ — A future rights closure should move from sparse evidence scanning to per-file or per-component machine-readable licensing decisions.
- SLSA provenance: https://slsa.dev/spec/v1.0/provenance — The in-toto/SLSA-shaped JSON is useful as local provenance shape, but an unsigned cloudtainer-local statement should not be described as release-grade attestation.
- FAIR data: https://www.go-fair.org/fair-principles/ — The strongest FAIR gap is reusability: clear usage license, rich metadata, provenance, and community-standard packaging are all still incomplete.
- Citation File Format: https://citation-file-format.github.io/ — A CITATION.cff bridge should be staged after rights/authorship decisions, not invented early.
- Sumcheck/Fiat-Shamir caution: https://lance.fortnow.com/papers/files/ip.pdf — The proofcore lanes should keep their current non-claim posture: toy transparent sumcheck/transcript checks are not a production SNARK or streamfold correctness proof.

## Next-session priority order

1. Work from `RIGHTS/RIGHTS_DECISION_PACKET_REV0863.*` and record owner/upstream decisions without inventing licenses.
2. Keep `PATCH_BUNDLE_MANIFEST.json` current so the overlay ZIP has a first-class identity separate from canonical rev0826 metadata.
3. Freeze new proofcore lanes until candidate payload bytes or a concrete verifier/payload edge appears.
4. When candidate ZIP/cache/source artifacts are mounted, rerun the rev0862 archive locator on those actual sources and keep a portable source ledger.
5. After rights closure, regenerate RO-Crate, SPDX, and citation surfaces from one rights/source/authorship table.

## Non-claims

This revision does not grant rights, recover streamfold payloads, unblock publication, add a root license, add a SNARK, add zero knowledge, prove streamfold correctness, or provide a signed external attestation.
