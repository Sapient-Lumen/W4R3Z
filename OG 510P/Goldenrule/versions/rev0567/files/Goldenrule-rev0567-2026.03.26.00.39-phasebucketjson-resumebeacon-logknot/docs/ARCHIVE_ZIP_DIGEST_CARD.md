# Archive Zip Digest Card

Compact external-zip verification surface: once the authoritative sibling Golden Rule revision zip is known, publish either a stable embedded digest (for older sibling zips) or the exact live verification commands (for the current self-referential head zip).

## Headline findings

- The authoritative sibling zip remains the live current-root package `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip` at `/mnt/data/Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`.
- Because this card is embedded inside that same current-head zip, a stable embedded size or SHA-256 would be self-referential and cannot be trusted as a fixed point.
- Use `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes` and `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256` against the sibling zip on disk when you need the live bytes verified.
- For one-command winner verification, run `python3 scripts/tools/verify_authoritative_archive_zip.py`.

## Selected authoritative zip verification surface

- selected_zip_name: `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`
- selected_zip_path: `/mnt/data/Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`
- matches_current_root_zip: `True`
- embedded_digest_stable: `False`
- embedded_size_bytes: `None`
- embedded_sha256: `None`
- live_emit_size_bytes_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes`
- live_emit_sha256_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256`
- verify_zip_command: `python3 scripts/tools/verify_authoritative_archive_zip.py`
- exact_current_zip_present: `True`
- current_root_vs_authoritative_head_aligned: `True`
- timestamp_head_matches_authoritative_head: `True`
- duplicate_revision_count: `1`
- adjacent_revision_timestamp_inversion_count: `0`

## Stewardship

- open_doc: `docs/ARCHIVE_ZIP_DIGEST_CARD.md`
- inspect_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py`
- emit_sha256_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256`
- emit_size_bytes_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes`
- emit_zip_path_command: `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit zip-path`
- verify_zip_command: `python3 scripts/tools/verify_authoritative_archive_zip.py`

## Why this card exists

- The archive already resolves which sibling zip should win authority, but an inheritor may still need an exact verification surface for the selected zip bytes.
- Current-head zips are self-referential if they try to embed their own final digest inside themselves, so this card deliberately degrades to live verification commands in that case instead of pretending a false fixed point exists.
- Older sibling zips do not have that self-reference problem, so their size and SHA-256 can still be embedded directly when they remain the authoritative external head.

