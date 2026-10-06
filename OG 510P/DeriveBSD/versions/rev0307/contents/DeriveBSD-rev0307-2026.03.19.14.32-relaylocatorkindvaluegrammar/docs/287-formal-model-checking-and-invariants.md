# Formal model checking as evidence (TLA+ lane)

DeriveBSD already treats **tests, fuzzing, and replay capsules** as first-class evidence.
The missing “greenfield advantage” is to also treat **design-level model checking** as a normal tool,
especially for the state machines that cross trust boundaries.

This doc proposes a light, practical lane:

- keep models **finite and tiny**
- model **authority + state transitions**, not implementation
- run model checking in CI and emit a `modelcheck.receipt`

## Why bake this in

The archive now contains multiple places where *one missing transition* can cause a bad day:

- update metadata expiry / rollback / witness cosigning
- boot environment “try then confirm” switching
- inbound/outbound network lease brokers
- sealed-secret unsealing policy evolution
- breakglass grants, expiry, and revocation

These are **concurrent / distributed / stateful** problems, and they are notoriously hard to test by execution alone.

TLA+ is a good fit because it is designed for describing systems at a level above code, and TLC can check
finite models for invariant violations and deadlocks.

## What the artifact should look like

### Inputs
- a model (TLA+ module, PlusCal, or other) referenced by digest
- a model configuration (constants, invariants, bounds)
- a declared “intent”: which ADR/RFC this model supports

### Output
Emit a receipt:

- `spec/modelcheck.receipt.schema.json`
- example: `spec/examples/modelcheck.receipt.json`

The receipt should record:
- tool + version
- the digests of inputs
- run parameters (bounds, constants)
- result summary (pass/fail, deadlock, invariants checked)
- a digest of any counterexample trace bundle and logs

### Where it plugs in
- ADRs that define a protocol/state machine should link to the model and to the latest passing receipt.
- Promotion gates *may* require a passing model check for high-risk protocols (optional, but easy in a greenfield).

## Starter model: boot environment switching

A tiny finite model is included:

- `docs/models/bootenv_switch.tla`
- `docs/models/bootenv_switch.cfg`

It is intentionally minimal: it exists to demonstrate the workflow and the evidence object,
not to fully specify loaders, ZFS, or health checking.

## Practical rules (so it doesn’t become theatre)

1. **One model per scary decision.** If there is no clear decision it supports, don’t add the model.
2. **Keep it finite.** If TLC can’t explore it, it won’t help us.
3. **Prefer invariants over prose.** “Must never happen” belongs in `INVARIANTS`.
4. **Treat counterexamples as bugs.** A failing model check should be triaged like a failing test.
5. **Tie models to receipts.** A model without a receipt is just a document.

## Open questions
- Do we standardize on TLA+/TLC only, or allow multiple checkers (e.g. Apalache) behind the same receipt contract?
- What is the minimal “model budget” (time/states) that still catches real mistakes in practice?
