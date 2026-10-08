# Cargo rebuild explanation lanes — 2026-03-16

## Main judgment

The archive now has enough Cargo build-performance substrate that future passes must stop flattening all “why was this build weird?” work into one fake crate.

The strongest near-buildable split is now:

1. **P-0469 Cargo Rebuild Explanation Kit** — one-run or two-run **support bundles** for a concrete rebuild mystery.
2. **P-0035 cargo-build-insights** — **historical session warehouse** and regression/trend adjudication across many runs.
3. **P-0490 Cargo Lock Contention Witness Kit** — **waiting / lock / collided-root** diagnosis.
4. **P-0494 Cargo Compile-Time-Deps Workflow Kit** — **tool-surface parity** and fallback-to-full-build diagnosis.
5. **P-0045 cargo-input-manifest** — **build input manifest / signature** truth for reproducibility and cache keys.

These lanes should import from one another, not collapse into one “Cargo build doctor”.

## Why this sharpened now

Several official signals line up:

- Cargo’s build-analysis goal says Cargo is recording build metadata across invocations and introducing `cargo report` commands for rebuild reasons and timings.
- Current unstable docs say `-Zbuild-analysis` writes JSONL logs to `$CARGO_HOME/log/`, gives each invocation a unique session id, and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.
- The Cargo 1.94 development-cycle update says `cargo report timings` kept gaining missing features, `cargo report rebuild` / `rebuilds` was added for rebuild diagnosis, and `cargo report sessions` exists to find the ids the other commands need.
- The relink-don’t-rebuild and build-dir-layout goals both make clear that “too much rebuilt” and “why reuse collapsed” are still active upstream pain, not solved history.

That means the missing crate is no longer “record builds somehow.”
The missing crates are the **boring coordination artifacts around support, history, contention, parity, and signatures**.

## What P-0469 should own

P-0469 should own:

- one concrete rebuild ticket or a tight baseline/head comparison,
- a small cause vocabulary,
- session import / freeze behavior,
- exactness receipts that distinguish imported wording from normalized facts and local inference,
- and one bundle that a maintainer can attach to CI, a bug report, or an internal support thread.

P-0469 should **not** own:

- long-term warehousing,
- generalized trend dashboards,
- lock-wait / blocked-process diagnosis,
- compile-time-deps / editor parity truth,
- or build-signature completeness.

## Anti-patterns to reject

### Anti-pattern 1: `cargo report` already solved the workflow

Cargo is building the recorder/query substrate.
That does **not** mean the stable support bundle, redaction policy, exactness ledger, or comparison workflow is already boring.

### Anti-pattern 2: waiting equals rebuilding

A build can wait on a collided root without any interesting rebuild-cause story.
A build can also rebuild heavily without visible blocking.
Those are adjacent but different artifacts.

### Anti-pattern 3: tool-only compile drift equals rebuild causality

When `cargo check`, rust-analyzer, or `--compile-time-deps` differs from a fuller build, the receiver needs a **tool-surface parity receipt** first.
That may explain a rebuild incident, but it is not the same contract as a rebuild-cause bundle.

### Anti-pattern 4: one session bundle equals historical analysis

One support-grade bundle should be tiny and reviewable.
A warehouse crate should import many sessions, preserve unknown fields, and answer “when did this start?”
Merging them creates a bloated MVP.

## Planning rule for future passes

When a future pass touches Cargo build weirdness, it must state explicitly whether the crate is primarily about:

1. **today’s rebuild mystery** (P-0469),
2. **many-run history / regression series** (P-0035),
3. **blocked roots / waiting** (P-0490),
4. **tool-surface divergence** (P-0494), or
5. **input completeness / signatures** (P-0045).

If the answer is “all of them”, the proposal is probably not honest enough yet.

## Sources

- Cargo build-analysis goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo unstable docs (`-Zbuild-analysis`, `cargo report`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- This development-cycle in Cargo 1.94: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Relink don’t Rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
