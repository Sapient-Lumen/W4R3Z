# rev0010 refactor/audit notes

## Refactors/fixes

### Sequential Overlord triggers

Before rev0010, multiple attacking Overlords drew all cards before any discard choice. That was a subtle information advantage. rev0010 adds `_begin_overlord_trigger_sequence(...)` so each trigger exposes its discard decision before the next trigger draws.

### Jace -1 target-state actions

Before rev0010, Jace -1 only chose a target player and then bounced the first available Overlord by internal priority. rev0010 includes `target_state=ready|sick|tapped` in legal actions. Impending Overlords are not legal creature targets.

### Simulator readiness module

Added `src/muc5/readiness.py` to keep directed scenarios, fuzzing, and readiness reporting out of the core engine.

## Audit additions

- `scripts/run_rev0010_rules_scenarios.py`
- `scripts/fuzz_simulator_rev0010.py`
- `scripts/profile_simulator_rev0010.py`
- `scripts/simulator_readiness_rev0010.py`
- `tests/test_rev0010_simulator_readiness.py`

## Policy

Every future simulator-touching revision should add at least one of:

```text
new directed scenario
new fuzz invariant
new leakage check
new deterministic replay fixture
new performance measurement
```
