# Garden scheduler

Garden nodes give capacity, but they are not infinite sinks.  `gardenrefusal.py` already handled one admission window; rev0015 adds `gardenscheduler.py` for multi-window pressure.

## Protected work

The scheduler gives special attention to:

```text
head_watch
witness_query
seed_gate
```

Bulk provider and region reprovide work are important, but they must not starve the control-plane functions that keep mutability, evidence, and entrances alive.

## Useful refusal across windows

A garden can refuse work with signed retry hints.  The scheduler then carries still-live work into later windows after resource refill.  This is intentionally not payment and not global reputation.  It is local operator hygiene: a good garden should refuse clearly rather than silently drop.

Decision kinds:

```text
scheduled_all
scheduled_with_refusals
dropped_invalid_only
starvation_pressure
```

`starvation_pressure` is the dangerous one: protected work remained unscheduled after all windows.

## Dream direction

A future garden node UI could show these counters:

```text
protected work accepted
bulk work deferred
useful refusals issued
families capped
starvation pressure detected
```

This makes generosity legible without turning gardens into authorities.
