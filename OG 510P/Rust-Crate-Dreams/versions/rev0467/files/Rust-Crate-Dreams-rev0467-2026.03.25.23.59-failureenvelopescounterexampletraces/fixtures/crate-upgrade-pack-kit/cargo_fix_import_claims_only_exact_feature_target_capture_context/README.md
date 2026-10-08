# Scenario: cargo fix import claims only exact feature/target capture context

A maintainer imports a `cargo fix` result that rewrote source files for the default package and target,
but the pack wants to talk about a broader workspace lane.

The import receipt should not stand alone.
It should point at an explicit `capture-context.receipt.json` describing:

- which package selection ran,
- which targets and features were active,
- which target triples were selected,
- the toolchain posture,
- the lockfile posture,
- and whether the result is directly replayable or only a copied summary.

This keeps “a fix was observed” separate from “the whole upgrade lane is covered”.
