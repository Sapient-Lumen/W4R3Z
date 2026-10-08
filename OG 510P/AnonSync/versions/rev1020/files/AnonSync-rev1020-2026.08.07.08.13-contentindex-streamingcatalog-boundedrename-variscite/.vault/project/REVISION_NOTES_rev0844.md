# AnonSync rev0844

## Mission increment

A recovery witness must not merely describe bytes that might eventually exist.
It may authorize rename or deletion only after the complete intended payload is
frozen, synchronized, bound to one retained namespace, and recoverable under an
explicit state machine.

Rev0844 turns the local JSONL replay replacement into one descriptor-relative
crash protocol. The parent directory, lock name, ledger, journal, journal
staging name, and exact temporary are no longer reopened through unrelated
absolute-path calls.

## Severe defect found and corrected

The first implementation direction published the journal before materializing
the replacement temporary. Pre-commit recovery could then treat a journal's
family-looking temporary name as deletion authority even when the file was
partial or had been rebound to unrelated bytes. That is the wrong authority
order.

The production order is now:

1. create the exact temporary beneath the retained parent directory;
2. write and fsync the complete replacement;
3. create, write, and fsync a journal staging inode;
4. publish the journal with a no-overwrite `linkat`, retire the staging name,
   and fsync the directory;
5. rename the still-open temporary over the ledger and fsync the directory;
6. unlink the journal and fsync the directory again.

A visible v3 journal therefore binds a temporary that was complete and fsynced
before witness publication. Recovery validates its digest and complete
canonical chain before any temporary retirement, on both the pre-rename and
post-rename sides of the state machine.

## Delivered

- Added `LocalJsonlReplayNamespace`, a move-only, process-incarnation-bound owner
  of a retained parent-directory descriptor and the ledger family's reserved
  member names.
- Converts the selected ledger spelling once to an absolute lexical path,
  traverses every parent component descriptor-relatively with symlink rejection,
  and proves every later traversal still reaches the retained `(device,inode)`.
- Performs ledger, lock, journal, staging, temporary, link, rename, unlink, and
  directory-sync operations with `*at` syscalls beneath that authority.
- Binds the advisory lock descriptor back to the current lock pathname on every
  namespace proof; unlink-and-recreate cannot silently split cooperating writers
  across different lock inodes.
- Introduces canonical journal v3 with `previous_payload_sha256` and one strictly
  parsed implementation-minted temporary name. Exact v2 recovery remains
  read-only compatible.
- Uses a fsynced staging inode and no-overwrite hard-link publication. Recovery
  recognizes only absent, staging-only, final-only, or an exact two-name/two-link
  pair for the same journal inode.
- Preserves staging-only and pre-journal temporary residue instead of guessing
  that a family-looking name may be deleted. Such residue blocks later commits
  until explicit operator policy resolves it.
- Rechecks the exact loaded ledger payload before creating any recovery witness.
- Adds an explicit pre-commit rollback counter to backend statistics and
  reporting.
- Adds 172 focused runtime checks and a 37-obligation structural audit covering
  namespace rebinding, parent symlinks, lock rebinding, fork inheritance,
  journal topology, stale state, every named crash frontier, forged temporary
  names, and rebound temporary bytes.

## Validation

The exact record is in
`REVISION_EVIDENCE/rev0844/validation/VALIDATION_SUMMARY.json`.

The final active source passed a GCC 14.2 Debug all-target build, a quiescent
no-work rebuild, all 140 registered tests with exact range accounting, all 40
registered source/architecture audits, a Clang 17 `-Werror` focused lane, and a
GCC 14 ASan+UBSan focused lane with leak detection.

## Scope limits

This is a logical crash-state-machine proof, not a claim of arbitrary
instruction/block power-loss completeness on every filesystem and storage
stack. The retained parent descriptor defeats parent-path rebinding, but POSIX
does not provide unlink-if-inode or rename-if-inode primitives; a hostile actor
with concurrent write authority inside the same retained directory can still
race name-based mutation. Deployment must make that directory writer-exclusive
or add a stronger privileged mediation boundary.

The Linux 4.4 host cannot execute an `openat2` lane. Rev0844 also does not claim
Windows runtime coverage, automatic orphan garbage collection, distributed
convergence, payload confidentiality, anonymity, metadata hiding, forward
secrecy, post-compromise recovery, hostile-parser isolation, or secure erasure.
