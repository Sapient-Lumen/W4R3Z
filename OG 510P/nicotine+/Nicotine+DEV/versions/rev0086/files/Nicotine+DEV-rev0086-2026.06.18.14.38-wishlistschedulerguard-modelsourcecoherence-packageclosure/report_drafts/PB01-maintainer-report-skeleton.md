# PB-01 maintainer report skeleton — rev0011 draft / not external-ready

## Summary

Nicotine+ peer connection primary election can be replaced or promoted without an explicit source/generation binding. A direct `PeerInit` claiming an existing username and connection type can replace an established P/D primary connection and migrate queued messages. A secondary P/D/F connection that shares the same `PeerInit` object can become primary after post-init data is processed. A valid `PierceFireWall` route demonstrates a realistic compatibility path where an indirect secondary is intentionally kept open behind an established direct primary, but is later promoted by the generic secondary-promotion rule.

## Impact boundary

Session-integrity and availability hardening. This is not code execution and not standalone file disclosure. The direct-replacement path needs a reachable incoming connection that can claim a username/type. The secondary-promotion path needs a secondary connection associated with the same init object.

## Evidence packet

```text
maintainer_artifacts/pb01/test_peer_connection_primary_election_reproducer.py
evidence/rev0011-pb01-maintainer-reproducer-run.txt
evidence/rev0011-pb01-source-trace.md
data/rev0011_pb01_compatibility_matrix.csv
```

## Affected lanes checked

```text
github-tag-3.3.10: caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
github-branch-3.3.x: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
github-branch-master: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
```

## Current-behavior reproducer result

```text
github-tag-3.3.10: 10 passed
github-branch-3.3.x: 10 passed
github-branch-master: 10 passed
```

## Compatibility constraints

A safe fix should not reject ordinary first direct P/D `PeerInit` messages, should not break indirect fallback when no direct primary exists, and should still allow a valid indirect connection to win over an unestablished direct attempt. The problematic transition is later replacement/promotion without an explicit generation/election condition.

## Fix-shape sketch

Introduce one connection generation/election model rather than independent patches for U-168 and U-176. Direct replacement should require a pending outbound request/address/generation match or another explicit failover/election condition. Secondary-to-primary promotion should require an elected failover/generation state, not merely any post-init message. F connections should also be tied to transfer-token/session generation.

## Public-overlap status

No direct public report was found for the combined primary-election overwrite/promotion invariant in the rev0011 hard-search refresh. Public/upstream-adjacent material exists around PeerInit/PierceFireWall connection ordering, symptoms in connection-init logs, historical token/extension discussion, and broad 3.3.11 RC spoofed-user/distributed-search hardening. Treat novelty as candidate-no-direct-public-match-found, public/upstream-adjacent.

## Remaining before external use

Final private/maintainer overlap check if available; convert this current-behavior witness into a fixed-behavior regression once a patch shape exists; keep impact wording bounded.
