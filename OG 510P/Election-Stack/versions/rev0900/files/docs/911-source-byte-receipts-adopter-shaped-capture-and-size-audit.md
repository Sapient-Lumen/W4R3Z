# 911. Source-byte receipts, adopter-shaped capture, and size-budget audit

**Track:** Shared / Release evidence / Source authority / Adopter capture

## What changed

rev0873 adds a concrete source-byte receipt lane instead of another doctrine layer. The archive still does not ship third-party PDFs or text bodies, but `artifacts/source_byte_receipts/` now records successful byte observations for selected pinned rows and `tools/source_byte_receipt_pack.py` validates those receipts against `evidence/lock/external-sources.toml`.

The first receipt pack covers 13 pinned, high-leverage source rows:

- EAC/VVSG and election-administration rows: `source: eac_vvsg2_test_assertions_v1_4_pdf`, `source: eac_e2e_protocols_draft_tgdc_2023_pdf`, `source: eac_incident_response_comms_guide_pdf`, `source: eac_enhancing_election_security_public_comms_2024_pdf`, `source: eac_enr_securing_results_checklist_pdf`, `source: eac_post_election_tabulation_audit_guide_2024_pdf`.
- NIST/RFC technical rows: `source: nist_fips_186_5_pdf`, `source: nist_sp800_204d_pdf`, `source: nist_sp800_61r3_pdf`, `source: rfc8785_txt`, `source: rfc8032_txt`, `source: rfc9421_txt`.
- Independent context row: `source: nasem_securing_the_vote_highlights_pdf`.

The validation report is `artifacts/reports/source-byte-receipt-validation-report.json`. It records 13 valid receipts, zero invalid receipts, and 10,421,893 observed bytes, while explicitly saying the archive has not achieved source-byte cache completeness.

## Why this is safer than bundling bytes immediately

The prior gap was not only that source bytes were absent; it was that the archive had no first-class place to record byte observations. Bundling every PDF would create size, licensing, and stale-byte pressure. A receipt lane gives maintainers a narrow, auditable bridge:

1. the lockfile remains the canonical URL/hash authority;
2. the receipt records one successful observation of the bytes outside the release tree;
3. the receipt validation gate proves observed sha256 equals the lockfile sha256;
4. the archive remains small and does not imply that every source has been cached.

`local_filename` hints were added to the same 13 lockfile rows so an operator can later place bytes in an external download directory and run local cache verification without guessing unstable URL basenames.

## Adopter-capture work

The capture-record validator was tightened so a synthetic fixture cannot be shape-valid while requesting public-answer promotion. A shape-valid synthetic record may demonstrate required evidence fields, but promotion remains blocked unless a future adopter replaces the synthetic placeholders with live, responsible-office-owned capture evidence.

The new fixture `artifacts/examples/adopter_authority_capture_records/valid-example-county-in-custody-route-no-promotion.synthetic.json` is intentionally more adopter-shaped than the previous minimal positive fixture. It names a responsible office, public help route, jurisdiction scope, conflict review, human approver role, approval time, source/text digest, and explicit completion gap, while keeping `promotion_requested=false` and `promotion_allowed=false`.

The updated `artifacts/reports/adopter-capture-record-validation-report.json` now has seven fixtures, two shape-valid non-promoting fixtures, five expected-failure fixtures, zero expectation failures, zero shape-valid promotion requests, and zero shape-valid promotions.

## Size-budget audit/refactor

Adding receipts and a new gate left almost no size-budget margin. rev0873 compacted obsolete historical generated CSV row bodies and retained their original SHA-256 digests in `artifacts/reports/rev0873-historical-report-size-compaction.json`. This saved 161,144 tracked bytes without deleting current no-go evidence or weakening current source/adopter gates.

The compacted rows were old generated CSV snapshots from current-authority/source-refresh/platform-source-tail history. Current v873 reports remain full where the release gate compares them to generators.

## Remaining no-go boundary

This revision still does **not** establish current voter instruction, legal advice, source-byte cache completeness, public-release authorization, certification, production signer authority, independent validation, or live-pilot readiness.

The next high-value move is to turn this receipt lane into an operator-facing cache workflow: fetch selected bytes into an external cache directory, verify them with `scripts/verify_external_sources_lock.py`, and record a bounded receipt only after the lockfile hash matches.
