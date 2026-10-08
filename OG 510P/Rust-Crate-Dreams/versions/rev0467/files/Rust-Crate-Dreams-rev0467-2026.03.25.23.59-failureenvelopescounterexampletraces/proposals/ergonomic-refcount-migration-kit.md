---
id: P-0448
title: Ergonomic Ref-Counting Migration Kit — Share-trait ledgers, capture audits, and closure-migration receipts above today’s Rc/Arc idioms
status: idea
domains: [language, async, gui, ergonomics, interop, devtools, ci]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/ergonomic-rc.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/ergonomic-rc.html
---

# Problem

Rust is actively rethinking ergonomic ref-counting because real users keep running into the same pain:

- `Rc` and `Arc` capture patterns in closures and async blocks are verbose,
- the ceremony obscures business logic,
- the problem shows up in GUI frameworks, async services, language interop, and even the compiler,
- and there is genuine design tension between ergonomic shorthand and keeping ref-count changes visible.

The 2026 direction is sharper than before: prototype a semantic `Share` trait and move expressions that give more precise closure-capture control while keeping ref-count behavior understandable.

But ordinary maintainers still lack a crate that helps them answer practical questions like:

- where do we currently clone-to-alias versus clone-to-copy?
- which closures would benefit from future share-aware migration?
- how many patterns depend on today’s explicit clone visibility?
- and what would a semver-safe migration plan look like if the language direction matures?

The missing crate is not another smart pointer.

The missing crate is a **migration kit** that turns ref-count ergonomics work into a reviewable adoption plan.

# What it provides

- `share-profile.toml` — pins analysis scope, closure families, alias-vs-copy policy, and migration assumptions.
- `capture-audit.json` — lists current closure / async-block capture patterns involving `Rc`, `Arc`, references, senders, and other aliasing types.
- `share-ledger.json` — distinguishes semantic aliasing (`Share`-like) from independent-copy cloning in the analyzed codebase.
- `migration.receipt.json` — records which code patterns are mechanically migratable, ambiguous, or intentionally explicit.
- `share-codemod.patch` — optional patch draft for purely mechanical migration hints where policy allows.
- `cargo share-migrate audit` — scans a crate/workspace and builds the capture ledger.
- `cargo share-migrate explain` — explains why a capture pattern is flagged as aliasing-heavy, cost-sensitive, or intentionally explicit.
- `*.sharebundle.zip` — shareable artifact for design review or edition/language migration planning.

# What the crate should provide other people

1. **A semantic ledger** separating alias-creating clones from independent-value clones.
2. **A migration plan** for future ergonomic ref-counting features without pretending they are stable already.
3. **A closure-capture audit** that helps teams see where today’s verbosity is concentrated.
4. **A review artifact** for deciding when explicit clone visibility is a feature, not a bug.
5. **A bridge** between language experiments and day-to-day application code.

# Persona / who it’s for

- GUI and async application maintainers
- interop-heavy projects using `Arc` or `Rc` pervasively
- library authors who expose callback-heavy APIs
- compiler/tooling contributors studying adoption pressure

# Users & user stories

- **GUI maintainer**: “Show me the hot spots where `Rc` clone boilerplate dominates closures.”
- **Async service author**: “Record which `Arc` captures are mechanical and which are performance- or clarity-sensitive.”
- **Interop maintainer**: “Track where aliasing semantics matter more than raw clone cost.”
- **Language experimenter**: “Bundle real examples showing how a `Share`-style feature would help without hiding important behavior.”

# Prior art (and why it’s insufficient)

- Rust has multiple goal periods devoted to ergonomic ref-counting and has now converged on `Share`-trait plus move-expression experiments.
- The standard library already gives the raw building blocks (`Rc`, `Arc`, sender-like aliasing handles), but those are operational tools, not migration artifacts.

What remains missing is a **semantic/adoption layer** that helps teams reason about aliasing-oriented clone patterns before any future syntax becomes stable.

# Design goals

1. **Semantic over operational** — distinguish aliasing intent, not just “cheap clone” folklore.
2. **Migration-honest** — never imply future language syntax is settled.
3. **Explicitness-aware** — some code wants visible ref-count changes; preserve that choice.
4. **Closure-first** — the first pain surface is capture patterns.
5. **Reviewable** — outputs should help humans decide, not silently rewrite code.

# MVP surface

- Minimal types: `ShareProfile`, `CaptureAudit`, `ShareLedger`, `MigrationReceipt`, `CodemodHint`, `ShareBundle`
- Minimal functions:
  - `scan_captures()`
  - `classify_aliasing_clone()`
  - `build_migration_receipt()`
  - `render_explanations()`
  - `write_bundle()`
- Feature flags:
  - `syn`
  - `quote`
  - `cargo`
  - `serde`
  - `codemod`

# Compatibility story

- Works on stable Rust source today; it is not blocked on future language stabilization.
- Treats future ergonomic features as optional migration targets, not assumptions.
- Can degrade to audit-only mode when codemod safety is unclear.
- Should complement, not replace, ordinary code review around ownership and performance.

# Conformance & fixtures

- Fixtures for `Arc`-into-async-block patterns.
- Callback-heavy `Rc` GUI captures.
- Sender-like aliasing handles.
- Cases where explicit clone visibility is intentionally preserved.
- Goldens for “mechanically migratable”, “ambiguous”, and “do not rewrite” categories.

# Path to boring stability

- Stabilize the aliasing taxonomy before any codemod layer.
- Keep future-language assumptions data-driven and versioned.
- Prefer explanations and receipts to aggressive rewriting.
- Add richer migration support only after the audit workflow proves useful.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and cargo subcommand that scan a workspace for `Rc`/`Arc` capture patterns, classify alias-oriented clones conservatively, and emit a `share-ledger.json` plus a migration receipt bundle.

# De-risk plan

1. Start with auditing and explanation, not rewriting.
2. Keep the aliasing taxonomy narrow and semantic.
3. Validate the workflow on one GUI crate and one async-heavy crate.
4. Add codemod hints only for truly mechanical patterns.

# Non-goals

- Not a new smart pointer crate.
- Not a promise that future ergonomic ref-counting syntax will look exactly one way.
- Not an optimizer that removes or inserts clones automatically without review.
- Not a performance oracle for atomic reference counting.

# Architecture & API sketch

```rust
pub enum CloneSemantics {
    Aliasing,
    IndependentValue,
    Ambiguous,
}

pub fn scan_captures(profile: &ShareProfile, root: &Path) -> Result<CaptureAudit>;
pub fn classify_aliasing_clone(expr: &CloneSite) -> CloneSemantics;
pub fn build_migration_receipt(audit: &CaptureAudit) -> MigrationReceipt;
pub fn write_bundle(bundle: &ShareBundle, out: &Path) -> Result<()>;
```

Bundle draft: `share-profile.toml`, `capture-audit.json`, `share-ledger.json`, `migration.receipt.json`, `notes.md`.

# Security / safety model

- Never silently rewrite ambiguous ownership code.
- Keep cost-sensitive sites explicitly marked.
- Support path and symbol redaction in shared bundles.
- Record the exact migration assumptions used when generating hints.

# Maintenance & governance plan

- Track the evolving ergonomic-refcounting design and keep assumptions versioned.
- Maintain a public corpus of representative capture patterns.
- Keep codemod logic optional and conservative.
- Publish guidance on when explicit clone visibility should be preserved.

# Milestones

## 0.1
- capture audit
- aliasing taxonomy
- bundle export

## 0.2
- explanation rendering
- migration receipts
- opt-in codemod hints

## 1.0
- stable receipt schema
- public corpus
- CI/report adapters

# Open questions

- What is the smallest useful aliasing taxonomy?
- Which capture patterns are actually safe to suggest for mechanical migration?
- How should the crate encode “keep explicit clones here on purpose”?

# Sources

- Ergonomic ref-counting in 2026: https://rust-lang.github.io/rust-project-goals/2026/ergonomic-rc.html
- Ergonomic ref-counting RFC decision and preview: https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
- Initial ergonomic ref-counting goal: https://rust-lang.github.io/rust-project-goals/2024h2/ergonomic-rc.html
