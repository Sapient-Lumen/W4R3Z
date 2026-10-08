# Simulator status after rev0020

The simulator is now an automated beta with a stronger C++-audit path.

## Working surfaces

```text
five-card exact referee
hidden-information observations
legal macro-action menus
London mulligan agency scaffolding
20/40 life dial
public DecisionFrame interface
replay traces
promotion/statistical gates
C++ deck probes
C++ legal-menu differential checker
C++ transition microkernel
C++ recorded-trace checker
Jace ultimate shuffle transport
```

## C++ trace status

rev0020 trace check:

```text
36 traces
8,898 events
8,898 C++-supported transitions
0 skipped transitions
0 mismatches
30 Jace ultimate events checked
```

This is a strong sign that sampled public-agent traffic can be mirrored by the C++ transition microkernel. It is not a proof that C++ is ready to replace Python as the full referee.

## Learning-facing status

rev0020 also adds an imitation/action-ranker seed. It produces public-safe candidate-action rows and trains a tiny logistic smoke model. This is useful as a low-risk bridge toward neural methods, but it is not a strategic claim.

## Trust level

```text
automated play: yes
public replay/audit: yes
C++ transition parity on sampled traffic: yes
C++ full engine: no
learned strategy claims: not yet
```
