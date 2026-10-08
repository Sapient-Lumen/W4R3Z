# 860 — Current-authority near-term review-cliff burndown

**Track:** Shared / Source freshness / Maintainer operations
**Status:** v855/v856 release-gate coherence repair

Status: active in v849.

## Why this changed

The source-pressure reports were correct but still allowed a wasteful maintenance failure: hundreds of platform/UI/vendor rows could distract from a much smaller set of current-authority rows whose review windows were about to expire. v849 fixes the immediate current-authority cliff first.

## What changed

Forty-eight unpinned current-authority rows due on 2026-06-06 or 2026-06-07 were re-reviewed. They were not converted into byte pins in this cloudtainer. Instead, the rows remain explicitly unpinned, carry row-level `review_note` boundary text, and have bounded future `review_by` windows.

Primary outputs:

- `artifacts/reports/current-authority-near-term-review-rev0849.md`
- `artifacts/reports/current-authority-near-term-review-rev0849.csv`
- `artifacts/reports/current-authority-near-term-review-rev0849.json`
- `scripts/check_current_authority_review_cliff.py`

## New executable guard

`scripts/check_current_authority_review_cliff.py` fails if unpinned current-authority rows are due inside the near-term release horizon. It is narrower than the full external-source lockfile check so maintainers do not waste a session linearly reviewing the platform/UI/vendor tail before official current-authority rows.

Recommended release invocation:

```bash
ELECTION_STACK_SOURCE_REVIEW_DATE=2026-06-04 \
  python3 scripts/check_current_authority_review_cliff.py --horizon-days 7
```

## Remaining queue

v849 does not erase the broader source-maintenance problem. After the immediate cliff burndown, the current reports still show due-soon current-authority rows and a much larger platform/UI/vendor tail. The right next source pass is current-authority rows first, bounded platform sampling second.

## Boundary

This is maintainer source-currentness triage only. It is not a current voter-instruction source, legal advice, certification evidence, independent validation, production signer authority, or live-pilot authorization.
