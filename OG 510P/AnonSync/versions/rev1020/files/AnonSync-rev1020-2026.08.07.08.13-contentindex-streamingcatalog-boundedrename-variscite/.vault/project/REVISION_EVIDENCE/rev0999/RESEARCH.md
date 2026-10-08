# Rev0999 research and speculation

The bounded-byte delta path was audited against its retained-history access shape. The key scale observation is multiplicative: a 4 TiB file at 64 MiB per response permits 65,536 transfer turns, so even an apparently modest O(history) action per turn becomes dominant for a multi-terabyte media tree.

The retained design follows a database principle rather than a new protocol: use fixed metadata cutpoints for identity, indexed primary-key ranges for bounded evidence, and exact-path queries for one predecessor. Keep complete causal validation at the single terminal admission boundary where it still protects semantics.

The next measured question is whether the now byte-bounded and history-bounded path remains stable under sparse multi-terabyte files, restart, cold page cache, high latency, and controlled ENOSPC. Cross-file chunk discovery should follow only if it can preserve these bounded access shapes.
