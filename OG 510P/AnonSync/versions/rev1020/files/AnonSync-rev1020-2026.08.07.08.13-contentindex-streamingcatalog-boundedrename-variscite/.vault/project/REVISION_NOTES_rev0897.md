# AnonSync rev0897 revision notes

## Mission increment

Rev0897 keeps the project centered on authority-preserving convergence. It
closes the operational gap between durable outbox-clock quarantine and the
product executable: the shipped process can now publish a clock-only
observation and perform exact generation-fenced recovery without claiming work
or inventing a parallel clock authority.

The audit also corrects database targeting. Commands that observe, recover, or
send now require an existing replica store. A path typo can no longer become a
new empty authority database merely because all opens inherited
`SQLITE_OPEN_CREATE`.

## C++ implementation

`SyncReplicaSqliteOwner` now exposes
`observe_outbox_clock_or_throw()`. The method owns `BEGIN IMMEDIATE`, restores
the complete state, samples the injected clock under writer authority, publishes
through the same exact-CAS helper used by lease transitions, independently
re-attests the staged cutpoint, and returns accepted/quarantined/sticky state.

The internal clock path was refactored so probe and work operations share
`publish_outbox_clock_observation_or_throw`. Work paths retain their previous
behavior: a quarantine cutpoint commits and the attempted lease transition
throws. The explicit probe instead returns the exact quarantine result and
spends no dispatch authority.

`anonsync_replica` adds:

- `clock-observe`, with system or explicitly paired operator-trusted clock
  profile options; and
- `clock-recover --expected-observation-generation N`, which invokes the
  existing sticky-quarantine recovery primitive.

Both commands emit bounded flat JSON naming health, anomaly, high-water epoch,
observation/recovery generations, and accepted/rejected evidence presence.

## Database-open audit/refactor

`open_database_or_throw` now requires an explicit `DatabaseOpenDisposition`.
Status, clock observation/recovery, and send use `ExistingOnly`. Enqueue and
membership publication retain deliberate creation; `serve-one` requires
existing membership/anchor stores and may create receiver/effect stores.

The SQLite acquisition frontier now keeps the candidate `sqlite3*` in a
distinct exception-safe acquisition owner until open succeeded, the handle is
non-null, and `sqlite3_db_readonly(..., "main")` proves writability. Failed or
read-only candidates are closed before an exception is raised, including when
diagnostic construction or strict-owner allocation itself throws. This follows
SQLite's published contract that a handle is usually returned even on open
error and must be closed.

Existing-only opens additionally require at least one persistent non-internal
schema object and an already-WAL journal profile. A pre-existing empty file
therefore cannot be promoted to genesis by status/send/clock commands, and a
wrong DELETE-mode SQLite database is rejected without first changing its
persistent journal mode. Creation-capable commands enable WAL only for a
schema-empty bootstrap target and then verify that SQLite actually selected it;
nonempty targets must already carry WAL regardless of command.

`serve-one` now validates TLS credentials, binds the listener, restores existing
anchored membership, and only then opens creation-capable receiver/effect
stores. This prevents invalid preflight inputs from leaving empty authority
files.

## Proof and audits

The product process test now proves:

- missing status and clock targets return exit 1 with no stdout;
- no main/WAL/SHM database family is created for a typo;
- a pre-existing zero-byte database remains byte-empty and gains no sidecars;
- an unrelated DELETE-mode SQLite database remains byte-identical;
- a creation-capable membership open also leaves that nonempty wrong-role
  database byte-identical and does not create its paired anchor;
- failed-open diagnostic handles do not trigger the strict owner exit-86 path;
- missing membership during `serve-one` preflight creates no receiver/effect
  stores;
- healthy clock publication, source-change quarantine, status visibility,
  exact recovery, and repeated-recovery rejection;
- real mutual TLS delivery, exact receiver bytes, and terminal settlement after
  recovery.

The SQLite owner test adds a focused clock-only lifecycle and verifies that
observation/quarantine/recovery do not change replica evidence, policy,
operations, projection, or outbox authority.

`tools/audit_anonsync_replica_database_open_policy.py` pins explicit creation
policy, failed/read-only closure before adoption, and receiver preflight order.
The existing outbox-clock audit now pins the public probe, CLI recovery surface,
owner proof, and process lifecycle.

## Research and dependency status

SQLite's official documentation confirms the failed-open handle and read-only
fallback behavior addressed here. Official pages reported SQLite 3.53.4,
released 2026-07-24, and published SHA3-256
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`
for the 3.53.4 amalgamation ZIP. The cloudtainer could not acquire and verify the
archive bytes, so AnonSync remains exactly pinned to the bundled, configure-time
verified SQLite 3.53.3. No 3.53.4 upgrade is claimed.

## Remaining gaps

The next database-boundary correction should be an explicit store-set `init`
command and durable deployment manifest. Normal commands should eventually
require existing stores, eliminating implicit bootstrap and partial creation
across membership/anchor or receiver/effect pairs.

The largest product gap remains a bounded durable supervisor with explicit
operator/policy authority for clock recovery. Directory/tombstone/rename
semantics, reachability/GC, indexed scale, at-rest encryption, and a real privacy
threat model remain absent. TLS authentication still does not provide
anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance.

Detailed findings and the recommended sequence are in
`PRODUCT_CLOCK_RECOVERY_AND_DATABASE_TARGET_AUDIT_rev0897.md`.
