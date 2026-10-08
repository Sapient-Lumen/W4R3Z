# PB-01 maintainer packet — rev0011

## Status

PB-01 remains a strict/front-lane report-candidate, not a production-ready disclosure text.

## What changed since rev0010

rev0010 proved the state-machine behavior with a probe. rev0011 converts that into a smaller maintainer-grade pytest witness and adds compatibility baselines. This matters because the obvious but wrong fix would be to reject too much connection fallback behavior and break normal Soulseek direct/indirect races.

## Test layout

```text
maintainer_artifacts/pb01/test_peer_connection_primary_election_reproducer.py
```

The test has 10 cases per source lane:

```text
4 compatibility baselines:
- first direct P/D PeerInit accepted as primary;
- valid PierceFireWall with no direct primary becomes primary;
- valid PierceFireWall can replace an unestablished direct attempt.

6 current-behavior reproducer cases:
- later direct PeerInit replaces existing P/D primary and migrates queued messages;
- secondary P/D/F connection promotes itself to primary after post-init activity;
- valid PierceFireWall secondary remains behind established primary, then promotes after a P message.
```

## Run result

```text
github-tag-3.3.10: 10 passed
github-branch-3.3.x: 10 passed
github-branch-master: 10 passed
```

These are current-behavior assertions. Passing means the packet reproduces the current behavior, not that the behavior is fixed.

## Why this is one report, not two or four

U-168 and U-176 are two faces of the same missing generation/election model. U-165 only supplies a valid PierceFireWall route into the secondary-connection state; it is not strong enough as a standalone bearer-token finding yet. U-171, U-181, and U-185 touch connection state but have different sinks and fix vocabulary.

## Safe-fix constraints

A coherent fix should preserve legitimate first connection and fallback behavior while blocking later replacement or promotion unless the connection has an explicit generation/election right to become primary.
