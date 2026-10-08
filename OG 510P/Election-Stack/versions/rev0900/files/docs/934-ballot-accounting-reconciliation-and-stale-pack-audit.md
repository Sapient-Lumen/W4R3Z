# v897 ballot-accounting reconciliation and stale-pack audit

**Track:** Shared

## Why this was the next risk

v895/v896 made the standardized-results lane materially better: the archive can replay a minimal BD/CVR/ERR fixture, emit a CRO, and use a separate verifier to check the primary replay report and CRO.  The remaining mission risk was that matching option totals could still be disconnected from reporting-unit completeness.  A real closeout cannot stop at “the CVR totals equal the published result totals.”  It also needs ballot accounting, custody anchors, exceptions, and disposition records.

## What v897 adds

`tools/ballot_accounting_reconciler.py` adds a bounded executable bridge across K02 and K03.  It reads:

- `artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-definition-minimal.json`
- `artifacts/examples/example_county_2026_municipal_pilot/cdf/cast-vote-records-minimal.json`
- `artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-accounting-minimal.json`

It recomputes reporting-unit and contest accounting facts from the CVR fixture and compares them to the synthetic ballot-accounting ledger:

- CVR record count by reporting unit;
- eligible ballot count by contest;
- selection limit;
- expected selection slots;
- observed CVR selection count;
- undervote slots; and
- overvote-record count.

The release gate now includes `scripts/check_ballot_accounting_reconciler.py`, which requires the shipped report to be fresh and requires three negative controls to fail closed:

- CVR/accounting count drift;
- undervote-slot drift; and
- unknown reporting-unit accounting rows.

Current transcript: `artifacts/reports/ballot-accounting-reconciliation-rev0897.json`.

## Audit/refactor finding

The v896 ZIP exposed a stale-pack defect that was not just cosmetic.  The root version was v896, but several non-revision-named no-go packs still carried v895 `archive_version` values, including the local-pilot, redaction/publication, accessibility/language, custody/provenance, independent-review, adopter-capture, and adopter-record-validation packs.

v897 regenerates these packs and expands `scripts/check_current_revision_fixture_sweep.py` so future revisions check both rev-named executable reports and non-rev-named no-go packs.  That closes the gap that allowed root navigation, release decision artifacts, and subordinate no-go matrices to disagree.

## Boundary

This is synthetic replay and reconciliation only.  It is not live ballot-accounting evidence, not live custody evidence, not a full NIST CDF conformance result, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.  Real promotion still requires authorized local ballot-accounting exports, custody transfer/seal records, exception records, disposition records, redaction/publication approval, and external reviewer transcripts.
