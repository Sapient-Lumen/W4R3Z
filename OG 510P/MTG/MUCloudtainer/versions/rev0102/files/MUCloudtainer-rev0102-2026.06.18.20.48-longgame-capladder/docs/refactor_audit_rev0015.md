# rev0015 refactor and audit notes

## Refactors

rev0015 adds three explicit seams:

```text
C++ bridge seam:          cpp/muc5_probe_kernel.cpp + src/muc5/cpp_accel.py
adversarial policy seam:  public stall profile in src/muc5/public_agents.py
neural-prep seam:         src/muc5/action_features.py
```

The C++ bridge is intentionally source-first and rebuilt inside the cloudtainer. The Python path remains the reference. The action-feature encoder prevents future policies from depending on unstable dynamic action slot positions alone.

## New checks

The rev0015 tests check that:

```text
C++ probe kernel compiles and matches Python deck_probe output
stall policy prefers land/pass over proactive threats
stall counters public threats more than irrelevant stack fights
action feature vectors have stable length and expected flags
DecisionFrame action-feature matrices align with legal action count
```

The audit checks that:

```text
rev0015 C++ benchmark exists and matched Python within tolerance
rev0015 MAP-Elites gameplay evaluation passed promotion/statistical gates
rev0015 stall diagnostic detected truncation and failed strict promotion as expected
rev0015 action-feature module and docs/scripts/tests are present
```

## Pushback

Do not port the full engine to C++ until the Python referee semantics are more stable. The best long-haul path is differential testing: C++ should first reproduce Python snapshots, legal menus, state transitions, and replay fingerprints before it becomes authoritative.
