# rev0045 C++ core plan

rev0045 adds no new C++ kernel. It uses the existing transition shadow checker on branch-heavy label traffic:

```text
17,432 checked transitions
0 skipped transitions
0 mismatches
```

The C++ path remains staged:

```text
1. Numeric deck-probe kernels            done
2. Legal-menu differential harness       done
3. One-action transition microkernel     done
4. Stack/choice/ultimate coverage        done
5. Recorded trace checker                done
6. No-choice segment checker             done
7. Branch/payoff shadow checking         ongoing
8. Full rollout core                     later, only under Python parity gates
```

The immediate research bottleneck is label yield, not C++ throughput. C++ should remain attached as a parity shadow until branch collection becomes clearly speed-limited.
