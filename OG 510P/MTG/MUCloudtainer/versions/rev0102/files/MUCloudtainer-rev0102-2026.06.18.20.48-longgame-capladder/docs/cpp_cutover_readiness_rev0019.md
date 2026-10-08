# rev0019 C++ cutover readiness

The long-haul target is a high-performance C++ referee core, but the archive should not become an unsafe port. The current office model is:

```text
Python
  reference semantics
  public DecisionFrame boundary
  replay and promotion gates
  analytics and research iteration

C++
  high-throughput kernels
  stable legal-menu and transition slices
  differential-tested acceleration
```

## Current C++ components

| Component | Status | Authority |
|---|---|---|
| Deck probability probes | Fast and exact against Python | safe acceleration |
| Legal menu enumeration | Differential-tested on gameplay frames | candidate acceleration |
| Transition microkernel | Stack/choice/combat/end-turn subset checked | candidate acceleration |
| Recorded-trace transition checker | Added in rev0019 | audit bridge |
| Full rollout simulator | Not built | not trusted |

## Why not port everything yet?

The Python engine still changes when we discover rule or interface bugs. A full C++ port now would duplicate bugs faster and make debugging harder. The better pattern is to port seams after they stabilize, then force them to match Python on real traffic.

## Current blockers to full C++ rollout

1. Jace ultimate requires explicit RNG/shuffle transport.
2. C++ transition support is high in sampled public traces, but not mathematically complete.
3. A C++ rollout core would need public observation construction or a strict Python/C++ handoff.
4. Promotion/replay/statistical gates still live in Python and should remain there for now.

## Next C++ work

Best next steps:

```text
1. Add an explicit shuffle-record transport for Jace ultimate, or decide to keep ultimate Python-only.
2. Add C++ trace-check coverage summaries by action and phase to catch weak spots.
3. Start a C++ batch rollout prototype that consumes preapproved public policy code only after trace coverage stays stable.
4. Keep Python replay as the final referee for promoted results.
```
