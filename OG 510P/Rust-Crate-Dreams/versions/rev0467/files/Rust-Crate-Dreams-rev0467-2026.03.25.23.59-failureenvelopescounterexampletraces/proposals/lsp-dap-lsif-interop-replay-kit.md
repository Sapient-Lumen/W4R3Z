---
id: P-0356
title: LSP 3.17 + DAP + LSIF Interop & Replay Kit — capability locks, transcript replay, and editor/debugger evidence bundles
status: idea
domains: [developer-tools, editors, protocols, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
  - https://microsoft.github.io/debug-adapter-protocol/specification.html
  - https://microsoft.github.io/language-server-protocol/overviews/lsif/overview/
  - https://docs.rs/tower-lsp
  - https://crates.io/crates/dap
  - https://crates.io/crates/ls-types
---

# Problem

Rust already has good protocol types and server frameworks for language tooling, but real interoperability failures still happen at the seam between:

- advertised versus actual **LSP capabilities**,
- editor/client behavior and fallback assumptions,
- debugger launch/configuration expectations in **DAP**,
- offline navigation/index assumptions in **LSIF**,
- and transcripts that are too noisy, incomplete, or editor-specific to replay reliably in CI.

An implementation can compile, pass ad hoc editor testing, and still break on notebook documents, inlay hints, partial result streaming, monikers, launch configurations, or cancellation behavior. The missing Rust contribution is a **capability-pinned interop and replay kit** for language tools, not yet another raw protocol crate.

# What it provides

- `tooling-ir` — canonical Rust IR for LSP capabilities, DAP launch/attach/session summaries, and LSIF feature surfaces.
- `cap-lock` — lockfiles pinning supported protocol versions, capability subsets, client quirks, and expected fallbacks.
- `transcript-normalizer` — stable import of LSP / DAP transcripts into replayable event sequences.
- `interop-check` — checks for capability drift, unsupported requests, negotiation mismatches, and index/runtime inconsistencies.
- `tooling-diff` — semantic diffs such as “advertises semantic tokens, fails range requests”, “DAP launch config drift”, or “LSIF moniker mismatch versus live LSP”.
- `cargo tooling-evidence` — emit `*.lspbundle.zip` for CI, editor-extension bugs, or debugger integration handoff.

# What the crate should provide other people

1. **A boring default artifact for editor/debugger interoperability bugs**.
2. **Pinned capability expectations** for language servers, adapters, and test clients.
3. **Replayable transcripts** that survive transport noise and editor-specific details.
4. **A bridge between live protocol behavior and offline LSIF expectations**.
5. **Semantic diffs across protocol/library upgrades** instead of one-off manual editor testing.

# Persona / who it’s for

- Language-server authors
- Debug-adapter authors
- Rust IDE / editor integration teams
- Tooling QA maintainers
- Compiler and language-tool authors shipping editor support

# Users & user stories

- **Language-server maintainer**: “Show me which advertised capability regressed after a dependency upgrade.”
- **Editor integration engineer**: “Capture a failing session once and replay it in CI without the whole editor.”
- **Debugger author**: “Diff launch/config/session behavior between two adapter versions.”
- **Code-navigation team**: “Compare LSIF expectations with live LSP results for symbol navigation.”

# Prior art (and why it’s insufficient)

- Microsoft maintains the **LSP**, **DAP**, and LSIF specification surfaces.
- Rust has strong substrate in `tower-lsp`, `lsp-types` / `ls-types`, and `dap`.
- But there is still no boring-default Rust crate family for **capability lockfiles + transcript replay + cross-surface semantic diffs + portable evidence bundles**.

# Design goals

1. **Protocol-subset aware** — most tools implement only part of the standards, and that must be explicit.
2. **Replay-first** — sessions should be reproducible without a full editor UI.
3. **Cross-surface aware** — link live LSP, debug behavior, and LSIF where useful.
4. **Transport-neutral** — normalize stdio, pipes, sockets, and editor-specific wrappers.
5. **CI-friendly** — outputs should be deterministic and diffable.

# MVP surface

- Minimal types: `CapabilityLock`, `SessionTrace`, `ToolingProfile`, `ToolingReport`, `ToolingDiffFinding`
- Minimal functions:
  - `capture_trace()`
  - `normalize_trace()`
  - `validate_capabilities()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `lsp`
  - `dap`
  - `lsif`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target **LSP 3.17**, a practical subset of **DAP**, and basic LSIF surface comparisons.
- The crate should complement existing server frameworks rather than replace them.
- Client/editor-specific policy packs can stay optional.
- The core should remain useful for both language-specific tooling and generic protocol infrastructure.

# Conformance & fixtures

- Tiny captured traces for initialize / hover / completion / semantic-token / shutdown flows.
- DAP goldens for launch, set-breakpoints, continue, stack-trace, and disconnect.
- LSIF fixtures that check moniker/navigation consistency against live server behavior.
- Goldens for capability over-advertising, partial-result mishandling, cancellation drift, and debugger config mismatches.

# Path to boring stability

- Stabilize transcript and findings schemas before broadening feature coverage.
- Keep early protocol surface intentionally small and explainable.
- Freeze bundle layout only after it works across a few editors and adapters.
- Add client-specific overlays after the neutral capability model proves durable.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A library and CLI that capture or import an LSP/DAP session trace, normalize it, validate it against a pinned capability lock, and emit a compact `*.lspbundle.zip` for CI and bug handoff.

# De-risk plan

1. Start with a narrow subset of LSP and DAP messages.
2. Normalize transcripts before inventing many custom checks.
3. Keep LSIF comparison optional at first.
4. Use tiny reference servers/adapters in the first fixture corpus.

# Non-goals

- Not a new language-server framework.
- Not a debugger UI.
- Not a full IDE test runner.
- Not a replacement for protocol type crates.

# Architecture & API sketch

```rust
pub struct ToolingReport {
    pub lock_id: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<ToolingDiffFinding>,
}

pub fn validate_capabilities(lock: &CapabilityLock, trace: &SessionTrace) -> Result<ToolingReport>;
pub fn capture_trace(reader: impl std::io::Read) -> Result<SessionTrace>;
```

Bundle draft: `profile.toml`, `capabilities.json`, `trace.jsonl`, `normalized.json`, `lsif.json`, `diff.json`, `notes.md`.

# Security / safety model

- Treat all client/server transcripts as untrusted input.
- Default to path/URI/token redaction in bundles.
- Record exact protocol and lockfile versions.
- Support deterministic normalization so traces stay diff-friendly.

# Maintenance & governance plan

- Keep core focused on capability models, trace normalization, and bundle formats.
- Version editor/client quirk packs separately.
- Grow a small public corpus of reference sessions.
- Avoid coupling to one editor or one language ecosystem.

# Milestones

## 0.1
- trace normalizer
- capability lockfiles
- bundle writer

## 0.2
- replay harness
- semantic diffs
- optional LSIF comparisons

## 1.0
- stable `*.lspbundle.zip`
- public fixture corpus
- documented upgrade policy for protocol and client-quirk drift

# Open questions

- Which editor quirks belong in generic profile packs versus external adapters?
- How much transport detail should be preserved in normalized traces?
- What minimum LSIF comparison is useful without absorbing full code-intelligence semantics?

# Sources

- LSP 3.17 specification: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
- DAP specification: https://microsoft.github.io/debug-adapter-protocol/specification.html
- LSIF overview: https://microsoft.github.io/language-server-protocol/overviews/lsif/overview/
- `tower-lsp`: https://docs.rs/tower-lsp
- `dap`: https://crates.io/crates/dap
- `ls-types`: https://crates.io/crates/ls-types
- `lsp-types`: https://docs.rs/lsp-types
