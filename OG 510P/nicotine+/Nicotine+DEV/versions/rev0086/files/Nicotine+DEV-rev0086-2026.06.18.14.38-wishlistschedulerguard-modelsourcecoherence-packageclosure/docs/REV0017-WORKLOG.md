# rev0017 worklog

## Focus

Primary target from rev0016 queue:

```text
PENDING-CONN-BUDGET-01 / U-181
```

## Work completed

- Built `maintainer_artifacts/pending-conn-budget-01/test_pending_peer_connection_budget_reproducer.py`.
- Ran the test against `github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master`.
- Added `tools/probe_rev0017_pending_conn_budget.py` for machine-readable per-lane probing.
- Captured source snippets for pending init, message append, address response, and socket-cap deferred connection paths.
- Performed targeted public-overlap searches for exact internal strings and broader connection symptoms.
- Refactored U-181 away from PB-01 and ADDR-CONNECT-01.

## Test result

```text
github-tag-3.3.10: 4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

## Decision

No strict promotion. U-181 is a verified audited-backlog hardening item.

## Next queue change

Move next narrow target to transfer-size/opened-file provenance, led by U-69/U-107/U-198. Keep U-146/U-159 queued but lower because they are more likely to be request-throttle hardening than strict candidates.
