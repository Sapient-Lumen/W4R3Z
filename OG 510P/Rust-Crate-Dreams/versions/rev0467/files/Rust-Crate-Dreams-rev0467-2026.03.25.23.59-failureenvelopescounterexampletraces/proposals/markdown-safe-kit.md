---
id: P-0068
title: Markdown Safe Kit — safe-by-default Markdown→HTML pipelines with XSS conformance tests
status: idea
domains: [web, security, wasm, docs, devtools]
last_reviewed: 2026-03-01
evidence:
  - https://users.rust-lang.org/t/how-to-ensure-rendered-markdown-is-safe-pulldown-cmark/129880
  - https://users.rust-lang.org/t/how-to-ensure-rendered-markdown-is-safe-pulldown-cmark/129880/4
  - https://crates.io/crates/pulldown-cmark
---

# Problem
Rust has strong Markdown parsers, syntax highlighters, and HTML sanitizers, but developers still struggle to build a **safe-by-default** pipeline:
- preventing XSS and unsafe attributes when rendering to HTML
- allowing “just enough” HTML/classes for syntax highlighting
- working in WASM/browser contexts (where the threat model is immediate)

This leads to bespoke, error-prone glue code and missing test coverage.

# Users & user stories
- Docs sites and CMSs: “I want Markdown rendering that is safe to embed in a browser without being a security expert.”
- WASM apps: “I need a pipeline that works client-side and doesn’t accidentally allow XSS.”
- Library authors: “I need conformance tests and a stable config story for sanitization.”

# Prior art (and why it’s insufficient)
- `pulldown-cmark` parses CommonMark and can render HTML, but it’s not a sanitizer; safety questions recur.
- Common advice is to combine a sanitizer (`ammonia`) with syntax highlighting (`syntect`) and allow-list classes — but each project re-derives the safe config and misses edge cases.

# Design goals
- **One public entrypoint**: `render_safe(markdown, options) -> SafeHtml`
- Safe defaults:
  - no raw HTML passthrough unless explicitly enabled
  - strict URL schemes, attribute allow-lists
- First-class extension hooks:
  - syntax highlighting with class allow-list support
  - custom tag/attribute allow-lists (auditable diffs)
- **XSS conformance suite**:
  - curated corpus of malicious inputs
  - golden sanitized outputs
- WASM compatibility (no OS-only deps; feature flags for heavier components).

# Non-goals
- A new Markdown parser.
- A full static site generator.

# Architecture
- `markdown-safe-core`:
  - pipeline orchestration + config schema
  - `SafeHtml` wrapper with redaction-safe debug formatting
- `markdown-safe-syntect` (optional):
  - highlight integration and allowed-class management
- `markdown-safe-cli` (optional):
  - `render` + `audit` (run XSS corpus against current config)

# MVP plan
## 0.1
- Core pipeline: pulldown-cmark → HTML → sanitize (strict default)
- Minimal XSS corpus + test runner
- WASM build target verified

## 0.2
- Syntect integration helper and class allow-list plumbing
- “Explain” mode: show why an element/attr was removed (debugging).

# Adoption plan
- Provide drop-in examples for Axum + static hosting + WASM SPA.
- Publish the conformance corpus as a separate crate for reuse.
