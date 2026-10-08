# Frontier salience — 2026-03-22 (181)

This pass did **not** open another unsafe-verification lane.
It deepened **P-0120 Unsafe Contract Auditor Kit** instead.

## Current top frontier

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

## Why P-0120 was the right lane to deepen now

Fresh official Rust work makes the missing value here unusually concrete:

- the 2026 flagships page explicitly names **normative unsafe documentation** as part of Safety-Critical Rust;
- the std-contracts goal keeps pushing toward machine-readable safety contracts and runtime-check-capable contract attributes;
- the unsafe-fields goal makes it clearer that important safety invariants often live beyond the visible surface of `unsafe` blocks;
- Miri remains excellent substrate but is explicit that it cannot be treated as the full definition of Rust UB or as a universal proof engine.

That combination makes the missing crate less “another unsafe checker” and more a **reviewable unsafe obligation/evidence contract**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. **authority-import truth**,
2. **unsafe-obligation drift truth**,
3. **witness-comparison honesty**,
4. **callback/FFI boundary receipts**,
5. and **portable diffable unsafe-audit bundles**.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0120**, **P-0485**, **P-0121**, **P-0434**, and **P-0460**.

Especially resist:

- another “Miri wrapper” crate,
- another generic unsafe scorecard,
- another proof-dashboard bundle,
- or another FFI checklist that does not actually export reviewable unsafe receipts.
