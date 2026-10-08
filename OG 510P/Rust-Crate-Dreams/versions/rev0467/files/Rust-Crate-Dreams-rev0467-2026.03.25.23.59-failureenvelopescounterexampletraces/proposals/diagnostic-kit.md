---
id: P-0004
title: Diagnostic Kit — rustc-like errors for tools, parsers, compilers
status: idea
domains: [dx, cli, diagnostics, tooling]
last_reviewed: 2026-02-28
evidence:
  - https://users.rust-lang.org/t/a-crate-to-print-cute-rustc-like-compiler-errors/18914
  - https://crates.io/crates/miette
  - https://crates.io/crates/codespan-reporting
  - https://docs.rs/ariadne
---

# Problem
Many Rust tools want rustc-quality diagnostics (spans, labels, help notes, suggestions). Historically, rustc’s internals were tightly coupled, and people asked for a “plug in and go” crate for compiler-style errors.

# Users & user stories
- CLI tool authors: “When parsing a config or DSL, show users exactly where it broke.”
- Language tooling authors: “I want to emit diagnostics with snippets and fix-its.”
- Library authors: “I want structured errors I can render in multiple styles.”

# Prior art (and why it’s insufficient)
- Multiple crates exist in this space, but the ecosystem still lacks a *default* with:
  - a stable spec for spans/labels,
  - consistent UX patterns,
  - easy integration with `anyhow`/`thiserror`/`miette`-style errors.

# Design goals
- A small, stable core data model:
  - source files, spans, labels, severity, codes, help
- Multiple renderers:
  - “rustc” style
  - JSON (for IDEs)
  - minimal (for logs)
- Ergonomic builder API + derive macros
- Unicode-aware, terminal-color safe (termcolor-compatible)

# Non-goals
- Being tied to a specific parser library.

# Architecture & API sketch
- `diagnostic-kit-core` (data model)
- `diagnostic-kit-render` (terminal + json)
- `diagnostic-kit-macros` (derive helpers)

# Security / safety model
- Defensive handling of untrusted input (file paths, text).
- No unsafe in core; isolate unsafe in renderer if needed.

# Maintenance & governance plan
- Stability pledge for the core model.
- Golden-tests for renderer output.

# Milestones
- 0.1: core model + rustc-style renderer
- 0.2: JSON renderer + LSP-friendly output
- 0.3: macros + integrations
- 1.0: stable spec + docs

# Sources
- https://users.rust-lang.org/t/a-crate-to-print-cute-rustc-like-compiler-errors/18914
