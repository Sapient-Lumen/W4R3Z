# Archive Zip Lineage Card

Compact external package-lane audit: confirm whether the sibling revision zips agree with the live root, identify the immediate predecessor zip, and flag any reused revision labels that can make archive-head recovery ambiguous from filenames alone.

## Headline findings

- The authoritative sibling zip head in `/mnt/data` is `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`, and it aligns_with_live_root=False.
- The exact current-root zip `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip` is present=True; the immediate predecessor zip is `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`.
- Sibling zip lineage contains 1 duplicated revision labels (rev0562), so revision reuse must be treated as an external package risk.

## Current live root

- root_name: `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal`
- revision_label: `rev0565`
- expected_zip_name: `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`

## External zip authority

- scan_dir: `/mnt/data`
- authoritative_external_head: `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`
- authoritative_revision_label: `rev0566`
- authoritative_timestamp: `2026.03.26.00.24`
- aligns_with_live_root: `False`
- exact_current_zip_present: `True`
- immediate_predecessor_zip: `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`

## Duplicate revision labels among sibling zips

- `rev0562` appears 2 times: `Goldenrule-rev0562-2026.03.25.19.13-localrootsfetch-pruneladder.zip`, `Goldenrule-rev0562-2026.03.25.23.12-userspacerustup-livebridge.zip`

## Steward commands

- audit_command: `python3 scripts/tools/audit_archive_zip_lineage.py`
- canonical_cut_command: `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`

## Tail of sibling zip lineage

- `rev0560` @ `2026.03.24.05.13` — `Goldenrule-rev0560-2026.03.24.05.13-proofbudget-citationbytes.zip`
- `rev0561` @ `2026.03.25.22.47` — `Goldenrule-rev0561-2026.03.25.22.47-rustupdetour-shadowcomeback.zip`
- `rev0562` @ `2026.03.25.19.13` — `Goldenrule-rev0562-2026.03.25.19.13-localrootsfetch-pruneladder.zip`
- `rev0562` @ `2026.03.25.23.12` — `Goldenrule-rev0562-2026.03.25.23.12-userspacerustup-livebridge.zip`
- `rev0563` @ `2026.03.25.23.23` — `Goldenrule-rev0563-2026.03.25.23.23-registryonlysurface-fetchtripwire.zip`
- `rev0564` @ `2026.03.25.23.43` — `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`
- `rev0565` @ `2026.03.25.23.58` — `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`
- `rev0566` @ `2026.03.26.00.24` — `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`
