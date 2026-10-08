# rev0867 federal official-source sweep and current-authority classifier refactor

**Track:** Shared / source maintenance / release-risk burn-down  
Status: synthetic release-maintenance artifact  
Release date: 2026-06-10

## What changed

rev0867 addresses two concrete risks found after rev0866:

1. **The 45-day current-authority reports disagreed.** `report_current_authority_source_queue.py` and `report_current_authority_burndown_batches.py` carried near-duplicate host, state, and tag logic. That hid several state/local rows from one report and counted `get.gov`/NIST-adjacent routes differently.
2. **The next large queue was not the 30-day cliff; it was the 45-day authority cliff.** After the seven-row 30-day queue was cleared, the next high-risk work was a mixed 45-day queue containing federal pages, official public routing pages, accessibility/rights pages, and many state/local jurisdiction pages.

The fix is deliberately operational, not doctrinal:

- centralize current-authority classification in `scripts/_shared/current_authority.py`;
- add `scripts/check_current_authority_report_consistency.py` so the queue and batch reports must agree;
- re-review the non-state federal/official/current-routing portion of the 45-day queue as bounded `xref` context;
- leave state/local jurisdiction rows visible rather than pretending they are safe to carry forward as current voter instructions.

## Queue movement

Before the rev0867 sweep, the shared classifier exposed `145` unpinned current-authority rows due within 45 days on the 2026-06-10 release-review date. The earlier split reports had shown lower counts because their classification lists had drifted.

The sweep updated `75` non-state rows:

| Lane | Rows updated | New review_by | Boundary |
|---|---:|---|---|
| Federal election authority | 37 | 2026-08-09 | EAC route/context only; not voter instruction or certification evidence |
| Federal cyber authority | 12 | 2026-08-09 | CISA/get.gov route/context only; not a source-byte cache or security attestation |
| Official public communications/routing | 11 | 2026-08-09 | Vote.gov/NASS routing context only; not jurisdiction-specific instructions |
| Accessibility or rights authority | 13 | 2026-08-09 | Official accessibility/rights route context only; not legal advice or compliance determination |
| Federal standards or AI authority | 1 | 2026-08-09 | Standards-route context only; pin versioned artifacts before normative use |
| Other current authority | 1 | 2026-08-09 | Official-route context only |

Machine-readable record:

- `artifacts/reports/federal-official-route-sweep-rev0867.json`
- `artifacts/reports/federal-official-route-sweep-rev0867.csv`

No byte pins were added.

## Why state/local rows were left in the queue

The remaining 45-day queue is now `70` state/local jurisdiction rows. Those rows are intentionally not swept into a blanket extension, because they are the highest-risk rows for misuse as current voter instructions. They include jurisdiction-specific eligibility, registration, provisional ballot, disability-access, displaced-voter, vote-center, confidential-registration, and ballot-return surfaces.

These rows must be handled only when a real jurisdiction/adopter path exists, and then with jurisdiction-specific review, source-byte capture where possible, and counsel/operator signoff before public use.

## Audit/refactor details

New shared helper:

- `scripts/_shared/current_authority.py`

Updated reports now use the same classifier:

- `scripts/report_current_authority_source_queue.py`
- `scripts/report_current_authority_burndown_batches.py`
- `scripts/report_source_review_pressure.py`

New drift firewall:

- `scripts/check_current_authority_report_consistency.py`

The consistency check compares the 45-day current-authority due count and lane counts produced by the queue report and the batch report. It fails if one report hides work the other report sees.

## Current status after rev0867

For the 2026-06-10 release-review date:

| Measure | Status |
|---|---:|
| Expired unpinned source-review rows | 0 |
| Due within 30 days | 0 |
| Current-authority due within 45 days | 70 |
| Current-authority 45-day lanes | state/local only |
| Byte pins added | 0 |

Generated reports:

- `artifacts/reports/source-review-pressure-current-rev0867.json`
- `artifacts/reports/current-authority-source-queue-45day-rev0867.json`
- `artifacts/reports/current-authority-burndown-batches-45day-rev0867.json`

## Next riskiest work

The next substantive pass should focus on the state/local queue, not more platform doctrine:

1. choose a real or synthetic jurisdiction scope before reviewing state/local rows;
2. pin durable PDFs first;
3. for mutable HTML pages, keep them as routing/context unless a live authority review captures the exact text and timestamp;
4. add a local adoption gate that fails if a jurisdiction row is cited as public guidance without a current/pinned source and human approval.

Boundary: rev0867 is still synthetic-only release maintenance. It is not current voter instruction, legal advice, certification evidence, production signer authority, independent validation, source-byte cache completeness, or live-pilot authorization.
