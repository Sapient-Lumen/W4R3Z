# Decisions — rev0169

## D169-01 — make close-time SQLite cleanup non-blocking

**Decision.** Replace truncating WAL checkpoint cleanup at close with a short passive checkpoint attempt.

**Why.** Teardown should not be able to turn an already-complete checkpoint test into an ambiguous hang. SQLite recovery is a better boundary than forcing WAL truncation during every close.

## D169-02 — document bounded acceptance as the recipient path

**Decision.** Add `tools/run_acceptance.py` and make it the command a recipient should run first.

**Why.** Per-module subprocesses give clearer failure localization and wall-clock control than monolithic discovery while still exercising the same unittest modules.

## D169-03 — refuse unedited generated scenario templates

**Decision.** Generated player-input and model-policy placeholder values are validation errors for scenario capsules.

**Why.** An experiment harness should fail closed before producing plausible-looking artifacts from placeholder text.

## D169-04 — add MIT license

**Decision.** Ship a top-level MIT `LICENSE` and project metadata pointing to it.

**Why.** The artifact is intended as a gift and research substrate; reuse and patching rights should be explicit.

## D169-05 — keep the scientific claim modest

**Decision.** Rev0169 improves sendability and falsifiability; it does not claim empirical evidence that retcon planning improves fiction.

**Why.** Trust depends on separating package custody from experimental results.
