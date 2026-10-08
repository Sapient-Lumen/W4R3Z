# AnonSync rev0811 revision notes

## Mission-level result

Rev0811 turns checkpoint ownership from a property of one transient owner row
into durable protocol memory. Once an owner generation has been minted, release
or checkpoint replacement can no longer make the session appear never owned.
Every later mutation must present a current exact capability or first acquire a
successor generation, unless a separately evidenced administrative transition
has disabled ownership.

This preserves AnonSync's central invariant: authority must be checked by the
recipient that owns the transition, on the exact durable snapshot and lifetime
that will contain the effect.

## Parent and lineage

The source basis is the exact extracted content of:

`AnonSync-rev0810-2026.07.17.12.30-stickyowner-resetfence-privatepermit-transactionaudit.zip`

SHA-256:

`99da2dc69724cd085b5739f6913509b151f57383b464264871267a82e500c0ba`

The parent was usable as source but was not verifier-clean as a rev0810 release.
Its archive used the long filename as the only root instead of `AnonSync/`; its
release gate still declared rev0809; its primary manifest omitted the rev0810
fallback note, alternate manifest, and two reference files; and its sticky-owner
implementation was only a standalone sketch outside production CMake, runtime,
and CTest. Exact failing reports are retained under
`REVISION_EVIDENCE/rev0811/lineage/`.

No build product was used as source. No third-party source changed.

## Defects corrected

### 1. Release laundered owned state into capability-free mutation

The rev0809 policy allowed an empty capability when the durable owner row was
`released`. That meant successful enrollment into owner-fenced mode was not
sticky. A caller could release its generation and then mutate through an
unowned path.

Rev0811 introduces a durable `owner-required` mode row outside the checkpoint
root's cascade. Release retires the live owner row but compare-and-replaces the
mode timestamp without disabling ownership. A released generation cannot be
presented again, and an empty capability is rejected until a successor is
minted.

### 2. Root reset erased the only ownership evidence

`sync_session_resume_transfer_daemon_owner_locks` is a checkpoint child. Deleting
`sync_session_checkpoints` therefore invokes the reviewed foreign-key cascade
and removes the owner row. The old reset path could recreate a checkpoint that
looked never owned.

The independent mode row survives that cascade and retains the latest owner
generation. A post-reset acquisition increments the durable mode generation,
not an absent child row, so reset cannot rewind generation history.

### 3. Destructive reset authorization was orchestration-owned

The large domain translation unit directly issued the checkpoint-root `DELETE`.
That separated recipient authorization from the destructive operation and made
it easy for later call sites to bypass the owner boundary.

Root deletion now has one focused C++ owner. A private
`CheckpointRootResetPermit` is issued only after the exact capability has been
verified in the exact live typed write transaction. The permit is noncopyable,
nonmovable, single-use, and binds the SQLite handle, transaction generation,
session, mode snapshot, and reset epoch. The delete and mode proof occur before
the same transaction commits.

### 4. Repair paths lacked successor authority

After sticky mode was integrated, the operator recovery workflow correctly
failed: it attempted a legitimate checkpoint repair after the previous owner
had been released but did not acquire a successor. The standalone repair CLI
had the same gap.

Both paths now use a scoped internal lease that mints a database successor,
passes its exact capability into recipient options, and retires the same
capability. Workflow, direct operator, and standalone CLI tests lock in that
lifecycle.

### 5. Recipient time admitted values SQLite cannot persist

Acquisition already rejected values above SQLite's signed 64-bit integer
ceiling. Recipient observation/reset epochs previously rejected zero but not
`INT64_MAX + 1`. Rev0811 rejects that range before any destructive SQL or value
binding. The SQLite test proves an out-of-range unowned reset leaves the root
intact.

## Production changes

- Added `StoredOwnerModeEvidence` to the pure transition policy.
- Added exact combined validation for mode and owner rows.
- Added monotonic generation planning from independent mode evidence.
- Added legacy owner-row backfill into `owner-required` mode.
- Added `sync_session_checkpoint_owner_modes` with no checkpoint-root foreign
  key.
- Added exact compare-and-replace updates for acquisition, release, and reset.
- Added private transaction-bound `CheckpointRootResetPermit`.
- Centralized checkpoint-root deletion in the owner-recipient boundary.
- Converted checkpoint replacement to the typed RAII SQLite transaction.
- Added owner capability and observation epoch to checkpoint options.
- Added internal acquire/release wrappers for repair-owner leases.
- Added scoped repair-owner lifecycle to workflow, direct repair, and CLI paths.
- Expanded domain tests and focused policy/SQLite tests.
- Expanded the source audit from 25 to 38 obligations.

## Source delta

Twelve active implementation files changed. The textual delta is 2,318 added
and 480 removed lines. The large domain unit changed from 15,308 to 15,371
lines; the new authority machinery is concentrated in the independently linked
owner policy and recipient boundary rather than reintroducing direct root-delete
ownership into the domain.

Exact per-file hashes, line counts, and the unified source patch are in:

- `REVISION_EVIDENCE/rev0811/CHANGESET.json`
- `REVISION_EVIDENCE/rev0811/repository_metrics.json`
- `REVISION_EVIDENCE/rev0811/SOURCE_DIFF_rev0810_to_rev0811.patch`

## Validation

- Release all-target build: passed.
- One-shot CTest: 86/86.
- Sync-domain model: 594/594.
- Owner policy: 39/39.
- Owner SQLite proof: 39/39.
- Owner source audit: 38/38.
- Selftest advertisement/registration: 38/38.
- Scheduler separation: 22/22.
- Domain selftest separation: 13/13.
- Ten consecutive policy-plus-SQLite iterations: all passed, 780 focused
  assertions total.
- Strict compilation: 8/8 GCC 14.2 and Clang 17 unit/compiler combinations.
- Focused GCC ASan/UBSan: 2/2 binaries, 78/78 checks. Leak detection and bundled
  SQLite instrumentation were disabled; no full-program sanitizer claim is
  made.

## Remaining boundaries

The sticky mode is local to compliant participants sharing the SQLite database
and VFS. Time remains caller-supplied. There is no production administrative
-disable API yet. The mode table is not yet exact-schema-attested against a
hostile preexisting object. SQLite plus filesystem effects are not one
crash-atomic transaction. Distributed convergence, privacy, key lifecycle, and
cross-device consensus remain separate unproved problems.
