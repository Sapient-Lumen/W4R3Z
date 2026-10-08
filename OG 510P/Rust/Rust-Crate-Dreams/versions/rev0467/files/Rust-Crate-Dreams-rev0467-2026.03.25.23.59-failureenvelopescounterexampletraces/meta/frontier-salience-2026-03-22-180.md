# Frontier salience scan — 2026-03-22 (dependency lifecycle implementation readiness)

This pass did **not** add another proposal.
It deepened one of the strongest existing cross-sector lanes until it looked more like a real crate someone could start building.

## Ranked frontier after this pass

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0535 Dependency Lifecycle Transition Kit**
3. **P-0011 Crate Health Contract Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0532 Async Runtime Assurance Profile Kit**
8. **P-0469 Cargo Rebuild Explanation Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0431 Public Dependency Boundary Kit**

## Why P-0535 moved up

Fresh official signals make the lane sharper rather than fuzzier:

- the safety-critical write-up explicitly describes rising-criticality workflows where teams contain, constrain, or replace crates as assurance demands increase;
- the Rust challenges write-up says the remaining ecosystem pain is often domain-specific, which favors local architectural transition contracts over generic crate folklore;
- crates.io now exposes stronger trust context (Security-tab visibility, Trusted Publishing Only Mode, SLOC, `pubtime`), but that still does not tell a reviewer where a dependency may live inside one system;
- Cargo’s docs now give a clearer source-story split among `[patch]`, restricted path overrides, exact-source replacement, and read-only vendoring.

That combination makes **P-0535** more than “another supply-chain idea.”
It is a **local architecture transition contract** above the graph and above imported trust facts.

## Product lesson from this pass

The lane became more buildable when three artifacts became first-class:

- `transition-plan.manifest.json`
- `dependency-exception.ledger.json`
- `imported-signal.receipt.json`

Those are the missing review objects between “we know our graph” and “we have an honest lifecycle story.”

## Guardrail

Do not add:

- another dependency score,
- another vulnerability dashboard,
- another generic vendor/offline parity tool,
- or another successor/replacement helper

unless it clearly escapes the present ownership of **P-0535**, **P-0011**, **P-0496**, **P-0515**, and **P-0017**.

## Sources

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- https://doc.rust-lang.org/cargo/reference/source-replacement.html
- https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- https://rustfoundation.org/strategic-plan/
