# 162 — Release gates and CI evidence pipeline

**Track:** Shared


This doc defines a **minimum release gate** for this archive so it does not silently drift under
human or LLM edits.

The gate is intentionally boring: it enforces that artifacts remain **internally consistent** and
that external references do not change without notice.

## 162.1 Required checks (MUST pass for any release tag)

### A. Structure + index integrity
- `scripts/check_index.py` (numbered docs must be indexed)
- `scripts/check_tracks.py` (every numbered doc declares a Track)
- `scripts/check_envelope_kinds.py` (example EvidenceEnvelope kinds must be registered)
- `scripts/check_attachment_requirements.py` (required receipt/gossip attachments per kind)
- `scripts/check_receipt_profiles.py` (example receipts must name a registry profile)
- `scripts/check_proof_obligations.py` (claims/hazards may only reference registered POs)

### B. Schema integrity
- `scripts/validate_schemas.py` (JSON schema validity)
- `scripts/gen_schema_catalog.py` (catalog updated)

### C. Source pinning integrity
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

Run from the repository root:

```bash
python3 scripts/check_index.py
python3 scripts/check_tracks.py
python3 scripts/check_envelope_kinds.py
python3 scripts/check_attachment_requirements.py
python3 scripts/check_receipt_profiles.py
python3 scripts/validate_schemas.py
python3 scripts/gen_schema_catalog.py
python3 scripts/verify_external_sources_lock.py
python3 scripts/validate_artifact_refs.py
python3 scripts/build_manifest.py
git diff --exit-code
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
