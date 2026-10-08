# rev0866 next-authority EAC page audit

**Track:** Shared / source maintenance / release-risk burn-down

This note records a small next-risk pass after the seven-row due-within-30-days queue was cleared.

## What changed

Three high-reference EAC mutable pages were parser-rechecked on 2026-06-10 and moved out of the immediate 45-day authority queue with a short 2026-08-09 review window:

| Lockfile ID | Decision | Boundary |
|---|---|---|
| `eac_effective_design_for_the_administration_of_federal_elections_page` | Parser-confirmed as the current EAC Effective Design page dated 2026-04-14. | Official design/communications context only; not jurisdiction-specific voter instruction or legal authority. |
| `eac_clearinghouse_resources_accessibility_page` | Parser-confirmed as the current EAC accessibility clearinghouse page dated 2026-05-06. | Official accessibility resource index only; not jurisdiction-specific voter instruction or legal authority. |
| `eac_clearinghouse_resources_communications_page` | Parser-confirmed as the current EAC communications clearinghouse page dated 2026-04-14. | Official communications resource index only; not jurisdiction-specific voter instruction or legal authority. |

No byte pins were added. These are mutable official pages, so the cube now gives them a bounded short review window instead of treating them as byte-stable evidence.

## Why this is substantive

The previous pass cleared the 30-day cliff. This pass starts on the next cliff: current-authority rows due within 45 days. The count dropped from 140 to 137. That is small, but the three rows are high-reference pages and reduce a likely future bottleneck without adding another registry or doctrine layer.

## Machine reports

- `artifacts/reports/next-authority-eac-page-audit-rev0866.json`
- `artifacts/reports/next-authority-eac-page-audit-rev0866.csv`
- `artifacts/reports/current-authority-source-queue-45day-rev0866.json`
- `artifacts/reports/current-authority-source-queue-45day-rev0866.csv`

## Follow-on work

The next real queue is not platform/UI sprawl. It is the remaining 137 current-authority rows inside a 45-day horizon, especially state/local official pages and remaining EAC/CISA federal authority pages. Those should be refreshed, pinned where durable bytes exist, or demoted before any platform/watchlist cleanup gets more time.
## Verifier/check refactor

The release go/no-go checker no longer assumes the 30-day source-review queue must be nonzero. That assumption became stale once rev0866 actually cleared the near-term queue. The check now verifies that the due-within-30-days field exists and is nonnegative, allowing a true zero while still preserving the source burn-down lanes.

