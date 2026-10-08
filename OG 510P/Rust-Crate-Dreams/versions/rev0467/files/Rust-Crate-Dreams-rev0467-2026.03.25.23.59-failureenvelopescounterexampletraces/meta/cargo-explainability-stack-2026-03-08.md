# Cargo explainability stack — incubation note (2026-03-08)

Purpose: stop treating the best Cargo-facing ideas as isolated proposals and instead describe a plausible **crate family** with a sane order of attack.

## The three strongest adjacent proposals

- **P-0468 Cargo Resolver Explanation Kit**
- **P-0469 Cargo Rebuild Explanation Kit**
- **P-0494 Cargo Compile-Time-Deps Workflow Kit**

These proposals are adjacent enough that future passes should check whether a claimed “new idea” is really just a missing layer or fixture family inside this stack.

## What each crate provides other people

### P-0468 Cargo Resolver Explanation Kit
Provides a **graph-choice artifact**:
- why a version was chosen,
- why a feature is active,
- why a crate was built more than once,
- and what changed across two resolved graphs.

Other people get:
- PR attachments,
- lockfile-drift explanations,
- feature-cause JSON for tool authors,
- and one portable `resolvewhybundle.zip` instead of screenshots of `cargo tree`.

### P-0469 Cargo Rebuild Explanation Kit
Provides a **run-delta artifact**:
- which units rebuilt,
- which were reused,
- which visible fingerprints changed,
- and whether lock contention, wrapper drift, target/profile drift, or tool-driven cache invalidation are implicated.

Other people get:
- one CI artifact for “why was this build slow?”
- one issue attachment for “why did rust-analyzer or cargo check poison reuse?”
- and one conservative JSON report that does not require reading raw Cargo trace logs.

### P-0494 Cargo Compile-Time-Deps Workflow Kit
Provides an **invocation-parity artifact**:
- what the tool-only build included,
- where it diverged from a normal build,
- what assumptions were pinned,
- and when the user should fall back to a full build.

Other people get:
- editor/build parity receipts,
- rust-analyzer-friendly diagnostics,
- and a support bundle that stops “works in the editor, fails in cargo build” from being pure folklore.

## Recommended incubation order

### First: P-0469
Why first:
- strongest concrete user story,
- clear current evidence of pain,
- easiest artifact to explain to non-experts,
- and best chance of producing valuable fixture goldens quickly.

### Second: P-0468
Why second rather than first:
- it is strategically enormous,
- but some of its receipt/redaction/manual-review vocabulary should be proven in P-0469 first,
- and resolver explanation gets easier to present once the archive already has a shared “why bundle” style.

### Third: P-0494
Why third:
- it depends on a sharper notion of what counts as parity drift,
- and its best artifact vocabulary can borrow from the first two.

## Shared contract vocabulary the stack should converge on

Across all three crates, keep these shared ideas aligned:

- `manual_review_required`
- `observed_fact`
- `conservative_inference`
- `assumption_lock`
- `redaction_policy`
- `command_receipt`
- `comparison_baseline`
- `bundle_schema_version`

If future passes rename these separately in each proposal, that is drift.

## 0.1 recommendation for P-0469

### User story
“After a `cargo check` or editor background build, a subsequent `cargo build` rebuilt far more than expected. Give me one bundle that explains the likely reason without requiring Cargo internals expertise.”

### Minimal artifact set
- `rebuild-context.toml`
- `unit-rebuilds.json`
- `rebuild.receipt.json`
- `notes.md`

Do **not** require deep fingerprint detail for first value. Make fingerprint deltas an optional overlay once the basic report is useful.

### First fixture corpus
1. `cargo build` then `cargo build` → mostly reused
2. `cargo check` then `cargo build` → suspicious rebuild drift
3. target/profile change → expected split
4. wrapper or `RUSTFLAGS` drift → explicit mismatch receipt
5. lock contention or shared target-dir hint → manual review / contention witness

## 0.1 recommendation for P-0468

### User story
“A manifest or workspace-selection change caused unexpected feature or duplicate-build behavior. Show the shortest cause chain I can review.”

### Minimal artifact set
- `resolve-why.lock`
- `feature-causes.json`
- `duplicate-builds.json`
- `resolver-choice.receipt.json`
- `notes.md`

### First fixture corpus
1. workspace feature forwarding
2. dev-dependency or target-specific feature split
3. duplicate same-version build caused by feature separation
4. lockfile-pinned version choice that surprises the user

## Anti-patterns for this stack

- Do not turn P-0469 into a historical warehouse; that is closer to `cargo-build-insights`.
- Do not turn P-0468 into a graph visualizer product.
- Do not make P-0494 pretend tool-only builds are a stable user guarantee when Cargo explicitly says the feature is permanently unstable.
- Do not silently collapse observed facts and reconstructed explanations.

## Repo implication

For the next few passes, the archive should prefer:
- fixture/schema stubs,
- explicit adoption stories,
- and small shared receipt vocabularies,

rather than adding more top-level proposal count.
