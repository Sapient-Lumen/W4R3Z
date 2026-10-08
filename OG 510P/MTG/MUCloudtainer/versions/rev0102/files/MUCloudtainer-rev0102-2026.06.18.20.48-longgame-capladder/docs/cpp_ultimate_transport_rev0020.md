# rev0020 C++ Jace ultimate shuffle transport

rev0019 left one explicit C++ transition debt: **Jace ultimate**. The reason was not the loyalty effect itself; it was the shuffle.

Python is still the semantic authority. For C++ differential checking, rev0020 does not try to reproduce Python's RNG stream. Instead it carries an explicit shuffle transcript:

```text
pre-state + ACTIVATE_JACE(mode=ultimate)
  ↓
Python applies the action with authoritative RNG
  ↓
post-state target library order is captured as cpp_shuffle_csv
  ↓
C++ applies the same action using that explicit ordered library
  ↓
compare C++ SIGv2 to Python post-state SIGv2
```

This keeps the long-haul C++ plan honest. We can port deterministic state mechanics while treating random outcomes as externally supplied transcripts until a full C++ rollout core has its own auditable RNG contract.

## New transport seam

`src/muc5/cpp_transition.py` now provides:

```python
with_jace_ultimate_shuffle_transport(pre_state, action, post_state)
has_jace_ultimate_shuffle_transport(action)
```

A legal menu action does **not** carry `cpp_shuffle_csv`. Therefore:

```python
is_supported_transition(pre_state, legal_ultimate_action) == False
```

After Python applies the action and creates the post-state:

```python
transported = with_jace_ultimate_shuffle_transport(pre_state, legal_ultimate_action, post_state)
is_supported_transition(pre_state, transported) == True
```

The hidden `cpp_shuffle_csv` field is for C++ checking only. It is not agent-facing, not part of the legal menu, and not a strategic input.

## C++ behavior

`cpp/muc5_transition_micro.cpp` now supports `ACTIVATE_JACE(mode=ultimate)` when an explicit shuffled-library CSV is present. It performs:

```text
Jace controller loses 12 loyalty
chosen target player's library cards move to exile
chosen target player's hand is cleared
chosen target player's new library becomes cpp_shuffle_csv
state-based checks run afterward
```

The state-based check matters because Jace usually drops to zero or below and goes to the graveyard.

## New result

`data/rev0020_cpp_trace_summary.json` reports:

```text
36 traces
8,898 public decisions
8,898 C++-supported transition checks
0 skipped transitions
0 C++ mismatches
0 Python replay errors
30 Jace ultimate events
30 / 30 Jace ultimate events C++-checked
```

This does not make C++ the full simulator. It closes the known rev0019 trace coverage gap.
