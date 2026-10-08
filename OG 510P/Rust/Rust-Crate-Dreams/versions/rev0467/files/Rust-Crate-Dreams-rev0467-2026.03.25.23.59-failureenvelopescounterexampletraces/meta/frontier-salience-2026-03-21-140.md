# Frontier salience snapshot — 2026-03-21-140

This pass did **not** open another generic async helper, another shutdown wrapper, or another runtime implementation.
It added **P-0532 Async Runtime Assurance Profile Kit**.

## Why this frontier moved up

The current official Rust writing now exposes the gap directly:

- the March 2026 Rust challenges post says async remains painful and that runtime lock-in is still a distinctive ecosystem problem;
- the January 2026 safety-critical post says async is attractive for middleware/event-driven systems, but the runtime and qualification story is not settled at higher integrity levels;
- that same post explicitly recommends defining requirements for a **safety-case friendly async runtime**;
- and the 2026 project flagships keep safety-critical evidence on the main agenda while the async roadmap keeps focusing on language blockers rather than on runtime support contracts.

At the same time, Tokio, Embassy, and RTIC already expose materially different assumptions around shutdown, allocation, timers, scheduling, priority, and evidence posture.
That means the sharper missing crate is not another runtime.
It is a **runtime-choice contract** above today's runtimes.

## Main conclusion

Promote **P-0532** high immediately, but keep it narrow.
The next worthy move is not a universal runtime abstraction and not a benchmark bakeoff.

It should stay focused on:

1. freezing the actual **runtime profile** in use,
2. making **shutdown behavior** explicit,
3. publishing **qualification basis** rather than hand-waving “suitable” or “embedded-ready”,
4. keeping hosted, embedded, and interrupt-priority runtime models visibly distinct,
5. and letting teams diff runtime-support posture across releases.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — strengthened because official Rust sources now identify both async lock-in and unresolved runtime qualification as live ecosystem problems.
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still strong because stop barriers and timeout aftermath remain adjacent runtime-selection pain.
3. **P-0529 Channel Surface Contract Kit** — still strong because channel semantics remain one of the runtime-shaped hidden contracts teams absorb.
4. **P-0521 Crate Resource Surface Pack Kit** — still strong because runtime choice often changes actual budget topology and clone-sharing posture.
5. **P-0484 Toolchain & Target Support Contract Kit** — still strong because runtime claims only matter in the context of real target/support posture.

## Keep these boundaries sharp

- **P-0532** is runtime family + allocation posture + shutdown behavior + qualification basis.
- **P-0520** is lifecycle / barrier / timeout aftermath.
- **P-0529** is channels and delivery semantics.
- **P-0521** is resource topology.
- **P-0484** is toolchain/target support.

Do not let “async ecosystem support” flatten those lanes into one fake crate.
