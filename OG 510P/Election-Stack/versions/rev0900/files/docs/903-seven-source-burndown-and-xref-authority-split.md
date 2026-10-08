# 903 — Seven-source burn-down and xref authority split

**Track:** Shared / Source freshness / Maintainer-risk burn-down

rev0866 resolves the visible seven-row near-term source-review cliff without pretending this cloudtainer has local third-party bytes.

## What changed

1. **The due-within-30-days queue is now zero.** `artifacts/reports/source-review-pressure-current-rev0866.json` reports no expired rows and no due-within-30-days rows for the `2026-06-10` current-date pass.
2. **No byte pins were invented.** The seven rows remain unpinned because this cloudtainer could not fetch external bytes. The decision report records `byte_pins_added = 0`.
3. **The rows are no longer mixed into an urgent blocker lane.** Each row now carries a specific bounded decision: parser-confirmed mutable context, blocked archival/publisher route, or implementation context pending a real byte pin.
4. **The BPC route is replaced with the parser-confirmed explainer page.** The previous PDF-style route is no longer the maintained reference for the CVR/ballot-image tradeoff context. (xref: bpc_making_ballot_images_and_cast_vote_records_public)
5. **The NCSL rows are explicitly mutable summaries, not state-law authority.** They remain useful jurisdiction-variation reminders, but public guidance must verify current state/local law and official election-office instructions. (xref: ncsl_14_how_states_verify_voted_absentee_mail_ballots; xref: ncsl_ballot_processing_and_counting_can_begin_maptype_tile)
6. **The Science DOI row is blocked, not silently stale.** The publisher DOI route remains the named reference, but the parser block is recorded and the row is xref context only until locally hashed or replaced by a durable open route. (xref: science_doi_10_1126_sciadv_adt1512)

Machine-readable record: `artifacts/reports/source-seven-row-decision-burndown-rev0866.json` and `.csv`.

## Decisions by row

| Reference | rev0866 decision | Next review |
|---|---|---:|
| xref: bpc_making_ballot_images_and_cast_vote_records_public | Replaced inaccessible PDF-style route with parser-confirmed maintained explainer page; xref policy context only. | `2026-12-07` |
| xref: brennan_center_legacy_democracy_9_25_08_bestpracticeschecklist | Keep as historical checklist context; current authority must come from EAC/canvass sources. | `2027-06-10` |
| xref: elections_group_content_uploads_2023_08_ballot_management_audit_230809 | Keep as implementation context pending a real byte pin. | `2026-09-08` |
| xref: iml_key_23626 | Keep as rumor-control implementation example, not current authority. | `2026-12-07` |
| xref: ncsl_14_how_states_verify_voted_absentee_mail_ballots | Keep as mutable jurisdiction-variation summary, not state-law authority. | `2026-09-08` |
| xref: ncsl_ballot_processing_and_counting_can_begin_maptype_tile | Keep as mutable jurisdiction-variation summary, not state-law authority. | `2026-09-08` |
| xref: science_doi_10_1126_sciadv_adt1512 | Keep publisher DOI row as parser-blocked article context until locally hashed or replaced. | `2027-06-10` |

## Refactor/audit result

The practical refactor is a source-authority split, not a new registry:

- `source:` remains reserved for pinned byte-identity references in docs.
- `xref:` can carry context, but every unpinned context row must have a bounded `pin_exemption` and `review_by`.
- Mutable state-policy summaries must not be used as live voter instruction or legal authority.
- Blocked publisher/archival routes must say they are blocked or historical rather than sitting in an urgent queue with a misleading generic note.

This reduces future operator waste: maintainers can now work on high-leverage pinning or actual public-surface controls instead of reopening the same seven xref-only rows every turn.

## What remains hard

The cube still has many unpinned source rows. rev0866 improves the current-date queue, but it does not solve source-byte availability. The durable next improvement is to add an explicit source-byte acquisition lane for the highest-leverage PDFs/specs, then use local-file pinning rather than extending review windows.

Boundary: rev0866 remains synthetic-only. It is not current voter instruction, legal advice, source-byte cache certification, voting-system certification, production signer authority, independent validation, publication governance, or live-pilot authorization.
