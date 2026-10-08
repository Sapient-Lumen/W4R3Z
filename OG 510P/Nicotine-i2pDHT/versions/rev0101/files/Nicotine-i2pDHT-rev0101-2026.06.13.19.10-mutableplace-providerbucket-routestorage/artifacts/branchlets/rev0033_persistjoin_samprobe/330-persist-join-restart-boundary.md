# Persist join restart boundary

Restart is a protocol boundary. A node that forgets hard negative evidence, replays a stale journal tip, or suppresses store repair after a convenient checkpoint can resurrect bad state.

`persistjoin.py` treats these reports as separate evidence surfaces:

- `PersistLoadReport`
- `JournalReplayReport`
- `CheckpointAssessment`
- `ScopeLedgerReport`
- `StoreDebtReport`

The join rejects or holds when:

- persisted reload quarantined or lost hard negatives;
- journal replay quarantined;
- checkpoint assessment quarantined;
- checkpoint journal tip does not match the replayed journal tip;
- scope ledger carries proof debt;
- store repair/custody debt remains;
- joined report digests are replayed or aliased.

The deliberately conservative guess is that durable restart acceptance should require the boring exactness of all local lanes at once. A valid component report is not a valid durable advance.
