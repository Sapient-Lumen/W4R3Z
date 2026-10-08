# Branchmergefold audit/refactor

`src/i2p_dht_lab/branchmergefold.py` makes the rev0027 merge auditable. It verifies:

- current rev0027 modules/tests/docs exist;
- the spoken rev0026 schedjoin branchlet remains regression-visible;
- the unspoken rev0026 lineage/workmeter branchlet remains regression-visible;
- merged branchlet docs are mapped instead of overwriting the schedjoin rev0026 doc numbers;
- public pointers, head registry, docs index, and surface ledger point to the current path.

This is deliberately boring cube hygiene. The DHT design is now large enough that losing ideas by filename collision is itself a technical risk.
