# Model-walk and deterministic-test frontier

Revision: rev0028

BrowserRT should grow a testing architecture that can keep up with the runtime architecture. The first target is the framed SAB mailbox because it is small enough to model and dangerous enough to deserve more than a happy path.

## The ladder

```txt
1. Example test
2. Deterministic model walk
3. Seed corpus with counterexample preservation
4. Interleaving simulator
5. Browser Worker proof
6. Chaos/history checker
7. Optional formal spec for algorithms that justify it
```

Rev0016 lands rung 2 for the variable-frame mailbox.

## Design pattern

Each provider should eventually expose or accompany:

```txt
reference model
command generator
real-system adapter
invariant checker
history artifact
counterexample format
```

The format matters. A failing test should not say "ring broke." It should say:

```txt
seed: 23551
capacityBytes: 96
step: 73
command: pop
expected: seq 235510042, checksum 3182214
actual: seq 235510043, checksum 11235813
prior commands: [...]
```

## Why this is cloudtainer-friendly

Model walks are cheap, deterministic, and local. They can run in the release tier without launching Chromium. That means they are the right place to spend semantic effort before browser, OPFS, WebGPU, or cross-tab proofs consume a turn's budget.

## Future hazards

- Random tests without reproducible seeds are not acceptable.
- Model walks without a counterexample shape are hard to debug.
- A model that mirrors the implementation too closely is not a model; it is duplication.
- A model test that becomes slow will get skipped and therefore stop protecting the runtime.
- Passing model walks do not justify performance claims.
