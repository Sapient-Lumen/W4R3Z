# Scenario — reqwest client clones share one pool, but the bound is still per host

This scenario exists so the archive does not let a reusable client sound like each clone creates an independent pool.

The important support truths are:

- clones share the same underlying client state,
- the pool is meant to be reused,
- and `pool_max_idle_per_host` is a **per-host** bound rather than a whole-process connection total.
