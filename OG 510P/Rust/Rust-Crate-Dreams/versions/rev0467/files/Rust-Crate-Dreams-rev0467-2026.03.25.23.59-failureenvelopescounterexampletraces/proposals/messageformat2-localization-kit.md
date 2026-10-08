---
id: P-0199
title: MessageFormat 2 Localization Kit — MF2 parser/formatter + ICU4X integration + conformance fixtures
status: idea
domains: [i18n, gui, web, formatting, correctness, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://www.unicode.org/reports/tr35/tr35-messageFormat.html
  - https://messageformat.unicode.org/
  - https://github.com/unicode-org/message-format-wg
  - https://blog.unicode.org/2025/03/unicode-cldr-47-release-messageformat-2.html
  - https://github.com/unicode-org/icu4x
  - https://crates.io/crates/fluent
needs:
  - Rust has solid i18n primitives (ICU4X) and an established localization stack (Fluent), but lacks a **native, conformance-driven** implementation of Unicode MessageFormat 2 (MF2), which is becoming the new standard for dynamic messages.
  - App authors want a stable, cross-platform message system that composes with ICU-style formatters (numbers/dates) and avoids “roll your own plural logic” mistakes.
risks:
  - Localization systems are language-sensitive; correctness must be proven by conformance fixtures and differential checks, not just unit tests.
  - Scope creep (full localization platform). MVP must focus on **MF2 core + ICU4X adapters + fixtures**, not translation management.
---

# Problem

Dynamic UI messages (plural/gender/select, formatted numbers/dates, rich grammatical matching) are a repeated source of bugs and ecosystem fragmentation. Unicode’s **MessageFormat 2** (MF2) aims to standardize this layer, but Rust does not yet have a “default” MF2 implementation with:

- a strict parser and stable AST
- ICU4X-backed formatting hooks
- conformance tests tied to the normative spec
- ergonomics for embedding in Rust apps (server and GUI)

# What it provides

A library-first, conformance-first MF2 stack:

1) **MF2 parser + AST (stable, diffable)**
- strict parser with good diagnostics
- stable AST serialization (`mf2-ast.json`) for caching and tooling

2) **Formatter runtime with ICU4X adapters**
- builtin selectors (plural rules, grammatical matching)
- formatters that delegate to ICU4X (numbers, dates, lists, relative time) where appropriate
- extension points for custom formatters/selectors

3) **Conformance & fixtures**
- import normative examples from TR35 MessageFormat
- fuzzing harness for parser + runtime
- “golden output” test runner for multiple locales

4) **Developer experience**
- `cargo mf2 check`: validate message files; produce diagnostics + `mf2-report.json`
- `cargo mf2 extract`: extract message ids and variables from Rust code (macro-assisted)

5) **Interop & migration helpers**
- compatibility notes/migration tooling for:
  - Fluent (where it remains a better fit)
  - legacy ICU MessageFormat
  - simple gettext-style strings

# Users & user stories

- **App developers**: “Use one message system for plurals/selection/formatting without reimplementing locale logic.”
- **Localization engineers**: “Validate message catalogs with clear diagnostics and conformance checks.”
- **Framework/toolkit maintainers**: “Offer MF2 support as a stable, testable dependency with ICU4X hooks.”

# Design goals / non-goals

**Goals**
- Spec-aligned parser/AST with excellent diagnostics.
- ICU4X integration for formatting and locale data.
- Conformance fixtures and differential checks as a release gate.

**Non-goals**
- Translation management tooling (CAT tools, workflows, hosted platforms).
- Forcing MF2 everywhere; provide migration/interop guidance with Fluent/gettext.

# Prior art (and why it’s insufficient)

- Fluent has a mature Rust implementation and is widely used, but MF2 is a separate emerging standard with different goals and integration points.
- ICU stacks in other languages are ahead; Rust needs a native implementation that composes with ICU4X’s Rust-first design.

# Architecture & API sketch

Crates:
- `mf2-syntax`: lexer/parser + diagnostics
- `mf2-ast`: stable AST + serde formats
- `mf2-runtime`: evaluation engine + ICU4X hooks
- `mf2-conformance`: fixtures + runner
- `cargo-mf2`: CLI tools

Core API:
- `Message::parse(&str) -> Result<Message, Diagnostic>`
- `Message::format(&self, args: &Args, locale: &Locale, providers: &Providers) -> Result<String, EvalError>`

# Minimum lovable MVP

- Spec-aligned parser + AST
- Minimal runtime with:
  - variables
  - select/plural (at least via ICU4X plural rules)
  - number/date formatting hooks
- A conformance runner that executes a small, curated fixture suite across a handful of locales

# De-risk plan

1) Start from the normative TR35 model: implement only the core, then add extension points.
2) Gate advanced features behind explicit opt-ins; keep the default runtime small.
3) Build fixtures first: every feature must land with a conformance case.

# Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4
