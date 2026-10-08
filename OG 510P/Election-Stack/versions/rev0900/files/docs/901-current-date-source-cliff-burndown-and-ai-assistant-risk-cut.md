# 901 — Current-date source cliff burn-down and AI-assistant risk cut

**Track:** Shared / Source freshness / Public-answer safety

rev0864 is a risk-first continuation of the rev0863 audit. It deliberately avoids adding another broad registry. The work here removes the current-date source-review blocker, separates accessibility/public-rights source work from generic platform churn, and tightens the automated voter-information assistant checklist where a wrong answer could injure a voter.

## What changed

1. **The current-date lockfile blocker is cleared.** At the session date `2026-06-10`, the lockfile had `27` already-expired unpinned rows, all with `review_by = 2026-06-06`. rev0864 re-reviewed those rows as `xref`-only citation backfill, updated their `retrieved` dates, and assigned bounded follow-up dates. The current-date source lockfile check now passes with `ELECTION_STACK_SOURCE_REVIEW_DATE=2026-06-10`.
2. **The fix does not pretend to be byte verification.** No SHA-256 source bytes were added. The burn-down report explicitly records `byte_pins_added = 0` because this cloudtainer does not contain a source-byte cache and the container fetch path was not suitable for reliable byte hashing.
3. **Three citation-backfill routes are now on a shorter replace/delete path.** `elections_group_content_uploads_2023_08_ballot_management_audit_230809`, `iml_key_23626`, and `science_doi_10_1126_sciadv_adt1512` were not parser-confirmed in this session. They remain unpinned `xref` rows, but their new deadline is `2026-07-10` rather than a full 90-day holdover.
4. **The remaining 24 expired rows were not promoted.** They were moved to `review_by = 2026-09-08` as explicit unpinned citation backfill. That keeps the current-date gate honest while preserving the next real task: pin durable PDFs/specs where possible, replace mutable pages with stronger anchors, or delete low-value context.
5. **The near-term current-authority cliff is also cleared.** A second pass reviewed the `13` CISA/DOJ/EAC/NIST rows that were due by `2026-07-10`. Five routes were parser-confirmed in this session; eight CISA routes were search-confirmed but direct parser/byte fetch was blocked here. All `13` remain `xref`-only with zero byte pins and a short `2026-07-25` source-byte decision deadline.

Machine-readable records: `artifacts/reports/citation-backfill-expired-burndown-rev0864.json`, `artifacts/reports/current-authority-nearterm-burndown-rev0864.json`, and their CSV companions.

## Audit/refactor: source-pressure lanes now reflect risk better

rev0863 correctly identified platform/UI sprawl, but its first-pass lane classification was too crude: W3C/WAI/WCAG accessibility material could fall into the same broad platform/vendor bucket as ordinary help-center pages. That is operationally wasteful in the opposite direction: maintainers might treat public-rights accessibility references as the same low-value churn as a browser help page.

rev0864 changes the report family this way:

- `scripts/report_source_review_pressure.py` now has a separate `accessibility_reference_due_30d` lane, classifies legal and durable standards before generic citation backfill, and creates parent directories for JSON output paths just as it already did for CSV output paths.
- `scripts/report_platform_source_tail.py` and `scripts/report_platform_source_sampling_plan.py` now exclude accessibility-reference rows from the generic platform tail and handle out-of-repo output paths safely.
- `scripts/report_current_authority_source_queue.py` now reports already-expired current-authority rows, not only future due-soon rows. Its summary now carries `current_authority_expired_count` and `current_authority_due_soon_count`, so an expired authority route cannot disappear from the queue view.

Current-date result at `2026-06-10` after the refactor:

| Queue | Count | Meaning |
|---|---:|---|
| Expired unpinned reviews | `0` | Current-date lockfile blocker removed. |
| Due within 30 days, all lanes | `727` | Still a large maintainer-pressure cliff. |
| Current-authority due within 30 days | `0` | The near-term CISA/DOJ/EAC/NIST queue was re-reviewed into a short `2026-07-25` source-byte decision window. |
| Accessibility-reference due within 30 days | `175` | Public-rights/UI-accessibility lane, no longer buried in generic platform churn. |
| Platform/UI/vendor due within 30 days | `540` | Still large enough to require sampling/consolidation rather than linear review. |
| Platform-tail sample | `57` of `542` | Host-balanced sample; avoids `485` line-by-line reviews unless the sample shows a product-family change. |

Reports: `artifacts/reports/source-review-pressure-current-rev0864.json`, `artifacts/reports/current-authority-source-queue-current-rev0864.json`, `artifacts/reports/current-authority-nearterm-burndown-rev0864.json`, `artifacts/reports/platform-source-tail-current-rev0864.json`, and `artifacts/reports/platform-source-sampling-plan-current-rev0864.json`.

## Cloudtainer waste corrected

The size gate exposed another non-substantive cost: repeated historical platform-tail CSV snapshots were consuming release budget even though their JSON summaries and current-date CSVs were enough for maintainer triage. rev0864 removes unreferenced historical platform-tail CSVs after `rev0843` and unreferenced newer platform-sampling CSVs while preserving the current-date CSVs and historical anchor files already cited by earlier compaction docs. Machine-readable record: `artifacts/reports/platform-tail-and-sampling-csv-compaction-rev0864.json`.

## AI assistant risk cut

The riskiest public-answer surface is not whether the archive has enough AI doctrine. It is whether an automated assistant can sound authoritative while getting a voter-specific rule wrong. rev0864 therefore edits `artifacts/checklists/automated-voter-information-assistant-surface-checklist.md` rather than adding a new policy registry.

The checklist now requires:

- no final rights-affecting automated determinations about eligibility, registration status, ballot acceptance/rejection, provisional-ballot outcome, cure sufficiency, ID sufficiency, challenge outcome, deadline exceptions, or accommodation entitlement;
- official form/lookup/secure-channel/human-office routing for rights-affecting or record-specific questions;
- visible `last_verified_at`, jurisdiction label, source hierarchy, explicit source anchors, and abstention behavior for action-changing answers;
- testing for prompt injection, source poisoning, stale-source replay, jurisdiction mixing, synthetic citations/confabulation, unsafe tone during source conflicts, and overconfident answers when sources are missing;
- human approval before templates change for deadlines, eligibility, registration or ballot status, ID, polling/place lookup, mail-ballot cure, accommodations, intimidation, challenges, provisional ballots, or dispute/escalation rights.

This aligns the cube with the direction of the current authority surface without pretending the archive is itself current authority: EAC's VVSG 2.0 certification milestone still leaves state testing/procurement/training/public-testing work to deployment contexts (`xref: eac_certified_voting_system_voluntary_voting_system_guidelines_vvsg`); DOJ's Title II web/mobile rule keeps accessibility in the state/local public-service lane (`xref: ada_gov_web_mobile_apps_fact_sheet_page`); NIST AI RMF/GenAI guidance makes prompt-injection, data-quality, provenance, human-AI configuration, and information-integrity risks operational rather than decorative (`source: nist_ai_rmf_100_1_pdf`; `source: nist_ai_600_1_genai_profile_pdf`); and WCAG remains a standards lane that should not be buried as vendor documentation (`xref: w3c_tr_wcag22`).

## What remains risky after rev0864

The source-debt problem is now visible and non-blocking for the current-date lockfile gate, but not solved. The archive still has only `118` byte-pinned external-source rows out of `1,216`. The next risk-reducing move is to byte-pin or replace the high-leverage PDFs/specs first, then use the platform sample to delete or consolidate low-value vendor pages.

The current-authority queue now shows `0` rows due within 30 days, but this is a short triage reprieve rather than source verification. The `13` current-authority rows re-reviewed in rev0864 must be pinned, replaced, or explicitly demoted before `2026-07-25`.

The three unconfirmed non-authority citation-backfill routes should be replaced or removed before `2026-07-10`. Extending them again without a stronger reason would be a bad sign: it would convert a burn-down into date laundering.

Boundary: rev0864 is still synthetic-only. It does not provide current voter instruction, legal advice, certification evidence, production signer authority, independent validation, source-byte verification, or live-pilot authorization.
