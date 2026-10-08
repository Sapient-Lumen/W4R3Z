# C++ core gameplan

The forward product should be a small policy decision and idempotency kernel, not an ever-growing archive of generated evidence.

The retained C++ path owns request/event normalization, operation-contract binding, JWT and signed-policy verification, a replay-ledger interface, SQLite/WAL persistence, backup snapshots, signed restore, and local rollback/prefix checks. Python is limited to validation, audit generation, and packaging.

Rev0619 changes the build order. Restore integrity remains supported, but the next product work should establish an independent operator trust configuration, a real request adapter, proof-of-possession, event identity deduplication, and a reserve-before-side-effect protocol. Only after those boundaries exist should the cube invest further in restore ceremony or generated corpus growth.
