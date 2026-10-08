---
id: P-0072
title: pdf-safe-kit — safe-by-default PDF parsing/extraction patterns + fuzz/conformance scaffolding
status: idea
domains: [documents, security, parsing, fuzzing, data-ingest]
last_reviewed: 2026-03-01
evidence:
  - https://crates.io/crates/lopdf
  - https://crates.io/crates/pdf-rs
  - https://github.com/rust-fuzz/trophy-case
  - https://www.firecrawl.dev/blog/pdf-parser-v2
  - https://crates.io/crates/pdfium
---
# Problem
PDF is a hostile, complex format. Rust PDF crates exist, and performance-focused parsers are emerging, but security posture is inconsistent: resource limits, decompression bombs, recursion depth, object stream handling, and corpus-based fuzzing are not standardized. Teams repeatedly rebuild “safe mode” wrappers and ad-hoc fuzz harnesses.

# Users & user stories
- **Document ingestion systems** want to extract text/metadata/images safely with predictable resource usage.
- **Security teams** want fuzzing scaffolds and safety knobs (caps, timeouts) that are easy to enforce.
- **Library authors** want shared fixtures and a common language for “what safe mode means.”

# Prior art (and why it’s insufficient)
- `lopdf` is a general PDF library for manipulation; safe-by-default ingestion patterns (limits, streaming extraction) are not its primary product. https://crates.io/crates/lopdf
- `pdf-rs` and other parsers show active work, but the ecosystem lacks a shared “safe mode” contract and conformance harness. https://crates.io/crates/pdf-rs
- C-backed solutions like PDFium are common and useful, but need sandboxing and strict boundary handling to be safe in ingestion pipelines. https://crates.io/crates/pdfium
- Rust-fuzz’s trophy case shows fuzzing uncovers real crash/DoS patterns in Rust projects — a hint that parser safety needs fixtures + harnesses, not just code review. https://github.com/rust-fuzz/trophy-case
- Recent Rust-based PDF parsing in production products demonstrates demand for fast extraction, but not a standardized safety kit. https://www.firecrawl.dev/blog/pdf-parser-v2

# Design goals
- **Safe-by-default wrapper API** with explicit limits:
  - max objects, max recursion depth, max decompressed bytes per stream
  - max page count, max image pixels, max font table size
- **Backend adapters**:
  - pure-Rust parser backends (`lopdf`, `pdf-rs`) first
  - optional PDFium backend behind a feature flag, with recommended sandbox configuration
- **Fuzz & conformance scaffolding**:
  - cargo-fuzz harness templates + guidance
  - a small, redistributable corpus policy (how to curate/triage)
  - regression fixtures (panic/OOM prevention tests)
- **Explain mode**: on failure, produce structured reasons (“limit hit”, “unsupported feature”, “invalid xref”, etc.)

# Non-goals
- Becoming “the one true PDF library.”
- Implementing a full renderer in 0.x.

# Architecture & API sketch
## Core interface
- `PdfReader::open(bytes, Limits) -> Result<PdfDoc>`
- `PdfDoc::extract_text(opts) -> Result<String>`
- `PdfDoc::pages() -> impl Iterator<Item=PageHandle>`
- `PdfError` includes `Reason` and optional `LimitHit { kind, value }`

## Backends
- `backend_lopdf`: parse with lopdf, enforce limits during traversal.
- `backend_pdf_rs`: parse with pdf-rs, enforce limits similarly.
- `backend_pdfium` (optional): run decode in a restricted subprocess (recommended), return extracted text.

# Security / safety model
- Default limits should prevent common DoS vectors (huge decompression, deep recursion, pathological xref/object streams).
- Treat PDFs as untrusted; do not allocate unboundedly; prefer streaming where possible.
- For C-backed backends, recommend a subprocess sandbox boundary (ties into `isolate-kit` / `cargo-build-jail` proposals).

# Maintenance & governance plan
- Separate “core limits + error taxonomy” from backend adapters.
- Maintain a public regression corpus with careful licensing notes; accept “structure-only” minimized PDFs where possible.

# Milestones
- **0.1**: core limits + lopdf adapter + minimal text extraction + limit-hit reasons.
- **0.2**: fuzz harness templates + CI fuzz smoke tests; expand error taxonomy.
- **0.3**: pdf-rs adapter + conformance fixtures; optional PDFium backend (feature-flagged).
- **0.4**: structured output modes (blocks/spans) with bounded memory.

# Open questions
- What are the minimal “safe default” limits that won’t break most real PDFs?
- How to curate a redistributable corpus responsibly (licensing + PII)?

# Sources
- https://crates.io/crates/lopdf
- https://crates.io/crates/pdf-rs
- https://github.com/rust-fuzz/trophy-case
- https://www.firecrawl.dev/blog/pdf-parser-v2
- https://crates.io/crates/pdfium
