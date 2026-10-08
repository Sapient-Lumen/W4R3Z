# Frontier salience — 2026-03-22 (183)

This pass did **not** open another async helper, benchmark harness, or runtime abstraction lane.
It deepened **P-0532 Async Runtime Assurance Profile Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0011 Crate Health Contract Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0532 Async Runtime Assurance Profile Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0469 Cargo Rebuild Explanation Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0431 Public Dependency Boundary Kit**

## Why P-0532 was the right lane to deepen now

Fresh official Rust and runtime docs make the missing value here more specific than “better async docs” or “another runtime comparison chart”:

- the March 2026 Rust challenges post says async remains painful and that runtime lock-in is still a real ecosystem problem;
- the January 2026 safety-critical post explicitly asks for requirements for a safety-case-friendly async runtime;
- the 2026 flagships keep async progress on the language agenda, which improves substrate but still does not publish a runtime-support contract for downstream users;
- Tokio’s runtime and `spawn_blocking` docs now make shutdown aftermath, blocking-task non-abortability, and resource invalidation after drop explicit enough to classify;
- `tokio-metrics` and `RuntimeMetrics` make runtime/task instrumentation concrete enough that evidence classes can stay honest;
- Embassy now documents no-`alloc`, static tasks, linker-detected RAM fit, fairness, timer queues, and optional multi-priority executors explicitly;
- and RTIC keeps single-shared-stack execution, compile-time deadlock-freedom, generated async executors, and timer-queue semantics concrete enough that it should stop being flattened into a generic executor label.

That combination makes the missing crate less “another runtime wrapper” and more a **reviewable runtime-choice and runtime-evidence contract**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. **qualification-basis truth**,
2. **runtime-profile drift truth**,
3. **portable runtime-assurance bundles**,
4. **host/target runtime-lane separation**, and
5. **manual-review honesty where runtime claims outrun evidence**.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0532**, **P-0520**, **P-0521**, **P-0484**, and **P-0503**.

Especially resist:

- another async tutorial or cookbook crate,
- another benchmark suite pretending performance equals runtime assurance,
- another runtime-neutral abstraction layer that cannot export reviewable receipts,
- or another dashboard that cannot say why a runtime claim is actually believed.
