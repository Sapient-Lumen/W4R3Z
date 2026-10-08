# Rev0941 focused audit

## Mission guard

The work advances Resilio-replacement behavior: larger files can make bounded,
restart-safe progress through the existing C++ peer service over the same direct,
Tor, or I2P stream boundary. Evidence and crash machinery remain subordinate
implementation qualities.

## Severe defect: operation admitted before payload completion

The draft range receiver staged a partial prefix and then admitted the complete
remote operation. A crash could therefore leave shared history claiming a file
whose complete bytes had never become durable. Rev0941 returns typed payload
progress before operation admission; admission occurs only after exact assembly,
whole-file SHA-256 verification, and payload publication.

## Severe defect: completed-page cursor discarded

When a response page contained completed operations followed by a partial large
file, the receiver returned the request's old cursor. Continuation could replay
or request the wrong operation. The result now carries the response's completed-
prefix cursor. A deterministic tombstone-plus-large-file test exercises three
range rounds and exact final convergence.

## Waste removed: repeated source-store scans

The first implementation reconstructed and verified the complete payload-store
snapshot for every range. The authenticated serve session now pins one verified
snapshot to its folder, actors, channel binding, and source evidence digest. Each
ordinary range reads only the requested bytes and re-proves the selected inode.
Mutation or observation drift falls back to complete verification rather than
silently serving mixed versions.

## Test-proof correction

ASan scheduling exposed a false test assumption that handshake expiry must report
at least one `SSL_accept()` attempt. Absolute expiry may occur after accepted-
socket policy proof but before that call. The test now checks the actual authority
boundary: typed expiry, no completed handshake, no peer identity, and no durable
receive. Attempt counts remain diagnostic.

## Remaining risk

The implementation is a correctness slice, not production large-file support.
It lacks block/delta reuse, sparse partial-file ownership, cache reachability and
GC, high-scale small-file performance, and compatibility negotiation.
