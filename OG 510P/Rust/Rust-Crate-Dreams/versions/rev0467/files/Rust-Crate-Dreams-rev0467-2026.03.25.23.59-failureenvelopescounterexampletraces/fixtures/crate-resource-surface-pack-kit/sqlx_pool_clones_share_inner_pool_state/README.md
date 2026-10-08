# Scenario — sqlx pool clones share one pool budget

This scenario exists so the archive can distinguish a cheap clone handle from constructing another pool.

The important support truths are:

- clone does not multiply the pool budget,
- the shared pool remains one waiting room,
- and independently constructed pools still multiply total database-side resource usage.
