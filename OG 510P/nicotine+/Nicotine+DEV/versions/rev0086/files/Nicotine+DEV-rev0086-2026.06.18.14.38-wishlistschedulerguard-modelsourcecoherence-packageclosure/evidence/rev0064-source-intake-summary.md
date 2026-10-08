# rev0064 source-intake helper summary

```json
{
  "critical_file_crosscheck_pass": 15,
  "entry_safety_failures": 0,
  "errors": [],
  "git_identity_pass": 3,
  "lane_summaries_pass": 3,
  "negative_controls_pass": 4,
  "package_hygiene_pass": 5,
  "revision": "rev0064",
  "safe_extraction_roundtrip_pass": 3,
  "source_identity": {
    "exists": true,
    "sha256": "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b",
    "source_zip": "/mnt/data/Nicotine-source(1).zip"
  },
  "source_lane_file_rows": 2139,
  "source_lane_total_bytes": 46605550,
  "source_lane_total_files": 2139,
  "source_zip_entries": 3551,
  "status": "pass"
}
```

Lane summaries and worktree identities are stored in:

```text
data/rev0064_source_lane_summary.csv
data/rev0064_source_lane_git_identity.csv
data/rev0064_source_safe_extraction_roundtrip.csv
data/rev0064_source_critical_file_crosscheck.csv
data/rev0064_source_intake_negative_controls.csv
```
