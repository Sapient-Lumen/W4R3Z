# Related-work research pass 020 — model oracles and deterministic simulation

Revision: rev0028

This pass focused on how BrowserRT should test increasingly ambitious scheduler and provider semantics without spending browser/OPFS/GPU budget too early.

## Ideas stolen

### FoundationDB Simulation and Testing

FoundationDB's simulation posture is the strongest inspiration: run a whole system inside a deterministic simulated environment so failures can be repeated. BrowserRT cannot claim that yet, but it can adopt the smaller pattern: deterministic seeds, fake providers, trace artifacts, and reproducible counterexamples.

### TLA+ and PlusCal vocabulary

TLA+ sharpens the distinction between a model and an implementation. BrowserRT's current model proof is executable JavaScript, not a formal spec. The useful theft is the habit of naming states, transitions, invariants, and forbidden claims.

### Model-checking model checking

Model-checking's actor/model-checking framing suggests a future where BrowserRT agents and providers expose transition surfaces that can be explored systematically. Rev0025 does not do exhaustive exploration; it prepares the office vocabulary.

### Kubernetes Scheduling Framework

Kubernetes' scheduler framework divides scheduling into extension points and plugin-like phases. BrowserRT should eventually treat lane admission, scoring, reservation, fallback, binding, and unreserve/recovery as separate hooks rather than one opaque dispatch function.

### Jepsen and history checking

Jepsen's discipline is not just testing; it is comparing observed histories to documented claims. BrowserRT should record histories and never make a claim without a checker that can falsify it.

### Hypothesis / fast-check style stateful testing

Stateful model testing compares a real implementation against a simple model across command sequences. That is the direct shape of `scheduler:cross-lane-model-walk-proof`.

## Resulting design pressure

Every serious BrowserRT provider should eventually have:

```txt
implementation
reference model
seeded command generator
history artifact
invariant checker
counterexample replay
non-claim boundary
```

## What entered the cube

- `docs/20-architecture/cross-lane-scheduler-model-frontier.md`
- `docs/40-validation/cross-lane-model-walk-slice.md`
- `tools/cross_lane_model_walk_probe.mjs`
- `tools/scheduler_model_contract_audit.mjs`

## Non-import policy

No external code, dependencies, assets, or hosted services were imported. Only ideas and vocabulary entered the cube.
