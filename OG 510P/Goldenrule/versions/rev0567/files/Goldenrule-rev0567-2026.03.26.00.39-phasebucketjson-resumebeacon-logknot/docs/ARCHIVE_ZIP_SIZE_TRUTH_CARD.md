# Archive Zip Size Truth Card

Compact package-size truth surface: distinguish the archive's internal zip proxy from the exact sibling zip bytes on disk, and use the immutable predecessor zip to calibrate the gap without pretending the current head can embed its own final size.

## Headline findings

- The current archive's internal zip proxy remains 4323153 bytes (4.123 MiB), but the exact current head zip bytes stay live-only because embedding them inside that same current-head zip would be self-referential.
- Use `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes` for the exact current head zip size and `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256` for the live digest.
- The immutable predecessor `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip` calibrates the gap: embedded proxy 4310355 bytes versus actual sibling zip 4676506 bytes, a delta of 366151 bytes (0.349189 MiB, share 0.084947).

## Current internal proxy

- approx_revision_zip_bytes: `4323153`
- approx_revision_zip_mebibytes: `4.123`
- raw_bytes: `15734504`
- raw_mebibytes: `15.006`
- selected_matches_current_root_zip: `True`
- exact_current_zip_present: `True`
- current_root_vs_authoritative_head_aligned: `True`

## Live verification commands

- emit_zip_path_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit zip-path`
- emit_size_bytes_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes`
- emit_sha256_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256`

## Immutable predecessor calibration

- zip_name: `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`
- zip_path: `/mnt/data/Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`
- revision_label: `rev0564`
- embedded_proxy_bytes: `4310355`
- actual_external_zip_bytes: `4676506`
- actual_minus_proxy_bytes: `366151`
- actual_minus_proxy_mebibytes: `0.349189`
- actual_over_proxy_ratio: `1.084947`
- actual_minus_proxy_share_of_proxy: `0.084947`
- embedded_guardrail_snapshot_date: `2026-03-23`

## Interpretation

- approx_revision_zip_bytes is a retained-tree packaging proxy used for archive drift and byte budgeting inside the repo.
- the exact current head zip bytes must be read from the sibling zip on disk, not embedded inside the same current-head zip.
- pick the authoritative head zip by revision-first authority, then verify its live bytes with inspect_authoritative_archive_zip.
