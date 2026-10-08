# Read-repair store pressure — rev0019

`readrepair.py` makes replica observations typed before repair work begins. A read result can be exact, missing, stale, wrong-digest, tombstoned, refused, or timed out. These are not interchangeable.

The local rule is:

```text
healthy = enough exact reads across enough families
repair = missing/stale/timeouts with bounded family-capped repair actions
quarantine = wrong digest or resurrection pressure
block = live tombstone evidence
```

The important failure mode is stale-cache resurrection. If a live tombstone exists and old replicas still answer the expected digest, that is not success; it is resurrection pressure. The repair planner refuses to turn old exact reads into truth when deletion/withdrawal/revocation evidence is live.

Risk tested in `tests/test_rev0019_storeflight_leasequorum_readrepair.py`:

- healthy exact replicas need family diversity;
- repairs are selected with family caps rather than “fix every convenient node”; 
- wrong-digest reads quarantine the round;
- tombstone-conflicting exact reads become resurrection pressure.

This closes another seam before live transport: STORE, lease renewal, readback, and repair are now separate evidence surfaces instead of one vague durability claim.
