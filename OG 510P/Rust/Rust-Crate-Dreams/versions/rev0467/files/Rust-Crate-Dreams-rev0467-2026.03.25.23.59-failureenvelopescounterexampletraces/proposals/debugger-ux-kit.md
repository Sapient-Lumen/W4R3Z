---
id: P-0083
title: Debugger UX Kit (Rust pretty-printing + debug “doctor”)
status: idea
domains: [devtools, debugging, lldb, gdb, cargo-tooling]
last_reviewed: 2026-03-04
evidence:
  - https://github.com/cmrschwarz/rust-prettifier-for-lldb
  - https://users.rust-lang.org/t/lldb-debugger-doesnt-pretty-print-vec/119974
  - https://cygwin.org/packages/x86_64/rust-debugger/rust-debugger-1.91.0-1
---

# Problem

Rust debugging still has a “works until it doesn’t” feel across platforms and IDEs: enums, `Vec`, `Result`, etc. can become painful to inspect when debugger formatters drift, get removed, or don’t match toolchain layouts. This turns routine debugging into a time sink and pushes people toward `dbg!()`-driven workflows even for complex systems.

Recent examples include third-party efforts to restore LLDB Rust pretty-printing after ecosystem changes, described as a stopgap until the situation improves. See `rust-prettifier-for-lldb`.  
Sources: `rust-prettifier-for-lldb` repo; Rust users thread on CodeLLDB pretty printing regressions.

# Users & user stories

- **App dev (desktop/server)**: “My debugger should show `Vec<T>` and enums sanely without spelunking raw memory.”
- **Systems/embedded**: “When I can attach a debugger, I need reliable visualization of `Option<Result<…>>` chains quickly.”
- **Tooling authors**: “I want a stable interface to ship formatters with my crate/product and validate compatibility in CI.”
- **Educators**: “Debugging basics should not depend on ‘secret scripts’ per OS.”

# Prior art (and why it’s insufficient)

- **Rust toolchain scripts**: `rust-gdb`/`rust-lldb` ship helpers (often packaged as “rust-debugger”), but distribution and IDE integration are inconsistent across platforms and installations. Source: rust-debugger package listing.
- **Ad-hoc pretty-printer repos**: e.g. `rust-prettifier-for-lldb` exist as community patches, but lack a standard packaging story, compatibility matrix, and CI-conformance approach. Source: `rust-prettifier-for-lldb` repo.
- **IDE extensions**: frequently re-invent integration, and regressions land when upstream or toolchain structures change. Source: users thread about CodeLLDB and `Vec` pretty printing.

# Design goals

1. **Cross-platform, versioned “debug support pack”**: ship formatters for LLDB + GDB + (optionally) WinDbg/VS tooling with explicit support ranges.
2. **Automatic installation & diagnosis**: `cargo debug-doctor` prints actionable steps (“your LLDB uses python3.11; formatter expects 3.12”, “missing rustlib/etc scripts”, “CodeLLDB setting X off”).
3. **Conformance tests**: a suite of tiny Rust programs + expected debugger renderings (“goldens”) to detect regressions per toolchain version.
4. **Opt-in product embedding**: libraries and apps can include the support pack as an artifact (or ask users to install it) with a one-line printed help message.
5. **Minimize brittleness**: avoid depending on private compiler internals; where unavoidable, isolate by version and test.

# Non-goals

- Becoming a full debugger UI.
- Guaranteeing perfect pretty printing for every custom type (provide extension points instead).
- Solving “debug optimized async in production” generally (out of scope; see record/replay proposals elsewhere).

# Architecture & API sketch

**Crates:**
- `debugger_ux`: core, no-std optional; defines test cases & expected shapes; provides install logic.
- `debugger_ux-lldb` / `debugger_ux-gdb`: formatter packs + adapters.
- `cargo-debug-doctor`: cargo subcommand.

**Key pieces:**
- **Formatter pack** layout:
  - `formatters/lldb/*.py`
  - `formatters/gdb/*.py`
  - `compat/*.toml` (toolchain/debugger versions; feature flags)
- **Golden tests**:
  - compile fixture programs
  - run debugger in batch mode
  - capture pretty-printed output
  - normalize platform differences
- **Extension points**:
  - macro/helper to register “type views” for user types
  - support for “derive(DebuggerView)” as optional proc-macro

# Security / safety model

- Running debugger scripts is a code-execution surface; treat the pack as software you install.
- Provide checksums and signed releases (Sigstore optional; see supply-chain proposals).
- `cargo debug-doctor` should never auto-fetch remote code unless explicit (and then verify).

# Maintenance & governance plan

- Versioned compatibility matrix in repo, updated via CI jobs that test nightly/beta/stable + major debugger versions.
- Keep scope tight: support the 20–30 most common std/core types first; add more only with tests.
- Encourage downstream contributions via “failing golden” PRs.

# Milestones

1. **MVP**: stable LLDB pack + `cargo debug-doctor` for macOS/Linux; fix std types (`Vec`, `String`, enums, `Result`, `Option`, `HashMap`).
2. **CI goldens**: run across a small matrix, publish dashboard.
3. **GDB pack**: parity with LLDB where feasible.
4. **IDE hooks**: docs + snippets for CodeLLDB, rust-analyzer, CLion.

# Open questions

- Best normalization strategy for debugger textual outputs across platforms.
- How to track rustc layout shifts without chasing internal changes.
- What’s the lightest-weight extension mechanism for user-defined types that won’t break often.

# Sources

- https://github.com/cmrschwarz/rust-prettifier-for-lldb
- https://users.rust-lang.org/t/lldb-debugger-doesnt-pretty-print-vec/119974
- https://cygwin.org/packages/x86_64/rust-debugger/rust-debugger-1.91.0-1
