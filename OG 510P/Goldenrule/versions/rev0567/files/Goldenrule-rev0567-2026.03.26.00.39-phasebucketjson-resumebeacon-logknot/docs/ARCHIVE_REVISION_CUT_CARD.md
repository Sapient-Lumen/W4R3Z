# Archive Revision Cut Card

Compact naming-and-cutover card for future package stewards: confirm the current head is safe to increment, derive the next normalized revision label, and stamp the exact next root/zip name without reusing an old revision number or ad-libbing the filename shape.

## Headline findings

- Current archive head `rev0565` is changelog-aligned, so the next safe label is `rev0566` rather than reusing any existing revision number.
- Normalized cut names must continue to match `^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)$` with descriptor slugs constrained by `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Use `make settle-archive-truth` before the final rename/zip step so the package-boundary truth surfaces settle on the live tree first.
- Use `python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug` to stamp the exact next root/zip name; the card template is `Goldenrule-rev0566-YYYY.MM.DD.HH.MM-descriptor-slug`.
- Use `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"` when you want the final settle + changelog append + rename + zip step executed from one command rather than by hand.
- Package boundary is still ready=True with pdf_count=0 and scratch_file_count=0.

## Current head and alignment

- root_name: `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal`
- revision_label: `rev0565`
- timestamp: `2026.03.25.23.58`
- descriptor_slug: `offlineproofladder-cachetruth-nightsignal`
- changelog_aligned_to_root: `True`
- latest_recorded_revision: `rev0565` (2026-03-25)
- immediate_predecessor_revision: `rev0564` (2026-03-25)

Recent changelog chain tail:

- `rev0560` (2026-03-24)
- `rev0561` (2026-03-25)
- `rev0562` (2026-03-25)
- `rev0563` (2026-03-25)
- `rev0564` (2026-03-25)
- `rev0564` (2026-03-25)
- `rev0565` (2026-03-25)

## Next revision naming contract

- next_revision_label: `rev0566`
- root_pattern: `^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)$`
- descriptor_pattern: `^[a-z0-9]+(?:-[a-z0-9]+)*$`
- timestamp_pattern: `^\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}$`
- template_root_name: `Goldenrule-rev0566-YYYY.MM.DD.HH.MM-descriptor-slug`
- template_zip_name: `Goldenrule-rev0566-YYYY.MM.DD.HH.MM-descriptor-slug.zip`

Planner invocation:

- `python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug`
- `python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"`
- Example exact root name if you reuse the current minute with the safe descriptor `normalized-nextname`: `Goldenrule-rev0566-2026.03.25.23.58-normalized-nextname`
- Example exact zip name: `Goldenrule-rev0566-2026.03.25.23.58-normalized-nextname.zip`

## Cut prerequisites

- settle_command: `make settle-archive-truth`
- package_boundary_ready: `True`
- pdf_count: `0`
- scratch_file_count: `0`
- require_changelog_alignment: `True`
- require_descriptor_slug: `True`
- require_utc_minute_stamp: `True`
- rename_before_final_reentry_validation: `True`

## Source surfaces

- `artifacts/reports/archive_package_cut_card.json`
- `artifacts/reports/archive_size_guardrail_card.json`
- `docs/ARCHIVE_PACKAGE_CUT_CARD.md`
- `docs/ARCHIVE_REENTRY_CARD.md`
- `CHANGELOG.md`
- `scripts/tools/plan_archive_revision_cut.py`
- `scripts/tools/cut_archive_revision.py`
