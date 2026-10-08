---
id: P-0048
title: install-script-jail — policy-driven sandbox runner for third-party installer scripts (curl|sh, bootstrap scripts)
status: idea
domains: [security, tooling, sandboxing, devx]
last_reviewed: 2026-03-01
evidence:
  - https://users.rust-lang.org/t/exploring-user-space-sandboxing-for-third-party-install-scripts-macos-rust/138456
  - https://github.com/madsmtm/cargo-sandbox
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
  - https://internals.rust-lang.org/t/compile-time-sandbox/21139
---

# Problem
A huge amount of developer tooling is still installed via third‑party bootstrap scripts (shell installers, “curl | sh”, custom update scripts). These scripts often run with full user permissions, touch `$HOME`, modify PATH files, download and execute binaries, and are difficult to audit.

Rust’s ecosystem is moving toward sandboxing at compile time (build scripts / proc macros), but the broader “installer scripts” problem remains unsolved, even though developers clearly want a safe, user-space sandbox approach.

# What this crate should provide other people
A **local-first, policy-driven sandbox runner** that:
- executes installer scripts in a constrained environment (filesystem + network + process policies),
- records what it did (auditable report artifact),
- and makes it possible to run these scripts safely without rewriting them.

The value is not “more sandbox theory”—it’s a tool that makes the default safer and debuggable.

# Users & user stories
- A developer wants to try a new CLI tool whose docs say “curl | sh”, but wants to constrain its side effects and review an audit report.
- A company wants a standard “safe installer runner” policy for developer laptops, with a per-team allowlist (e.g., “can write only to ~/.local/bin and ~/.cache/mytool”).
- A tool maintainer wants to provide a one-liner that runs in a safe jail and still works on macOS/Linux/Windows where possible.

# Prior art (and why it’s insufficient)
- One-off prototypes exist for user-space sandboxing of install scripts (macOS-focused), but there isn’t a reusable, portable tool with policies and report artifacts. Source: https://users.rust-lang.org/t/exploring-user-space-sandboxing-for-third-party-install-scripts-macos-rust/138456
- `cargo-sandbox` targets the Cargo build pipeline, not arbitrary installer scripts, and is not yet cross-platform. Source: https://github.com/madsmtm/cargo-sandbox
- Rust project goals discuss sandboxed build scripts (a related capability-driven direction), but installers are outside Cargo’s scope. Source: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

# Design goals
1) **User-space first**: no root, no daemon, minimal system assumptions.
2) **Policy profiles**: “laptop safe”, “CI safe”, “per-tool allowlists”.
3) **Explainability**: produce a report: what files were written, what hosts were contacted, what commands executed.
4) **Portability**: best-effort cross-platform; strong on Linux/macOS first, degrade gracefully elsewhere.
5) **Composable**: reuse `isolate-kit` (P-0031) once it exists; don’t duplicate sandbox primitives.

# Non-goals
- Full virtualization or container runtime replacement.
- Guaranteed identical behavior across OSes (sandbox capabilities differ).
- “Perfectly safe” execution of arbitrary scripts (goal is risk reduction + auditability).

# Proposed UX (CLI)
- `install-jail run --policy policy.toml -- bash -lc "curl -fsSL … | sh"`
- `install-jail fetch-run --url <script_url> --sha256 <expected> --policy policy.toml`
- `install-jail explain <report.json>`

# Policy model (v0)
- Filesystem:
  - allow read roots (e.g., `/usr`, `/etc`)
  - allow write roots (default: `~/.local/bin`, `~/.cache/install-jail/<tool>`)
- Network:
  - deny by default; allowlist hosts/domains
- Process:
  - deny exec outside allowlist (optional)
- Environment:
  - allowlist vars; redact secrets by default

# Report artifact
A JSON report (NDJSON optional) including:
- timestamps, exit status
- attempted network connections (host:port, allowed/denied)
- file write/create events (path, bytes, allowed/denied)
- executed commands (argv, allowed/denied)
- policy hash + tool version (so reports are comparable)

# MVP (0.1)
- CLI `run` with:
  - filesystem allowlist (read) + writable “staging” roots
  - network deny-by-default + allowlist
  - report artifact output
- macOS + Linux support (best effort) with clear “capability not supported” messaging.
- “safe defaults” policy profile included in repo examples.

# Milestones
0.2: `fetch-run` with script integrity pinning (sha256)  
0.3: richer reporting + redaction rules + policy diffing  
0.4: integration hooks for common tooling (e.g., wrappers for popular installers)

# Open questions
- How to model policies that are portable but not misleading (different OS primitives)?
- How to safely support “installer writes to PATH files” workflows without giving away the farm?
- Should the report format align with `cargo-event-stream` style NDJSON for reuse?

# Adoption plan
- Start as a standalone CLI + library.
- Provide recipes that map common install patterns to safe policies.
- Encourage maintainers to publish a recommended policy profile alongside install instructions.
