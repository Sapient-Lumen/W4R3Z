# Frontier salience scan — 2026-03-08 (tenth pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it made **P-0468 Cargo Resolver Explanation Kit** more implementation-ready.
The current Cargo/docs ecosystem now makes the missing layer sharper:
Cargo already has resolver docs, troubleshooting commands, stable graph context, unstable feature-resolution-adjacent substrate, and real third-party graph tooling.
What is still missing is the **portable explanation receipt**.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Still the best immediate incubation target because the user story is the most universal and the receiver-facing artifact is the easiest to explain in one support incident.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Rose in buildability, even if not above P-0469 in urgency. The boundary to existing Cargo and ecosystem tooling is much clearer now.
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Still the strongest tool/workflow parity layer and now sits more cleanly beside P-0468.
4. **P-0046 buildscript-ux-kit**
5. **P-0486 Debuggability Support Contract Kit**
6. **P-0035 cargo-build-insights**
7. **P-0490 Cargo Lock Contention Witness Kit**
8. **P-0059 buildscript-testkit**
9. **P-0058 native-deps-kit**
10. **P-0489 Cargo Build-Dir Consumer Transition Kit**

## Why P-0468 improved

Five current facts matter here:

- the resolver docs now include concrete troubleshooting guidance, not just abstract rules,
- `cargo tree` already exposes a practical feature/duplicate investigation workflow,
- `cargo metadata` remains stable context but still excludes feature resolution in the plumbing framing,
- `--unit-graph` gives a plausible richer import path,
- and `guppy` / `hakari` prove graph and feature-set reasoning is feasible without yet solving the receiver-facing support artifact.

That means **P-0468** no longer needs to pretend it is inventing graph introspection.
It can instead be precise about its contract:

- one feature-cause report,
- one version-choice receipt,
- one duplicate-build grouping,
- one graph-diff report,
- and one receipt that says where every claim came from.

## What should happen next

The best next passes on this frontier should prefer:

1. fixture/schema stubs for **P-0468**,
2. vocabulary alignment across **P-0468 / P-0469 / P-0035**,
3. conservative version-choice taxonomies,
4. and freshness checks as Cargo plumbing evolves.

They should **not** add another generic Cargo graph/feature idea unless it is clearly distinct from:

- resolver explanation,
- rebuild explanation,
- historical build warehousing,
- tool-workflow parity,
- or lock contention.

## Sources

- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo unstable features: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- `guppy`: https://docs.rs/guppy/latest/guppy/
- `cargo hakari`: https://docs.rs/cargo-hakari/latest/cargo_hakari/
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
