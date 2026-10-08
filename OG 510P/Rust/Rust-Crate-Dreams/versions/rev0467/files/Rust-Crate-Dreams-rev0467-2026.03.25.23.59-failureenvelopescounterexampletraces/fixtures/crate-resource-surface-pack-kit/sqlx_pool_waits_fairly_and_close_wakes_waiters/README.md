# SQLx pool wait / fair acquire / close-wakes-waiters scenario

Focus: SQLx documents both fair waiting and `close()` semantics that wake current and future waiters with `PoolClosed`.

Resource-surface reading: acquire fate is part of the support contract, not just pool size.
