# 653. Source-reference parser lockfile closure and xref reconstruction

**Track:** Shared / Evidence hygiene

This document records the v780 reconstruction pass for external-source discipline. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The release archive had a real evidence-control seam: several scripts scanned lockfile references with slightly different regular expressions. The strict release checker recognized simple `source: id` / `xref: id` shapes, while maintainer prose increasingly used backticked IDs and multi-ID citation clusters. That meant a non-blocking source-usage report could see references that the blocking checker did not enforce.

The failure mode is subtle: the archive can appear source-disciplined while a backticked or clustered ID remains outside the lockfile, or while an unpinned entry is still described as a normative `source:` instead of an informative `xref:`.

## Reconstruction rule

The parser now lives in one shared helper: `scripts/_shared/source_refs.py`.

All lockfile-reference scanners should use that helper rather than inventing local citation regexes. The helper recognizes compact markdown citation shapes, including inline-code citations and multi-ID groups, while avoiding placeholder examples such as `source: <id>`.

Updated consumers:

- `scripts/check_external_sources_lockfile.py`
- `scripts/check_recent_backticked_lockfile_citations.py`
- `scripts/check_unused_sources.py`
- `scripts/report_source_usage.py`
- `scripts/gen_external_sources_index.py`
- `scripts/check_track_a_pinned_sources.py`

## Closure behavior

This revision applies three repairs.

1. **Alias collapse:** duplicate semantic IDs were remapped to existing lockfile IDs instead of adding new aliases. Examples include Rekor, SCITT, in-toto/DSSE envelope posture, and EAC accessibility pages.
2. **Lockfile closure:** remaining cited IDs were added to `evidence/lock/external-sources.toml` as compact unpinned entries with bounded review windows.
3. **Normative/informative separation:** citation clusters that point at unpinned material were downgraded from `source:` to `xref:`. Pinned bytes remain eligible for `source:`; mutable pages and unpinned PDFs do not.

## Compression posture

The repair is intentionally lockfile-first. It does not download or bundle third-party bodies. It adds compact source IDs, short notes, tags, and review windows, then relies on citation and pinning policy to make drift visible. This keeps the archive from growing by copied source material while still making the evidence trail auditable.

The backfilled anchor family includes official and technical sources already used by the archive, such as EAC voter-facing and election-management materials (xref: `eac_voter_faqs_2024_pdf`; xref: `eac_election_management_guidelines_2023_pdf`; xref: `eac_voting_location_resource_calculator_page`), FVAP UOCAVA materials (xref: `fvap_mailing_ballots_election_updates_page`; xref: `fvap_fwab_backup_ballot_page`), DOJ civil-rights voting resources (xref: `justice_voting_resources_page`; xref: `justice_voter_intimidation_guide_2024_pdf`), NASS official-routing pages (xref: `nass_find_your_polling_place_page`; xref: `nass_voter_registration_status_page`), state election-office examples (xref: `virginia_candidates_and_referendums_page`; xref: `georgia_call_for_special_election_us_house_district_14_page`), and web-platform APIs used in public-surface handling (xref: `mdn_web_share_api_page`; xref: `mdn_clipboard_api_page`).

## Future maintainer test

When a source-audit report and the release gate disagree, treat the disagreement as a gate bug, not as a documentation nuisance. The blocking checker must be at least as strict as the report for unknown IDs and for unpinned `source:` usage.

Do not add a new numbered doc for each missing source family. Add one lock entry, collapse aliases, and use `xref:` until the bytes are pinned.

## Internal anchors

- `docs/151-authoritative-sources-and-lockfile.md`
- `docs/214-external-sources-index.md`
- `docs/228-external-source-pin-exemptions.md`
- `docs/230-external-sources-by-primary-tag.md`
- `docs/652-authenticity-cue-family-compression-and-promotion-budget.md`
- `evidence/lock/external-sources.toml`
