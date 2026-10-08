# Epic crate rubric — 2026-03-22

This note exists to keep broad frontier scans from turning into an unranked pile of “cool Rust ideas”.
A worthy crate contribution should solve a **real receiver-facing problem** and should do so in a way that another team can adopt, review, and maintain.

## Main judgment

The strongest missing crates in the current Rust ecosystem are usually **not** brand-new substrate layers.
They are the missing **middle layers** that turn existing substrate into a boring, reviewable contract for other people.

That usually means the best candidate crate is one of these:

- a **contract kit**,
- an **evidence / receipt kit**,
- a **doctor + summary + diff** workflow,
- a **conformance / replay / portability** kit,
- or a **support-surface** crate that makes “what this project really supports” explicit.

The archive should therefore reward crates that do at least four things well:

1. **Name the recurring pain honestly.**
2. **Exploit existing substrate instead of re-implementing it.**
3. **Export stable artifacts another team can review.**
4. **Stay narrow enough to ship a credible `0.1`.**

## Scoring dimensions for frontier ranking

### 1. Salience
How often does the pain show up in fresh official or ecosystem signals?
Recent signals still point at debugging, resource usage / compile-time drag, cross-compilation / support posture, async lock-in, safety-critical evidence, and cross-language interop.

### 2. Leverage
Does the crate help many other crates and teams, or only one narrow niche?
The archive should favor crates that improve adoption, reviewability, supportability, and operational clarity for many downstream users.

### 3. Middle-layer fit
Is the missing value really the layer **above** today’s substrate?
If the ecosystem already has runtimes, parsers, code generators, queue crates, or protocol bindings, the worthy crate is often the support / contract / diff / evidence layer above them.

### 4. Artifact quality
Can the crate emit something that another team can actually use?
Strong candidates usually produce at least one of:

- `*.receipt.json`
- `*.report.json`
- `*.manifest.json`
- `*.diff.json`
- concise Markdown summaries
- portable review bundles

### 5. Adoption path
Could a maintainer plausibly add this to CI, release review, support handoff, or docs in a week?
If adoption requires a giant platform rewrite, the frontier may be too ambitious for a crate-first move.

### 6. Boundary sharpness
Can the crate explain what it is **not**?
The strongest ideas keep adjacent lanes separate instead of collapsing support, trust, compatibility, docs posture, runtime behavior, and assurance into one fake green bit.

### 7. Sustainability
Does the design avoid becoming a hosted portal, a giant dashboard, or a permanent bespoke rules engine?
Crates with small stable vocabularies, receipts, and import adapters are easier to keep alive.

## What an epic crate should provide other people

A crate earns the word *epic* when it gives other people something they did not previously have a boring way to get.
In practice that means at least five deliverables:

1. **One compact answer** to an otherwise scattered question.
2. **One explicit vocabulary** that others can reuse.
3. **One evidence path** that separates observation from declaration.
4. **One diff path** that makes drift visible over time.
5. **One adoption story** that works in local dev, CI, release review, or downstream integration.

The archive should distrust candidate crates that only provide:

- a thin wrapper over one existing library,
- a score without an assumption ledger,
- a dashboard without receipts,
- a protocol binding without conformance / portability truth,
- or a giant abstraction that hides which runtime / toolchain / backend / transport actually matters.

## Current families of especially worthy crates

### A. Support-contract crates
Examples: toolchain/target support, MSRV support, public API readiness, debuggability support, service readiness.
These are strong because they turn day-to-day support folklore into reviewable artifacts.

### B. Interop and conformance crates
Examples: FFI boundary conformance, OpenAPI/JSON Schema toolchain contracts, plugin host compatibility, protocol conformance kits.
These are strong when real substrate exists but teams still cannot compare or verify behavior cleanly.

### C. Assurance and evidence crates
Examples: async runtime assurance, verification campaigns, assurance-case workbenches, evidence bundles, trust lenses.
These matter because safety, trust, and regulated adoption increasingly require portable evidence, not just claims.

### D. Productivity-surface crates
Examples: cargo-build-insights, diagnosis support, crash/symbolication workbenches, debugger support, text-input/product-engineering infrastructure.
These matter because the official 2025 survey and March 2026 challenges work still point at debugging, compile friction, resource costs, and support gaps.

## Anti-patterns

Do **not** promote a candidate just because it sounds modern or broad.
The archive should be skeptical of:

- “one crate to unify all async runtimes”
- “one universal data abstraction” without loss accounting
- “one score” for trust, health, maintenance, or compatibility
- “one dashboard” that hides provenance
- “one plugin system” that avoids lifecycle or capability truth
- “one build tool” that silently absorbs docs, MSRV, linker, and CI semantics into one guessed answer

## Practical ranking rule for future passes

When doing a broad scan, prefer this sequence:

1. re-read the latest entry,
2. read the latest frontier-salience note,
3. read this rubric,
4. check whether the candidate is already represented by an adjacent proposal,
5. only then decide whether to deepen, merge, split, or add a lane.

Broad scans should usually end in one of three outcomes:

- **deepen an existing high-salience lane**,
- **re-rank the frontier without adding a new proposal**,
- or **add one carefully scoped new lane with explicit artifacts and boundaries**.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
