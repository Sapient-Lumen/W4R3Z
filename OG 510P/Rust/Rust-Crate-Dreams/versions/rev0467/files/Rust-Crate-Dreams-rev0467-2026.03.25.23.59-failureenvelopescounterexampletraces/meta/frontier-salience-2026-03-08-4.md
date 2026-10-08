# Frontier salience scan — 2026-03-08 (fourth pass)

This pass deliberately does **not** add another protocol or foreign-package proposal.

The archive is now broad enough that the better move is often to turn one of the top-ranked ideas into something closer to a real crate plan: schemas, fixtures, layering decisions, and a clearer answer to the blunt question:

> what will this crate provide other people that they can actually inspect, diff, and rely on?

## External signals worth honoring right now

- The 2025 State of Rust survey still points to **resource usage / compile times** as a recurring productivity problem. That keeps Cargo explainability high on the frontier.
- The Rust project is still explicitly investing in **Cargo plumbing** and **build-dir/layout** work, which means more substrate exists, but ordinary teams still lack boring review artifacts above that substrate.
- Cargo now exposes a permanently unstable `--compile-time-deps` mode intended for tools like rust-analyzer, which makes the `build` / `check` / tool-only boundary more explicit.
- Recent real-world reports still describe `cargo check` / rust-analyzer interactions that trigger unnecessary rebuilds, so the “why did this rebuild?” pain is not hypothetical or purely historical.
- The Rust project is also publicly asking for more data on debugging pain in 2026, which keeps support/debug receipts near the top even when they are not the narrowest next crate to incubate.

## What currently looks most worthy

The top of the archive is now best understood as a **Cargo explainability stack** rather than a pile of separate ideas.

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Best next incubation target because the user pain is concrete, the fixture stories are clear, and the output artifact can be obviously useful in CI and editor/build debugging.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Still arguably the most strategic Cargo-facing idea because feature and version choices remain under-explained, but it benefits from sharing receipt vocabulary with P-0469 instead of incubating in total isolation.
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Important because Cargo now admits a tool-only compile surface, but teams still lack a parity/fallback bundle explaining when tool workflows diverge from normal builds.
4. **P-0496 Cargo Vendor & Source Parity Kit**
   - Remains strong because offline / vendor / source-replacement workflows still need honest source-origin receipts.
5. **P-0492 Cargo Registry Auth Doctor Kit**
   - Strong because Cargo auth/provider flows remain operationally sharp and frustrating.
6. **P-0084 Debuggability Support Contract Kit**
   - Still highly worthy, especially with the 2026 debugging survey signal, but it is slightly less attractive as the *next* repo move because Cargo explainability now has a cleaner shared stack to deepen.

## Why P-0469 rose to the top for an incubation-minded pass

P-0468 and P-0469 are close in abstract value, but this pass gives P-0469 the edge for practical reasons:

- there is a long-standing Cargo issue explicitly asking for better rebuild diagnostics,
- there are recent real-world reports of `cargo check` causing full rebuilds,
- the build-dir-layout work names lock contention and Cargo/Rust-Analyzer interference as active pain,
- and the resulting artifact is easy to explain to other people: “here is the bundle that tells you why this rebuilt.”

That gives P-0469 unusually strong **fixtureability** and **adoption clarity** for a 0.1.

## Stack view: how the three Cargo explainability proposals fit together

### Layer 0 — substrate
- Cargo plumbing outputs
- `cargo tree`
- timing reports
- fingerprint/debug logs
- `--compile-time-deps`

### Layer 1 — graph explanation
- **P-0468 Cargo Resolver Explanation Kit**
- answers: why this version, why this feature, why duplicate builds

### Layer 2 — run explanation
- **P-0469 Cargo Rebuild Explanation Kit**
- answers: why this unit rebuilt, why reuse failed, what changed between runs

### Layer 3 — invocation-parity explanation
- **P-0494 Cargo Compile-Time-Deps Workflow Kit**
- answers: how tool-only builds differ from normal builds, and when fallback is needed

The important judgment is that these are **not three unrelated crates**. They should share terminology, redaction posture, receipt conventions, and “manual review required” vocabulary.

## Working rule for future revisions

For the next few passes, prefer one of these moves over adding more proposal count:

1. add fixture/schema stubs to the top Cargo explainability proposals,
2. write explicit layering/incubation notes,
3. tighten roadmap language around which one should ship first,
4. or merge vocabularies where two proposals are rediscovering the same receipt concept.

Only add another proposal if it clearly outranks sharpening this stack.
