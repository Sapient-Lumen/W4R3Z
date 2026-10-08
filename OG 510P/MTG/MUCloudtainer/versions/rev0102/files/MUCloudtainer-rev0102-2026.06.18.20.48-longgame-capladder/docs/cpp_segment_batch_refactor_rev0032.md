# rev0032 — C++ segment batch refactor

rev0031 proved that no-choice forced-action runs could be checked by C++ segment execution. However, the checker still finalized segment signatures game-by-game. rev0032 adds a batched finalization path:

```text
Python-authoritative public games
  ↓
collect all no-choice segment transition records
  ↓
call C++ segment executable once for the whole panel
  ↓
compare C++ end SIGv2 to Python end SIGv2 per segment
```

The new API is:

```python
run_nochoice_segment_cpp_panel_batched(specs, revision="rev0032")
```

The old per-game path remains available. The new batched path is the one future high-volume scripts should prefer.

## Actor-refresh bug fixed

The segment kernel exposed a real C++ carry-state bug. The one-action microkernel parses a fresh `actor` field for every transition. The segment kernel carries state across a sequence, so it must refresh the action-local `actor` field before each record.

rev0032 fixes `cpp/muc5_transition_segment.cpp` so it updates:

```cpp
st.actor = to_i(rec, 35, st.actor);
```

for each subsequent record in the segment. It deliberately does **not** refresh `active_player`, `priority_player`, `frame`, or other engine state from the new record, because those must be produced by the previous C++ transition. Refreshing those would hide transition drift.

This is exactly why the C++ path remains shadowed by Python fingerprints: segment batching is useful only while it continues to match the semantic reference.
