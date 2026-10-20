# ADR 0123: persist live sync attempts before receive

Status: accepted

Date: 2026-08-21

## Decision

Every namespace that enables network synchronization owns one bounded canonical
`iotox-sync-attempt-journal-v1` record signed by the stable device. The journal stores a monotonically
burned attempt-ID high-water mark and only the immutable object, exact route key, and worker
incarnation for attempts that may have received bytes. Tox friend/file numbers are deliberately not
durable identities.

The attempt ID is persisted before scheduler assignment. Failure after that point may waste an ID but
cannot reuse it. After assignment, the transfer coordinator persists the complete active attempt under
the namespace transaction before asking the worker to resume an offer. Terminal processing commits or
discards staging, removes the active journal entry, and only then completes or fences the process-local
scheduler. A terminal event remains retained in the coordinator when a retryable filesystem or journal
operation fails, so draining the worker queue cannot lose the only completion fact.

At startup, recovery never resumes a Tox handle. For each signed active record it first verifies an
already committed digest-named object. Otherwise it attempts the same strict staging-to-object commit.
Complete valid bytes become committed recovery evidence; absent or corrupt staging is safely discarded
and classified fenced. Unexpected links, corrupt final objects, I/O uncertainty, foreign signatures,
and malformed state fail closed without clearing the active record. All successfully classified
records are removed in one signed journal replacement, making recovery idempotent across another
power cut.

Terminal scheduler tombstones remain process-local because a prior process's event queue and worker
incarnations do not survive restart. The durable high-water mark prevents ordinary ID reuse without
growing a permanent tombstone list.

## Consequences

The immutable transfer path now has restart reconstruction at its storage boundary: a crash after
receive admission cannot silently become an untracked reassignment, and a crash after object commit
does not require trusting a lost callback. The journal cannot authorize HEAD acceptance, activation,
retention, or deletion.

The stable signature and previous-record digest detect alteration and bind ordinary sequential
replacement, but do not defeat coordinated replay of a complete older journal. Worker-incarnation
change, no-clobber staging, content verification, and conservative recovery keep such replay from
retargeting live bytes; an external monotonic witness remains outside the claim. Agent startup still
has to invoke recovery before enabling a namespace, and the remote object request/offer record is not
yet frozen.
