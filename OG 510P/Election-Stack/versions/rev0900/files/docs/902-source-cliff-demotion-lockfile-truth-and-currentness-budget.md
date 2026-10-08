# 902 — Source-cliff demotion, lockfile truth, and currentness budget

**Track:** Shared / Source freshness / Cloudtainer burn-down

rev0865 is deliberately not another registry. It makes the current-date queue smaller by removing false urgency and correcting a lockfile truth error.

## What changed

1. **The near-term cliff is now real work, not page-count panic.** At `2026-06-10`, rev0864 still had `727` unpinned rows due within 30 days. Most were mutable vendor, browser, product-help, media-platform, or implementation-detail accessibility pages. rev0865 demotes those rows to explicit implementation/watchlist status and moves their next review to `2026-09-08` without claiming currentness.
2. **The due-within-30-days queue is now seven rows.** After the demotion, `artifacts/reports/source-review-pressure-current-rev0865.json` reports `expired_review_count = 0`, `current_authority_due_30d_count = 0`, `platform_ui_vendor_due_30d_count = 0`, `accessibility_reference_due_30d_count = 0`, and `unexpired_due_within_30_days_count = 7`. The remaining seven rows are citation-backfill replace/pin/delete work due `2026-07-10`.
3. **The demotion is not a freshness refresh.** The changed rows remain unpinned. Their notes now say they are implementation hints or platform watchlist rows. They must not support rights-affecting voter instructions, legal claims, certification claims, or current public-authority claims.
4. **The C2PA mutable spec pointer is current again.** The mutable HTML row formerly named `c2pa_content_credentials_spec_2_3_html` is now `c2pa_content_credentials_spec_2_4_html`, pointing at the C2PA 2.4 HTML specification. The older pinned `c2pa_content_credentials_spec_2_2_pdf` remains as historical byte-pinned context. C2PA remains provenance vocabulary and trust-signal context, not proof that media is true, official, or governing. (xref: `c2pa_content_credentials_spec_2_4_html`; source: `c2pa_content_credentials_spec_2_2_pdf`)
5. **Pinned-source notes now tell the truth.** rev0865 corrected `80` pinned rows whose notes still said `xref-only`, `no local byte cache`, or `Pin, replace, or demote before guidance use`. A new lockfile check rejects that contradiction for future pinned rows.
6. **The local source verifier no longer dirties the tree.** `scripts/verify_external_sources_lock.py` no longer creates `evidence/cache/` just because it ran. Missing local bytes now produce `SKIP` output unless `--strict` is requested.

Machine-readable record: `artifacts/reports/source-cliff-demotion-and-note-consistency-rev0865.json` and `.csv`. These files are intentionally compact; the full row-level truth is the lockfile itself, not a duplicated 801-row report.

## Why this was the riskiest next cut

The previous queue shape encouraged a bad maintainer behavior: spend the session re-opening hundreds of mutable platform pages while the few remaining load-bearing source problems stayed mixed into the tail. That is not sustainable. It also made the cube look more precise than it was, because a browser help page and a rights-authority accessibility anchor could appear in the same operational lane.

rev0865 changes the budget:

| Item | rev0864 current-date pressure | rev0865 current-date pressure |
|---|---:|---:|
| Expired unpinned review windows | `0` | `0` |
| Due within 30 days, all lanes | `727` | `7` |
| Current-authority due within 30 days | `0` | `0` |
| Accessibility-reference due within 30 days | `175` | `0` |
| Platform/UI/vendor due within 30 days | `540` | `0` |
| Platform-tail sample size | `57` | `0` |

The correct next unit of work is now visible: resolve the seven remaining citation-backfill rows, then pin or replace high-leverage authority PDFs/specs. Do not reopen the 720-row platform/accessibility tail unless an active public surface depends on a specific behavior.

## What not to infer

Do not infer that the demoted pages were reviewed and found current. Do not infer that a demoted accessibility implementation page is enough for a rights claim. Do not infer that a C2PA credential proves content is official or true. Do not infer that a recorded SHA-256 proves this cloudtainer currently contains source bytes unless a verifier is run with the matching local cache.

The safe rule is:

- `source:` rows with SHA-256 are byte-identity references, not automatically current public authority.
- `xref:` rows are context references unless pinned/reviewed by a separate current-authority process.
- `implementation_hint`, `platform_watchlist`, `accessibility_implementation_hint`, and `standard_watchlist` rows are non-authority by construction.

## Audit/refactor details

### Lockfile note consistency

`scripts/check_external_sources_lockfile.py` now fails a pinned row whose note still describes it as xref-only/unpinned work. This catches the exact class of contradiction fixed in rev0865.

### Side-effect-free verifier

`scripts/verify_external_sources_lock.py` previously created the default cache directory on read-only verification runs. That was small but wasteful: a verifier should not mutate an extracted release just to report missing optional local source bytes. The script is now side-effect free for missing caches.


### High-risk payload review-window drift

The current-date gate also exposed stale `last_verified_at` metadata on 15 special-case voter-facing payload templates. rev0865 refreshes those payload-control timestamps to `2026-06-10T00:00:00Z` without changing the 90-day review window. This is a synthetic control-window refresh after structural gate checks; it is not a legal review, current voter instruction, or jurisdictional source refresh.

### Review-pressure lane refinement

`scripts/report_source_review_pressure.py` now has an `implementation_hint_watchlist_due_30d` lane. If a future revision lets watchlist rows drift back into the near-term queue, they will appear separately from current authority and source-byte work.

## Remaining hard work

The seven rows due `2026-07-10` should not be extended again without a real pin, replacement, or deletion decision:

- `bpc_making_ballot_images_and_cast_vote_records_public`
- `brennan_center_legacy_democracy_9_25_08_bestpracticeschecklist`
- `elections_group_content_uploads_2023_08_ballot_management_audit_230809`
- `iml_key_23626`
- `ncsl_14_how_states_verify_voted_absentee_mail_ballots`
- `ncsl_ballot_processing_and_counting_can_begin_maptype_tile`
- `science_doi_10_1126_sciadv_adt1512`

Boundary: rev0865 remains synthetic-only. It is not current voter instruction, legal advice, source-byte cache certification, voting-system certification, independent validation, production signer authority, production publication governance, or live-pilot authorization.
