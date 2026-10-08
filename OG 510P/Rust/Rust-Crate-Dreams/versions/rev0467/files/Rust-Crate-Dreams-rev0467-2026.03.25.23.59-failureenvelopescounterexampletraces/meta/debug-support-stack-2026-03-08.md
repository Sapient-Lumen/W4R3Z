# Debug support stack — incubation note (2026-03-08)

This note sharpens three adjacent proposals into one more buildable stack:

- **P-0486 Debuggability Support Contract Kit**
- **P-0493 Source Path Hygiene & Debug Source Kit**
- **P-0491 Debugger Visualizer Compatibility Kit**

## Main judgment

The next strong non-Cargo frontier in this archive is **debug support**, not because Rust lacks debuggers in the abstract, but because maintainers still lack a **boring contract** for what a build actually supports.

Recent evidence makes that judgment easier to defend than it was even a few months ago:

- the 2025 State of Rust survey still leaves **debugging** among the most important productivity problems,
- the new 2026 debugging survey asks explicitly about cross-debugger support, visualizers, async debugging, and expression evaluation,
- Cargo and rustc already expose real substrate for `debug`, `split-debuginfo`, `strip`, and path-remapping behavior,
- Rust already has stable `#[debugger_visualizer]` support,
- and rustup already has explicit component vocabulary for `rust-src` / `rustc-dev`.

That means the archive should increasingly think in terms of **support receipts**, **source-lookup receipts**, and **visualizer compatibility receipts** rather than a vague “debugger tooling” bucket.

## Why this is a real crate frontier

The missing value is not another debugger.

The missing value is a family of crates that answer maintainers’ boring but consequential questions:

- what debugging posture did this build actually ship,
- where are the sidecars and symbol artifacts,
- can downstream users step into workspace/std/compiler sources,
- which debugger backends are supported by embedded visualizer assets,
- and what changed between two releases or profiles.

Those are review, support, CI, and release-handoff questions more than they are language-implementation questions.

## Stack members

### P-0486 Debuggability Support Contract Kit

This is the **center of gravity** for the stack.

It should provide the first stable vocabulary for:

- `interactive_debugger`,
- `backtrace_only`,
- `crash_symbolication_only`,
- `manual_review_required`.

Its first job is not to prove every debugger scenario. Its first job is to emit one honest bundle:

- `debuggability.receipt.json`,
- `symbol-layout.manifest.json`,
- `support-posture.report.json`,
- `debuggability-drift.diff.json`.

This is the proposal most likely to help other people immediately because it gives release engineers and support teams a compact answer to “what kind of debugging is this build actually good for?”

### P-0493 Source Path Hygiene & Debug Source Kit

This should be the **second** incubation target.

It is narrower than P-0486 and should remain that way.

Its job is to explain:

- remapped versus unremapped source paths,
- virtual `/rustc/<hash>/...` and `/rustc-dev/<hash>/...` source paths,
- whether `rust-src` or `rustc-dev` is needed,
- and whether privacy-oriented path hygiene degraded interactive source lookup.

This proposal becomes much easier once P-0486 already established the broader support-posture vocabulary.

### P-0491 Debugger Visualizer Compatibility Kit

This should be the **third** incubation target.

It is even narrower: embedded NatVis/GDB visualizer assets and their backend compatibility matrix.

Its first job is not to become a universal debugger automation layer. Its first job is to emit one honest matrix describing:

- which assets exist,
- which debugger families they target,
- whether they rendered correctly in a small fixture/golden set,
- and whether a regression came from the visualizer asset or from the broader debug-symbol/source posture.

## Recommended incubation order

### First: P-0486

Why first:

- it has the clearest direct maintainer value,
- it produces a bundle that CI/release/support teams can consume immediately,
- and its vocabulary should be reusable by P-0493 and P-0491.

### Second: P-0493

Why second:

- source-path hygiene is a sharp real seam,
- but its support consequences are easier to explain once P-0486 already defines the broad posture vocabulary,
- and its schemas can import or reference the same release/support receipt style.

### Third: P-0491

Why third:

- visualizer compatibility is valuable, but narrower,
- and it benefits from being able to say “the asset failed” versus “the build was never truly interactive-debugger-friendly” using P-0486-style evidence.

## What the first crate should provide other people

If the archive were forced to ship only one debugging-adjacent crate next, it should probably be **P-0486**.

That crate should provide other people:

1. **A stable support-posture vocabulary** instead of guessed debuginfo policy.
2. **A symbol-layout manifest** that says where sidecars actually are.
3. **A release-review diff artifact** for catching silent debugger regressions.
4. **A support bundle** that can travel with a bug report or release candidate.
5. **A narrow “doctor” surface** for mismatches like missing sidecars or an obviously stripped build claiming interactive-debugger support.

That is a strong 0.1 because it is immediately legible to downstream users.

## Suggested 0.1 boundaries

### P-0486 0.1

- inspect one built artifact set,
- capture debug level / split / strip facts,
- detect likely sidecars,
- classify one support posture conservatively,
- export a receipt and diff format.

### P-0493 0.1

- capture remap/trim-path posture,
- record virtual source-path prefixes,
- classify likely `rust-src` / `rustc-dev` requirements,
- export one source-availability report.

### P-0491 0.1

- discover embedded visualizer assets,
- emit a backend-target manifest,
- store normalized fixture render goldens,
- export a compatibility receipt without pretending all debuggers can be batch-driven equally.

## Archive lesson

This stack is a good example of the archive’s maturity rule:

When the substrate is already real, the next worthwhile crate is often a **support/review contract** above it.

Rust already has lots of debugging substrate. What it still often lacks is the **boring artifact that tells another human what the build actually promises**.

## Sources

- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo profiles (`debug`, `split-debuginfo`, `strip`): https://doc.rust-lang.org/cargo/reference/profiles.html
- Rust reference: `#[debugger_visualizer]`: https://doc.rust-lang.org/reference/attributes/debugger.html
- `rustc` remap-source-paths: https://doc.rust-lang.org/rustc/remap-source-paths.html
- rustup components: https://rust-lang.github.io/rustup/concepts/components.html
- Release note anchor for compiler-source path un-remapping: https://doc.rust-lang.org/beta/releases.html
