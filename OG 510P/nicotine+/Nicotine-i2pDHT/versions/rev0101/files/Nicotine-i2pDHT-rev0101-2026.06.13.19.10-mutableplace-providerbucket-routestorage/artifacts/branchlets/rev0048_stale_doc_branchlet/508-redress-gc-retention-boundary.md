# Redress GC retention boundary

`redressgc.py` treats local evidence minimization as a protocol boundary. Forgetting is useful, but forgetting the wrong thing can resurrect bad state.

The GC lane preserves:

- live hard negatives;
- deny/freeze pressure;
- active redress lift/watch receipts;
- fork evidence;
- pinned appeal facts.

It drops expired soft evidence and duplicate-family noise under budget pressure. It quarantines scope/request drift, live-hard-negative drops, active-redress drops, fork-evidence drops, and same-sequence conflicts.

This is still toy retention logic, not a production database.
