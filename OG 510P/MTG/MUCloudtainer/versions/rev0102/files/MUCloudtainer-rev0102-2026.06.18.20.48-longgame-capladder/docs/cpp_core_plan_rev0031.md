# rev0031 C++ core plan

The long-haul direction is C++ where suitable, but the authority boundary stays deliberate:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

Completed C++ seams:

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel initial cases
rev0018: stack/choice transition expansion
rev0019: recorded-trace checker
rev0020: Jace ultimate shuffle transport
rev0021: batched trace checking
rev0026: live C++ shadow rollout seam
rev0031: no-choice segment checker
```

The next C++ step should not be a blind port of the whole simulator. It should be:

```text
Python detects forced no-choice segment
Python records pre SIGv2
C++ applies the whole segment
Python verifies post SIGv2
```

Only after this works inside live rollouts should we consider a larger C++ rollout kernel.
