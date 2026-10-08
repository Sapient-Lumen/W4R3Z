# Archive Zip Authority Card

Compact sibling-zip reopen surface: choose one authoritative external revision zip to reopen, even when revision labels are duplicated or timestamps do not stay monotone across revisions.

## Headline findings

- The authoritative sibling zip to reopen is `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`, and its exact path is `/mnt/data/Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`.
- Archive head authority stays revision-first: `prefer highest revision label for archive head; use timestamp only to order multiple zips that share the same revision label`; timestamp_head_matches_authoritative_head=True.
- Visible external hazards remain duplicate_revision_count=1 and adjacent_revision_timestamp_inversion_count=0, so stewards should not pick the reopen target by timestamp alone.

## Selected authoritative zip

- selected_zip_name: `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`
- selected_zip_path: `/mnt/data/Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`
- selected_root_stem: `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot`
- immediate_predecessor_zip: `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`
- current_root_vs_authoritative_head_aligned: `False`
- exact_current_zip_present: `True`

## Resolution rule

- authority_rule: `prefer highest revision label for archive head; use timestamp only to order multiple zips that share the same revision label`
- scan sibling Golden Rule revision zips in the configured directory
- choose the highest revision label as archive head
- if a revision label is duplicated, break ties by timestamp inside that revision label only
- do not let duplicated revision labels collapse authority; keep timestamp tie-breaking inside the duplicated label only

## Recommended reopen commands

- resolve_command: `python3 scripts/tools/resolve_authoritative_archive_zip.py`
- emit_zip_path_command: `python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path`
- emit_unzip_command: `python3 scripts/tools/resolve_authoritative_archive_zip.py --emit unzip-command`
- resume_unzip_command: `mkdir -p /path/to/workdir && unzip -q /mnt/data/Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip -d /path/to/workdir`

## Visible external hazards

- duplicate_revision_count: `1`
- adjacent_revision_timestamp_inversion_count: `0`
- timestamp_head_matches_authoritative_head: `True`

### Duplicate revision rows

- `rev0562` appears 2 times: `Goldenrule-rev0562-2026.03.25.19.13-localrootsfetch-pruneladder.zip`, `Goldenrule-rev0562-2026.03.25.23.12-userspacerustup-livebridge.zip`
