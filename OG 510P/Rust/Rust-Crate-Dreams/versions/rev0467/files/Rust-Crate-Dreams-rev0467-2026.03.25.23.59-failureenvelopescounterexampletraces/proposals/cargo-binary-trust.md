---
id: P-0047
title: cargo-binary-trust — verification + policy layer for installing Rust CLI binaries
status: idea
domains: [cargo, supply-chain, tooling, devx]
last_reviewed: 2026-03-01
evidence:
  - https://internals.rust-lang.org/t/feature-request-add-cargo-binstall-by-default/23876
  - https://internals.rust-lang.org/t/cargo-install-locked-or-not-locked-middle-ground/23893
  - https://github.com/cargo-bins/cargo-binstall
  - https://www.reddit.com/r/rust/comments/1n1gelr/cargobinstallquickinstall_distributing/
  - https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
  - https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
---

# Problem
Rust CLI tooling is increasingly installed via **prebuilt release artifacts** because building from source with `cargo install` can be slow. There’s active community pressure to make this workflow more “default”. But the trust story for downloaded binaries is still ad hoc: checksums, signatures, provenance, and “what exactly did I just run?” varies wildly across projects and CI setups.

This is not just theoretical. Users report antivirus flags and concerns when consuming third‑party binaries (which may be false positives, but still signals a trust and transparency gap).

# What this crate should provide other people
A **verification + policy layer** that sits between “download a binary” and “execute/install it”, with an explainable result.

Concretely, it should make it easy for:
- **CLI users** to install binaries quickly *and* confidently.
- **Org security teams** to enforce allow-lists, provenance requirements, and update policies.
- **Maintainers** to adopt a standard verification story without building a bespoke system.

# Users & user stories
- A developer runs `cargo binstall ripgrep` and wants an optional `--verify` mode that explains what was verified (checksum, signature, provenance).
- A company wants to allow only binaries that come from:
  1) a trusted release workflow (OIDC publish / CI identity), and
  2) a verified provenance statement, and
  3) a known set of publishers/orgs.
- A maintainer wants “one more file in the release” that unlocks verification across multiple installer tools.

# Prior art (and why it’s insufficient)
- `cargo-binstall` solves *distribution ergonomics* but does not define a universal, portable, policy-driven verification bundle. Source: https://github.com/cargo-bins/cargo-binstall
- Trusted Publishing (OIDC) reduces publishing-token risk, but it doesn’t automatically yield install-time verification artifacts for end users. Source: https://blog.rust-lang.org/inside-rust/2026/01/13/infrastructure-team-q4-2025-recap-and-q1-2026-plan/
- Rust ecosystem work on mirroring/verification highlights the need for stronger trust primitives, especially for constrained networks. Source: https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/

# Design goals
1) **Tool-agnostic**: usable standalone and embeddable by `cargo-binstall`-like installers.
2) **Explainable**: produce a machine-readable verification report *and* a human explanation.
3) **Policy-driven**: allow rules like “require signature”, “require provenance”, “only from these identities”, “block untrusted hosts”.
4) **Incremental adoption**: start with checksums + signed manifests; grow into provenance attestations.

# Non-goals
- Replacing `cargo-binstall` or `cargo-dist`.
- Building a new PKI. Prefer existing ecosystems (Sigstore-style) when needed.
- Solving every OS packaging channel (brew/apt) in v0.

# Proposed UX (CLI)
- `cargo binary-trust verify <artifact> --bundle <bundle_dir_or_file>`
- `cargo binary-trust fetch-and-verify <crate-or-url> --policy policy.toml`
- `cargo binary-trust explain <report.json>` (turns a report into a human-readable narrative)

# Bundle format (initial)
A versioned directory/tar layout:
- `manifest.toml` (schema version, artifact digests, provenance pointers)
- `SHA256SUMS` (or structured digests file)
- `signature` (optional, for the manifest)
- `provenance/…` (optional, opaque blobs)
- `sbom/…` (optional)

The crate should provide:
- `BundleWriter` to create bundles
- `BundleVerifier` to verify bundles
- `Policy` parser + evaluator

# Security model
- Verification never silently “falls back”. If a policy requires provenance, absence is a hard failure.
- Reports include *what was checked* and *what was not checked*.
- Support offline verification (bundle contains all required materials, or clearly states online dependencies).

# MVP (0.1)
- Bundle schema v0 + verifier library.
- CLI `verify` that checks digests + optional signed manifest.
- Policy v0: allowlist of hosts/owners, require-digests, optional signature required.
- Integration guide: “how `cargo-binstall` could call this verifier”.

# Milestones
0.2: provenance support (attestation file types + pluggable verifiers)  
0.3: installer integration prototype (feature branch or sidecar wrapper)  
0.4: org policy profiles + CI templates

# Open questions
- Where should identity come from first (GitHub release signing? Sigstore identity? future TUF roles)?
- How do we avoid fragmenting bundle formats across installers?
- What is the minimal provenance claim that is both useful and realistically adoptable?

# Adoption plan
- Ship as a library-first crate plus tiny CLI.
- Provide drop-in integration examples for `cargo-binstall`.
- Provide a “producer” guide that aligns with popular CI setups (and future `cargo-dist` outputs).
