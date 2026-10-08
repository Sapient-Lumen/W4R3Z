---
project: Immoral Wealth
status: validation_report
claim_kind: archive_integrity_receipt
revision_current: rev0356
generated_at: 2026-06-18T08:38:13Z
---

# Validation report — rev0356

Command: `python tools/validate_archive.py`

Result: **PASSED: 0 errors, 0 warnings**

Rev0356 adds generic checks for exact live-count surfaces, code-formatted entrypoint paths, complete archive indexes, a non-circular complete manifest, manifest byte/hash equality, and `MANIFEST.sha256` consistency. It also checks the paired mission/evidence/cloudtainer audit and requires a single current-revision declaration.

## Important limit

This result certifies structural and release invariants. It does **not** certify that every source semantically proves every associated claim. The archive currently contains **6793 mechanical evidence associations**; claim-level locators, stance, quotations/extractions, and contrary-evidence review remain a staged migration described in `reports/mission-heart-evidence-integrity-and-cloudtainer-pruning-map-rev0356.md`.

## Packaging verification

The linked archive `Immoral-Wealth-rev0356-2026.06.18.04.37-mission-heart-evidence-integrity-and-cloudtainer-pruning-map.zip` was tested with `unzip -t`, extracted into a clean directory, and validated from the extracted copy with **PASSED: 0 errors, 0 warnings**.
