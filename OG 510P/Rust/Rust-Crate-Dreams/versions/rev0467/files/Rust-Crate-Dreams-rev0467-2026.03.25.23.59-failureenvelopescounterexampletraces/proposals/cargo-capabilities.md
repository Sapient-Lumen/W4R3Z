---
id: P-0033
title: cargo-capabilities — declarative capability manifests for build-time code (enforced by sandbox tools)
status: idea
domains: [cargo, security, policy, supply-chain, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://internals.rust-lang.org/t/build-script-capabilities/8635
  - https://internals.rust-lang.org/t/pre-pre-rfc-solving-crate-trust/6495
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
  - https://internals.rust-lang.org/t/compile-time-sandbox/21139
---

# Problem

Even with a sandbox, a practical question remains:
**what should this build script / proc macro be allowed to do?**

Today, teams either:
- allow everything (status quo), or
- break builds by denying everything and adding ad-hoc exceptions.

A declarative *capability manifest* would let crates state what they need (fs/net/env/process),
and let organizations enforce policies with fewer surprises.

This is a long-running idea in the ecosystem discussions, but there is still no widely adopted convention or toolchain-level artifact.

# Users & user stories

- **Crate authors:** “My build script only needs to read headers from `/usr/include` and write to `OUT_DIR`.”
- **CI/security teams:** “Deny network in build scripts by default; allow it only for explicitly declared crates.”
- **Reviewers:** “Show me a diff of capability requests between releases; alert on new network access.”
- **Tool authors:** “Consume capability metadata to drive sandbox policy (cargo-build-jail, cargo-policy, etc.).”

# Prior art (and why it’s insufficient)

- Internals threads propose capability systems, but no stable on-disk schema exists for tools to share.
- Some orgs implement internal allowlists, but these don’t travel well and aren’t standardized.

# Design goals

1. **Convention-first**: use `Cargo.toml` metadata (no compiler changes required).
2. **Toolable**: produce a lockfile-like resolved capability graph for the workspace.
3. **Diffable**: easy to see when an update adds `net` or broader fs access.
4. **Composable**: integrates with sandbox runners (cargo-build-jail) and policy engines (cargo-policy).
5. **Minimal schema**: few capability classes with escape hatches (explicit paths/domains).

# Non-goals

- Enforcing capabilities without sandboxing (manifest is declarative; enforcement is a separate concern).
- Fine-grained object-capability systems inside compiled code.

# Architecture & API sketch

## Manifest format

In `Cargo.toml`:

```toml
[package.metadata.cargo-capabilities]
build = { fs_read = ["$CARGO_MANIFEST_DIR/**"], fs_write = ["$OUT_DIR/**"], net = "deny", env_read = ["TARGET", "HOST"] }
```

Tool outputs:
- `target/capabilities.lock` (resolved union across dependency graph and features/targets)
- `cargo capabilities diff --from <rev> --to <rev>`
- `cargo capabilities explain <crate>` (why this capability is needed)

# Security / safety model

- This does not create a security boundary by itself.
- When combined with sandbox enforcement, it becomes a powerful “least privilege” workflow.
- The key win is reducing surprise and making review/policy scalable.

# Maintenance & governance plan

- Keep schema versioned and documented.
- Provide a compatibility policy: older tools ignore unknown keys safely.
- Encourage coordination with upstream sandboxing efforts (Rust Project Goals).

# Milestones

0. **0.1**: schema v0 + `cargo capabilities check` validator.
1. **0.2**: `capabilities.lock` resolver (workspace + dependency graph).
2. **0.3**: diff & CI gate (fail on new net/fs broadening without approval).
3. **0.4**: integration with `cargo-build-jail` policy compilation.

# Open questions

- How to model feature/target-specific capability differences without exploding complexity?
- How to avoid “capability spam” while staying expressive?

# Sources

- Build script capabilities discussion (2018).
- Pre-pre-RFC solving crate trust (2018).
- Rust Project Goal on sandboxed build scripts.
- Compile time sandbox discussion (capabilities + critiques).
