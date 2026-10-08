# Claim/evidence ladder — rev0074

A test can prove exactly what it asserts and still support the wrong product decision. Future packet reviews use this ladder and must record the highest rung actually reached.

| Rung | Question | Typical evidence | What it does not imply |
|---:|---|---|---|
| 0 | Can a source pattern be located? | source trace, AST/static check | runtime behavior |
| 1 | Can an internal state be constructed? | unit harness with assigned objects/maps | protocol reachability |
| 2 | Does current code make the transition? | exact-current behavior witness | that the transition is undesirable |
| 3 | Can protocol-valid input reach it? | parser/state-machine test with required tokens and ordering | arbitrary attacker control |
| 4 | Can an untrusted peer reach it under realistic ownership constraints? | two-ended or integration trace | material security impact |
| 5 | What concrete impact follows and persists? | bounded metrics, user-visible corruption, privilege/boundary crossing | severity beyond the measured case |
| 6 | Is the desired policy compatible and complete? | compatibility controls, reconnect/liveness cases, historical intent | implementation correctness |
| 7 | Does a candidate patch satisfy the policy without regressions? | focused regressions plus native/integration suites | upstream suitability under project policy |

PB-01B had reached rung 2 in the old packet, but its arbitrary-attacker interpretation was treated as though rung 4 had been reached. Rev0074 closes rung 3 and finds a locally authorized direct/indirect race plus explicit compatibility history. The defect claim is therefore retired on current evidence.

PB-01A reaches rung 3 for a direct `PeerInit` username/type claim. It does not reach a trustworthy election policy at rung 6 because the protocol message does not authenticate a generation and the old first-established-wins design has stale/reconnect risks.

Rules for future work:

1. Label synthetic construction separately from protocol reachability.
2. Add a negative policy or counterexample test before calling a patch selected.
3. Treat commit history and issue context as evidence of compatibility constraints, not mere background.
4. Record missing rungs in the packet ledger.
5. Never promote a packet because a regression suite written for one design turns green.
