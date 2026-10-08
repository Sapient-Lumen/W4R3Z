# Epic crate contribution bar — 2026-03-23

This note answers a repo-level question:

> What should count as a worthy, maybe even epic, crate contribution to the Rust ecosystem?

## Main judgment

A crate is worth serious promotion in this archive when it gives **other people** a durable new workflow or durable new evidence surface.

The strongest candidates usually provide at least one of these:

- a **decision pack**,
- a **support / capability contract**,
- a **migration or transition receipt**,
- a **diffable evidence bundle**,
- a **machine-usable knowledge pack**,
- a **portable conformance / interop report**,
- or a **small stable substrate** that many other tools can build on.

The weakest candidates usually provide only one of these:

- one thin wrapper around an existing crate,
- one parser/adapter with little workflow consequence,
- one score/ranking view with no review artifact,
- one “assistant shell” with hand-wavy claims,
- or one narrow domain integration whose real missing seam is still horizontal.

## The seven-part bar

### 1. Receiver-facing value
The crate must help somebody **other than the original author** make a decision, finish a review, debug a failure, certify a boundary, or hand off a workflow.

Good signs:
- another maintainer can inspect the output later,
- another team can consume it without reproducing the whole context,
- another tool can import part of the output.

### 2. Portable artifact seam
A strong crate exports something boring and checkable:
- `*.receipt.json`
- `*.report.json`
- `*.manifest.json`
- `*.bundle.zip`
- `*.diff.json`
- or another explicit schema-bound artifact.

If the crate cannot say what durable artifact it emits, it is usually still too vague.

### 3. Honest claim ceiling
A strong crate names what it **does not** prove.
For example:
- “local preflight” is not “hosted parity”,
- “symbols present” is not “usable interactive debugging”,
- “green lockfile today” is not “safe under re-resolution tomorrow”,
- “candidate ranked first” is not “all alternatives disproven forever”.

A crate becomes more epic, not less, when it has explicit refusal zones.

### 4. Leverage across many real Rust worlds
The best crates cut repeated cost across very different user groups:
- backend/async teams,
- CLI and desktop authors,
- embedded and `no_std` work,
- safety-critical and regulated adopters,
- Wasm/plugin ecosystems,
- kernel / low-level systems work,
- data / GPU / scientific stacks,
- and toolchain / build / CI maintainers.

### 5. Imported substrate instead of empire-building
A worthy crate reuses official or de facto substrate where possible:
- Cargo metadata and external-tools JSON,
- docs.rs metadata / rustdoc JSON / build summaries,
- crates.io security and publication metadata,
- rustdoc / rustc / rustup / target documentation,
- standard format outputs from debuggers, test harnesses, or verifiers.

It should usually **not** replace the upstream system wholesale.

### 6. Lovable `0.1` shape
The crate should have a believable first version with:
- a tight command/library surface,
- a small stable artifact vocabulary,
- 3–8 proving-ground fixtures,
- a path to boring maintenance,
- and a clear “what waits until later” section.

### 7. Diff and review friendliness
The best crates help compare **before vs after**.
Rust teams live in migration, release, upgrade, and incident workflows.
A crate that cannot participate in diffs, review, or handoff will usually have a smaller ecosystem effect.

## What a serious proposed crate should provide other people

When drafting or refining a proposal in this archive, answer these explicitly:

1. What exact artifact does it emit?
2. Who reads that artifact?
3. What repeated decision or failure does it shorten?
4. What stronger substrate does it import?
5. What claims does it refuse to make?
6. What are the proving grounds for `0.1`?
7. What later expansion should be postponed?

## Anti-patterns

A proposal should be demoted unless it escapes these traps:

### “Wrapper without witness”
The crate mainly wraps existing APIs but exports no new reviewable artifact.

### “Scoreboard without decision receipts”
The crate ranks things but gives no candidate basis, elimination basis, or re-entry rule.

### “Magic assistant shell”
The crate promises better guidance/search/chat without a durable, source-grounded knowledge or decision model.

### “One niche when a horizontal seam is still missing”
A narrow domain crate is proposed even though the real missing layer is still docs/debug/target/dependency/interop/knowledge/support truth.

### “Pretend support contract”
The crate collapses different lanes into one fake green check.

## Fast scorecard

Use this quick screen before promoting a proposal:

- Receiver-facing value: 0–5
- Portable artifact seam: 0–5
- Honest claim ceiling: 0–5
- Cross-domain leverage: 0–5
- Imported-substrate fit: 0–5
- Lovable `0.1`: 0–5
- Diff/review friendliness: 0–5

### Reading the score
- **30+**: likely worth active repo deepening
- **24–29**: promising, but sharpen artifacts or boundaries first
- **18–23**: likely interesting but not yet epic
- **below 18**: probably a narrow helper, experiment, or downstream plugin rather than a headline ecosystem contribution

## Default archive rule

When in doubt, prefer proposals that export a **portable answer** over proposals that export only another API surface.
