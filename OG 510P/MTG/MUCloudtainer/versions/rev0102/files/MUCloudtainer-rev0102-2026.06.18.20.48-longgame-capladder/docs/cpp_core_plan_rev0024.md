# rev0024 C++ core plan

The long-haul direction remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels and eventual high-throughput referee core
```

rev0024 does not add a new C++ kernel. That is deliberate.

Instead, the new learned-mulligan evaluation traffic is routed through the existing batched C++ trace checker:

```text
1,953 trace events
0 skipped events
0 mismatches
0 Python replay errors
```

This keeps C++ development disciplined. Every new policy family should produce traffic that still passes the C++ parity checker before we rely on C++ for bulk rollouts.

Current C++ seam ladder:

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel initial cases
rev0018: stack/choice transition expansion
rev0019: recorded-trace transition checker
rev0020: Jace ultimate explicit shuffle transport
rev0021: batched recorded-trace checker
rev0022-rev0024: new policy traffic must pass batched C++ trace gates
```

The next C++ target should not be a blind full rewrite. It should be a batch rollout sketch driven by recorded/prepared public traces or a tightly bounded rollout kernel whose signatures are compared against Python after every action.
