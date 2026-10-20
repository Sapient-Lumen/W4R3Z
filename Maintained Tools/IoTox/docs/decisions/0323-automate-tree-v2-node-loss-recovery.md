# ADR 0323: Automate tree-v2 node-loss recovery

- Status: accepted and implemented
- Date: 2026-09-03

## Context

ADR 0319 supplied an exact bounded comparison between an operator-selected backup and a restored
ordinary tree, but did not exercise reconstruction of IoTox identities, authority, membership, or
live synchronization state. A replacement writer also exposed two recovery boundaries that the
ordinary three-writer lifecycle did not cross.

First, completed publisher replay records remained in a bounded idempotency cache until eviction or
disconnect. `sync-share` treated any retained record as active work, so unrelated completed traffic
could indefinitely prevent an additive writer admission. Second, `sync-writer-cutoff` correctly
retains the old writer in historical policy and creates a checkpoint that can cite its terminal
branch. A fresh replacement that never trusted that writer must not accept such history. It needs a
new graph floor after every survivor has first accepted the cutoff checkpoints in sequence.

## Decision

Publisher replay entries now retain their namespace ID. Replay-cache retention is separate from
transfer lifetime. While holding the same authority/effect fence used by incoming synchronization
requests, an additive `sync-share` may discard exact-response entries for only the namespace being
widened. This neither cancels an existing transfer nor revokes any existing authority; a repeated
request is authorized afresh against the successor authority and namespace policy. This operation
is intentionally unavailable as a general drain or revocation primitive: destructive membership,
projection, and namespace changes retain their stronger quiescence requirements because an
outbound transfer may still be live.

`tools/run-sync-recovery-rehearsal.py` freezes one bounded same-VM ceremony:

1. create three fresh identities and a six-direction tree-v2 full mesh, converge one ordinary tree,
   and verify all stores;
2. copy one operator-selected ordinary generation into a separate backup view and restore view, then
   require `sync-recovery-verify` to match;
3. on both survivors, cut off the departing writer, revoke its synchronization authority, and remove
   its Tox friendship before erasing its complete node root;
4. restart the survivors, exchange the two cutoff checkpoints without skipping a generation, create
   a second post-cutoff checkpoint on each survivor, and exchange those graph floors;
5. create an empty replacement with fresh device and Tox identities, authorize and share it
   bilaterally, converge all three worktrees, repair all stores, and require only the three live
   principals in every current branch frontier;
6. erase all three live node roots, create three more fresh device/Tox identities and authority
   ledgers from the retained RecallRoot phrases, seed one ordinary worktree from the restored backup
   view, rebuild all six shares, converge, repair, and compare every replacement view with the
   selected backup; and
7. retain only hashes of obsolete and replacement principals in evidence and require the sets to be
   disjoint.

The liveness observer reads only canonical branch filenames and the fixed branch header. It does
not hammer authenticated `sync-history` or `sync-repair` while Tox must progress. The explicit
repair and four restore-verifier calls remain the integrity gates after convergence.

## Consequences

The final direct source-linked rehearsal passes with 33 regular files in one directory, 131,099 bytes,
one empty-node replacement, total live-node loss, six repaired node instances, and four exact
restore comparisons in 81.771 seconds. A retained clean 2-vCPU/2-GiB Sandwurm run composes the
ceremony with the 512-file capacity and 24-cycle persistent lifecycle, then repeats recovery in
97.238 seconds with zero watchdog restarts. Existing classic and tree publisher tests additionally prove
namespace-selective replay retirement and fresh handling after retirement; the direct owned registry
remains 831.

This makes the recovery sequence executable and repeatable. It does not prove that the backup is
physically or administratively independent, that its generation was selected correctly, that the
RecallRoot phrases or backup will remain available, that storage honors durability claims, or that
important data should use IoTox as its only recovery path. The 24-hour, near-ceiling, abrupt-power,
ENOSPC/read-only, open-descriptor, and independently retained-backup gates remain open.
