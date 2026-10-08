---
id: P-0153
title: GitOps Secrets Interop Kit (SOPS/age compatible)
status: idea
domains: [security, devops, secrets, gitops, tooling, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://getsops.io/
  - https://github.com/getsops/sops
  - https://github.com/gibbz00/rops
  - https://crates.io/crates/age
  - https://fluxcd.io/flux/guides/mozilla-sops/
---
# Problem

SOPS has become a de facto standard for “encrypted secrets in Git” workflows, especially in Kubernetes/GitOps ecosystems. But Rust projects still lack a cohesive, library-first way to:

- **Read/write SOPS-compatible encrypted docs** from Rust services/CLIs
- Enforce **policy** (key groups, required recipients, rotation, forbidden providers)
- Produce **auditable evidence** in CI (what changed, who can decrypt, what policy failed)
- Provide safe redacted repro artifacts when things go wrong

There are emerging Rust implementations (e.g. `rops`) and strong primitives (`age`), but we’re missing the *workbench layer* that makes this reliable and boring.

# What it should provide

## 1) A compatibility-focused library API
- Parse + validate SOPS metadata and encrypted payload structure
- Encrypt/decrypt YAML/JSON/TOML with SOPS-compatible semantics
- Providers/adapters: **age**, KMS stubs/traits (AWS/GCP/Azure) with feature flags
- A strict mode that rejects ambiguous edge cases (security-first)

## 2) Policy and hygiene as first-class objects
A policy file (e.g. `SecretsPolicy.toml`) for:
- required recipient sets and key-group rules
- allowed key providers
- rotation windows
- “no plaintext secret keys in repo” checks (pattern scanning)

## 3) CI-native evidence bundles
A portable `seopsbundle.zip` with:
- `manifest.json` (tool fingerprints, policy hash)
- `inputs/` (redacted structure + schema, never raw secrets)
- `sops_meta.json` (normalized metadata)
- `diff/` semantic diffs (which keys/groups changed)
- `report.json` (pass/fail + reasons)
- optional `repro.md` for maintainers

This should be safe to attach to issues by default.

## 4) Cargo UX: `cargo secrets`
- `cargo secrets check` (policy + schema + metadata hygiene)
- `cargo secrets rotate --plan` (produce a rotation plan artifact)
- `cargo secrets bundle` (produce the evidence bundle)
- `cargo secrets doctor` (common failure explanations)

# MVP → v1 roadmap

1) **MVP (0.x)**: SOPS metadata parsing + age encryption/decryption + `cargo secrets check` + evidence bundle.
2) **v0.5**: key-group policy + semantic diffs + rotation plan artifacts.
3) **v1.0**: provider traits + integration “packs” (Flux, ArgoCD) + long-term compatibility test corpus.

# Design notes

- Default to **age** (modern + recommended by SOPS) and keep provider plugins behind features.
- Treat “compatibility corpus” as critical: ship a set of encrypted fixture files and round-trip tests.
- Make redaction ergonomic: the bundle must be safe *by construction*.

# Why this is worthy

It would make Rust first-class in a widely used operational pattern: encrypted Git configuration, enforced by CI, usable by humans, and safe to debug.
