# 162 — Release gates and CI evidence pipeline

**Track:** Shared


This doc defines a **minimum release gate** for this archive so it does not silently drift under
human or LLM edits.

The gate is intentionally boring: it enforces that artifacts remain **internally consistent** and
that external references do not change without notice.

## 162.1 Required checks (MUST pass for any release tag)

Canonical step order is defined by `scripts/release_gate.py` (treat it as authoritative to avoid doc drift).

### A. Structure + index integrity
- `scripts/check_index.py` (numbered docs must be indexed)
- `scripts/check_tracks.py` (every numbered doc declares a Track)
- `scripts/check_adr_index.py` (ADR drift firewall: every ADR file is indexed and has Status/Date; prevents silent decision drift)
- `scripts/gen_track_bundles.py` (curated bundle entrypoints must resolve; no broken links)
- `scripts/check_doc_links.py` (relative markdown links must resolve; prevents quiet link-rot)
- `scripts/check_no_raw_urls_modern_docs.py` (for docs >=170, require `source:` citations instead of raw external URLs)
- `scripts/check_no_cache_artifacts.py` (fail if __pycache__/pyc or evidence/cache payloads are present)
- `scripts/check_no_symlinks.py` (fail if any symlinks are present; prevents non-portable bundles and symlink escape reads)
- `scripts/check_envelope_kinds.py` (example EvidenceEnvelope kinds must be registered)
- `scripts/check_doc_envelope_kind_references.py` (doc references using `kind:` / `Envelope kind:` must refer to registered kinds)
- `scripts/check_envelope_payload_schemas.py` (envelope kinds must point to real schemas)
- `scripts/check_attachment_requirements.py` (required receipt/gossip attachments per kind)
- `scripts/check_attachment_registry_integrity.py` (attachment requirements registry must reference known kinds and existing schemas; no duplicate kind+rel rows)
- `scripts/check_example_packets.py` (example evidence packets must verify offline; prevents rot)
- `scripts/check_example_report_pins.py` (drift firewall: verifier-report example pins + tool version must match canonical registry bytes and VERSION)
- `scripts/check_operator_tools_smoke.py` (operator-facing card tools must run cleanly on shipped example packets)
- `scripts/check_packet_paths.py` (fail if example packets contain unsafe relative paths)
- `scripts/check_object_uri_alignment.py` (example packets: object store integrity — URIs and bytes match declared digests; no orphan objects)
- `scripts/check_receipt_profiles.py` (example receipts must name a registry profile)
- `scripts/check_drill_scenarios.py` (drill scenario registry integrity: triggers, notice types, kinds, file refs)
- `scripts/check_known_issues_registry.py` (known-issues registry integrity: status enum + file refs; used for patch/mitigation transparency)
- `scripts/check_official_channels_registry.py` (official-channels registry integrity: canonical comms surfaces for PublicNotice channel IDs)
- `scripts/check_proof_obligations.py` (claims/hazards may only reference registered POs)
- `scripts/check_tombstones.py` (tombstone aliases must be minimal and point to a live target)
- `scripts/check_no_private_keys.py` (fail if any private key material is present)
- `scripts/check_jcs_vectors.py` (drift tripwire for RFC8785 canonicalization rules)
- `scripts/check_envelope_vectors.py` (drift tripwire for EvidenceEnvelope payload/tbs digests)
- `scripts/check_version_consistency.py` (VERSION/CHANGELOG/START_HERE must agree)
- `scripts/check_packet_verification_report_linkage.py` (drift firewall: `observer_verify_packet.py` must emit `verifier_report_tbs_digest` when requested)
- `scripts/check_size_budget.py` (reject accidental archive bloat)

Registry reference: the canonical CSV registries live under `artifacts/registries/` and are documented in `artifacts/registries/README.md`.

### B. Schema integrity
- `scripts/validate_schemas.py` (schema meta-validation; validates a small set of ship examples when `jsonschema` is available)
- `scripts/gen_schema_catalog.py` (catalog updated)
- `scripts/gen_public_surface_index.py` (public surfaces index updated)
- `scripts/gen_evidence_object_catalog.py` (evidence object catalog updated)
- `scripts/check_verifier_problem_codes_registry.py` (verifier problem-code registry is strict + sorted)
- `scripts/gen_verifier_problem_codes.py` (publishable verifier problem-code list updated)

### C. Source pinning integrity
- `scripts/check_external_sources_lockfile.py` (lockfile hygiene + verify `source: <id>` citations resolve)
- `scripts/check_unused_sources.py` (fail if any lockfile source id is unused; keeps the lockfile lean)
- `scripts/verify_external_sources_lock.py` (lockfile entries parse; sha256 verified when local copy exists)

### D. Evidence-reference integrity
- `scripts/validate_artifact_refs.py` verifies that references in:
  - `artifacts/claims/claim-evidence-matrix.csv`
  - `artifacts/hazards/hazard-register.csv`
  resolve to real files.

### E. Manifest integrity
- `scripts/build_manifest.py` regenerates `MANIFEST.sha256`
- `MANIFEST.sha256` MUST match the working tree

## 162.2 Suggested evidence lanes (optional but recommended)
- “Adversary simulation” lane for partition / split-world / censorship drills
- “Publication deadline” lane for MMD-style evidence delivery
- “Observer kit offline verification” lane

## 162.3 A minimal CI recipe (copy/paste friendly)

One-command gate (authoritative step list lives in the script):

```bash
python3 scripts/release_gate.py
```

To regenerate the manifest (for maintainers when cutting a release ZIP):

```bash
python3 scripts/release_gate.py --write-manifest
```

## 162.4 When a check fails
Treat failures as **drift alerts**:
- open an ADR if the failure reflects a real policy change
- otherwise fix the artifact so the archive remains self-consistent


## 162.5 Evidence packet publishing (recommended)
When preparing a public bundle for an election or drill:
- build a content-addressed packet and manifest using `tools/evidence_packager.py` (see `docs/173`)
- publish a coverage report using `tools/coverage_accounting.py` (see `docs/174`)

These steps are not required for *every* repo release tag, but they are required for any claim of “court-usable evidence package”.

## 162.6 Deterministic release archives (recommended)
When publishing this repository as a ZIP, prefer a deterministic build so releases are reproducible
(stable file order + stable timestamps).

```bash
python3 scripts/build_release_zip.py
```

This writes `dist/The-Election-Stack_<VERSION>.zip` and excludes known non-normative cache paths.
