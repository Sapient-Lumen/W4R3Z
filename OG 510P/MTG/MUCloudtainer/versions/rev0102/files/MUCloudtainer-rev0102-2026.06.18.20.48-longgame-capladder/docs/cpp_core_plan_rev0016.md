# rev0016 C++ core plan

MUC-5 is now explicitly a **Python reference / C++ hot-core** project.

The long-haul target is a C++ referee core, but not by rewriting the whole simulator in one jump. Python currently owns the semantics that matter most:

```text
hidden-information observations
DecisionFrame boundary
replay traces
promotion/statistical gates
reward/truncation guardrails
scenario/fuzz tests
analysis scripts
```

C++ should take over only the stable kernels whose input/output contracts are already narrow and measurable.

## Current C++ pieces

```text
rev0015: cpp/muc5_probe_kernel.cpp
  exact deck construction probability probes
  Python wrapper: src/muc5/cpp_accel.py

rev0016: cpp/muc5_legal_menu.cpp
  state summary -> legal macro-action strings
  Python wrapper/differential harness: src/muc5/cpp_legal.py
```

The legal-menu kernel is the first bridge toward a C++ referee. It does not mutate game state and does not decide strategy. It only mirrors the Python legal-action generator over a flat state summary.

## Porting ladder

```text
1. deck probes                       done: C++ benchmarked vs Python
2. legal menu enumeration             rev0016: C++ differential tested vs Python
3. state transition microcases         next: C++ apply one macro-action in directed scenarios
4. random rollout kernel               later: C++ state + built-in policy smoke rollouts
5. public DecisionFrame batch rollout  later: C++ engine behind Python agent boundary
6. full tournament core                only after replay/differential gates are strong
```

## Non-negotiables

C++ speed is useful only if the result remains compatible with:

```text
public observation redaction
legal-action mask semantics
mulligan agency
life-total tournament dial
replay fingerprints
truncation labeling
promotion/statistical gates
Python scenario tests
```

The archive should stay cloudtainer-bound and source-first. Future sandpeople should be able to open the cube, compile the C++ sources with the local `g++`, run Python tests, and compare C++ outputs against the Python oracle.

## Why not full C++ now?

The simulator is still evolving. A full C++ port today would likely copy bugs or create new semantic drift. The safer approach is differential porting: build one C++ kernel, compare it against many Python states, and only then expand the seam.

## rev0017 update: transition microkernel added

rev0017 adds the next rung after legal-menu enumeration:

```text
cpp/muc5_transition_micro.cpp
src/muc5/cpp_transition.py
```

The current C++ migration ladder is now:

```text
1. deck probes                         done rev0015
2. legal menu enumeration              done rev0016
3. deterministic transition microcases done rev0017, partial
4. stack/choice transition microcases  next
5. random rollout kernel               later
6. full tournament core                only after broad differential coverage
```

The governing rule remains unchanged: C++ must be faster *and* differentially matched against Python before it becomes authoritative for any slice.
