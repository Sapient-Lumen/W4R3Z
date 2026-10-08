# rev0075 revision summary

## Problem resolved

Rev0075 re-audits SEARCH-RESP-01A against the exact supported `3.3.x` source. The old packet correctly observed that a token-valid response can arrive under a username outside a direct user search's expected set. It then treated a green expected-set guard as a production-ready security fix.

The missing boundary is identity. Exact parsing shows `msg.username` comes from the username claimed in wire `PeerInit`. A peer claiming an expected name passes the guard. The protocol's old server-mediated username/token verification is obsolete, and upstream itself treats Soulseek usernames as spoofable in other permission decisions.

## Disposition

```text
confirmed: local request-scope consistency gap
confirmed: rev0039 guard filters claimed off-set names
not established: authenticated source, practical token capability, end-to-end injection, material impact
selected patch: none
security route: not supported by current evidence
status: open defense-in-depth research
```

## Validation

```text
exact source ref: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
source invariants: 8/8
classified matrix rows: 8/8
compile checks: 6/6
isolated upstream units: 58 passed, 1 skipped in baseline and patched states
```

## Cube refactor

The old two-file active test pair (322 lines / 9,898 bytes) is preserved in an archive. A shared harness and four role-specific tests now occupy 198 lines / 6,459 bytes. Identity, policy, current behavior, and token modeling no longer share one implicit verdict.

A deterministic status audit inventories historical SEARCH-RESP artifacts, checks archive hashes, and prevents current landing pages from inheriting obsolete production-ready language. It identifies 80 exact duplicate groups and 200,990 redundant bytes across 516 related files, providing a ranked basis for future manifest-based compaction.

## Boundary

No patch is recommended for upstream use. All material is research-only and must be independently recreated and reasoned about by a human under the project's contribution rules.
