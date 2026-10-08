# rev0879 compact audit record

## Load-bearing correction

Rev0878 reopened the configured effect root from pathname text for each effect.
A same-path directory replacement between calls could therefore redirect a later
publication while SQLite continued to describe the old namespace spelling.
Rev0879 retains one process- and thread-affine POSIX directory capability,
freezes its kernel-visible attestation, persists the attestation digest in exact
file-effect schema v2, and resolves effect destinations descriptor-relative
beneath that root. A live path replacement permanently revokes the capability;
a restart against a replacement object rejects the stored root digest.

## Second defect found during adversarial review

Retaining the root did not by itself bound intermediate directory authority. The
rooted traversal now rejects a destination parent component that crosses the
root device, is not owned by the retained effective UID, lacks owner
read/write/search, or grants group/other write. Rejection occurs before any temp
inode reservation. A runtime test proves the effect remains staged and retryable
until the descendant policy is restored.

## Refactor and audit correction

The former local-JSONL-specific directory owner is now a thin facade over the
shared `SyncDirectoryAuthority`; it no longer duplicates traversal, descriptor,
attestation, process/thread, move, or sticky-revocation state. Rooted and
absolute atomic publication likewise share one syscall state machine through a
verifier callback. An older thread-incarnation source audit initially failed
because it still expected the facade to own a direct thread field. The gate was
corrected to follow the shared capability and to require that the facade has no
parallel affinity implementation; the final complete registry is green.

Source audits are lexical architecture inventories, not behavioral proof. The
load-bearing evidence is the adversarial runtime corpus, full registered test
run, independent compiler lane, sanitizers, and repeated root-rebind stress.

## Remaining severe boundaries

The shipped `anonsync_core` executable still does not use this new owner path.
The portable `st_dev` check does not distinguish a same-device bind mount;
Linux `openat2(RESOLVE_NO_XDEV)` or `statx` mount IDs remain future hardening.
Same-UID and privileged local actors, Windows retained-root parity, authorized
root rebinding/migration, production-scale indexing, ordinary update/delete/
rename effects, complete retry/dead-letter policy, membership/key lifecycle,
compaction, anonymity, externally signed provenance, and formal proof remain
outside the claim.
