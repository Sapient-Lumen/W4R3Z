---
id: P-0040
title: proc-macro-sandbox-kit — tools to prepare for Wasm-sandboxed proc macros
status: idea
domains: [proc-macro, supply-chain, reproducibility]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/rust-lang/compiler-team/issues/876
  - https://internals.rust-lang.org/t/pre-rfc-sandboxed-deterministic-reproducible-efficient-wasm-compilation-of-proc-macros/19359
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
---

# Problem
Proc macros are powerful but currently run as dynamically-linked native code, creating **security** and **reproducibility** hazards. The compiler team is actively exploring a WebAssembly execution model, but crate authors lack a practical toolkit for **making proc macros “Wasm-ready”** (constraints, build pipelines, testing).

# Users & user stories
- **Proc-macro authors**: “Tell me what I must avoid to run in a sandboxed proc-macro world, and give me a tool to test it.”
- **Large orgs**: “We want to gate proc macros to a ‘safe subset’ now, before upstream changes land.”
- **Tooling ecosystem**: “We want a standard harness to run proc macros under restricted environments.”

# Prior art (and why it’s insufficient)
- Upstream discussions describe goals and approaches, but not a day-to-day developer kit.
- Individual sandboxes exist, but there’s no shared “compatibility test suite” or migration guidance.

# Design goals
- Provide a “Wasm-ready” **lint + test harness** for proc macros.
- Provide optional build tooling to compile proc-macro logic to a Wasm target for experimentation.
- Produce actionable diagnostics (“this proc macro attempts filesystem access via X”).

# Non-goals
- Replace rustc/Cargo’s eventual official mechanism.
- Guarantee universal compatibility (some proc macros genuinely require host access).

# Architecture & API sketch
Crates:
- `proc-macro-sandbox-kit` (library): defines capability model + harness runner.
- `cargo proc-macro-sandbox` (CLI): runs checks & tests.

Key pieces:
- **Compatibility lints**
  - dependency scanning for known “host-only” patterns
  - optional dynamic checks in a sandbox runner
- **Harness**
  - execute expansion against a corpus of inputs
  - run under restrictions (no net, limited FS, deterministic env)
  - emit a report artifact (JSON)

Example:
```bash
cargo proc-macro-sandbox check
cargo proc-macro-sandbox test --corpus corpora/
```

# Security / safety model
- Runner must treat proc macros as hostile code.
- Prefer OS sandboxing + strict resource limits (time/memory).
- Determinism mode: fixed env vars, stable temp dirs, `SOURCE_DATE_EPOCH`.

# Maintenance & governance plan
- Maintain a public corpus of “macro patterns” and compatibility expectations.
- Keep the kit aligned with upstream compiler-team direction; file issues when gaps appear.

# Milestones
- **0.1**: static lints + sandboxed runtime harness (native proc macros, sandboxed process).
- **0.2**: experimental Wasm build path + compatibility tags.
- **1.0**: widely adopted “proc macro hygiene badge” + CI action template.

# Open questions
- What “capability model” matches upstream best (FS/net/env)?
- How to provide meaningful determinism when macros depend on rustc internals?

# Sources
- https://github.com/rust-lang/compiler-team/issues/876
- https://internals.rust-lang.org/t/pre-rfc-sandboxed-deterministic-reproducible-efficient-wasm-compilation-of-proc-macros/19359
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
