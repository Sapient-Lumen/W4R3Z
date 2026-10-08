# rev0066 worklog

- Continued from rev0065.
- Kept the strict/front packet set frozen.
- Added `tools/probe_rev0066_patch_hunk_scope.py`.
- Reran the new hunk-scope helper against `/mnt/data/Nicotine-source(1).zip`: pass.
- Reran inherited rev0065 Git provenance helper against `/mnt/data/Nicotine-source(1).zip`: pass.
- Added patch file-scope, hunk preimage, marker contract, negative-control, package-hygiene, and summary ledgers.
- Added hunk-scope documentation and handoff gate material.
- Refactored the evidence language to distinguish hunk preimage binding from patch roundtrip, patch attribution, patch order, clean-room replay, source intake, and Git provenance.
- Refreshed current public context and retained public path traversal as watch-only context.

Helper summary:

```json
{
  "bundle_patches": 12,
  "errors": [],
  "file_scope_pass": 15,
  "file_scope_rows": 15,
  "hunk_pass": 41,
  "hunk_rows": 41,
  "lanes": 3,
  "marker_pass": 30,
  "marker_rows": 30,
  "negative_controls": 4,
  "negative_controls_pass": 4,
  "package_hygiene_pass": 3,
  "package_hygiene_rows": 3,
  "source_sha256": "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b",
  "source_sha256_expected": "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b",
  "source_sha256_status": "pass",
  "source_zip": "/mnt/data/Nicotine-source(1).zip",
  "status": "pass"
}
```

- Post-extract helper smoke: pass.
