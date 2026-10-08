# rev0036 worklog

Revision: `Nicotine+DEV-rev0036-2026.06.14.20.28-u123identitydraft-sessionguard-refactoraudit`

## Work performed

1. Continued from rev0035 and selected U-123 as instructed by the rev0035 next-revision queue.
2. Reran the current-behavior U-123 witness across all three archived lanes.
3. Added `test_downloads_duplicate_transfer_token_fixed_regression.py`, a fixed-behavior regression skeleton expected to fail on current source.
4. Ran the fixed regression across all three archived lanes and captured the expected failure at the missing active username+token map entry.
5. Added an identity-guard simulation helper and verified the fixed regression passes under a narrow object-identity deactivation guard across all three lanes.
6. Source-traced activation, deactivation, timeout, F-init, progress, close, and protocol token anchors.
7. Performed public-overlap review and kept the classification conservative.
8. Added a maintainer-ready U-123 report draft and fix skeleton.
9. Performed a coherence/refactor pass to keep U-123 transfer-session identity separate from PB-01, SEARCH-RESP-01, and media-parser rows.
10. Updated START-HERE, README, AUDITED-BACKLOG-RANKED, strict-promotion data, queue delta, and next-revision queue.

## Test/evidence summary

```text
current witness: 3 lanes OK
fixed regression on current source: 3 lanes expected-fail
identity-guard simulation: 3 lanes OK
```

## Packaging notes

No large source tree, `.git`, `source-trees`, `git-full`, `__pycache__`, or `.pytest_cache` directories are intentionally included.
