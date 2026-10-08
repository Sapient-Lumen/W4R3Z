# Rev0944 focused audit

## Mission guard

The change serves the Resilio-replacement product directly. It reduces measured
many-file payload-store cost in the shipping C++ folder owner. Verification and
lease vocabulary remain implementation discipline, not a competing mission.

## Severe waste corrected

Before rev0944, each one-file publication could acquire its own mutation lease
and rescan/re-hash every older payload. Rev0944 composes one move-only mutation
batch into a local folder traversal. Construction performs one complete bounded
scan and capacity calculation; successful create-new publications update one
exact sorted in-memory index. One-put APIs delegate to the same implementation.

A retained exact verification cache separately avoids rereading unchanged bytes
on later scans. Reuse requires the exact identity-marker inode and exact payload
`dev`/`ino`/type/mode/link/uid/gid/size/mtime/ctime observation. Anything cold,
new, replaced, or changed follows the complete hash path. Cache replacement
occurs only after complete traversal and final lease/root proof.

## Authority-lifetime audit

The folder owner releases the exclusive batch before remote shared payload reads,
network waits, and the absence phase. A mixed pass may reacquire after applying a
remote successor. A long local traversal can still retain the cooperative lease,
which is now an explicit target-scale measurement and segmentation concern.

The combined merge found exceptional recovery still calling the old scan
signature. The correction intentionally supplies no cache: after publication
ambiguity, durable namespace reconciliation is cold. If reconciliation cannot
classify the state, the batch is poisoned.

## Test and release-policy defects corrected

The replacement test now separates same-inode overwrite from atomic replacement
with both inodes alive. Both wrong-byte cases fail; exact repair, marker rebind,
restart, and forensic inspection exercise their respective cold/hash paths.

The draft wrapper verifier would have rejected the cube's intentionally retained
hidden donor namespaces even though only `BOOTSTRAPROSE.md` is visible. The policy
now admits the exact known hidden namespaces and rejects unknown visible or vault
content. Executable fixtures cover the real layout.

## Remaining boundary

Every batch/snapshot still enumerates, opens, and stats the full namespace. The
cache is restart-cold and no durable exact index or rotating full-byte scrub
exists. Batch-created entries receive one conservative hash on the next retained
scan. The next scaling move is a crash-consistent incremental metadata owner with
bounded scrub and lock horizons, not removal of the cold scanner.
