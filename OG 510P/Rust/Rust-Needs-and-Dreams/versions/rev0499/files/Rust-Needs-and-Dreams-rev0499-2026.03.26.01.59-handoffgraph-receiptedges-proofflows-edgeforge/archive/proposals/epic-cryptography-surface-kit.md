# Epic proposal: Cryptography Surface Kit

## Thesis
One of the more worthy Rust ecosystem contributions now would be a **portable review layer for cryptography surfaces**.

Not another algorithm implementation.
Not another blanket “secure crypto” badge.
Not another migration blog post about which crate to pick.

The missing layer is a way to publish, diff, and verify:
- which algorithm families are actually exposed,
- which provider/backend is really in use,
- whether secret material is wrapped, zeroized, serialized, or explicitly exposed,
- what constant-time, audit, and opaque-error posture is claimed,
- whether compliance-sensitive stories such as FIPS are real and under what conditions,
- how trait-family interop and provider swapping work,
- and what evidence supports those claims.

That contribution would be unusually leveraged because it can serve TLS and transport libraries, identity/auth systems, password-hash stacks, application security work, HSM/KMS integrations, compliance-sensitive deployments, and generic RustCrypto-based libraries at once.

## Why this could be epic
Rust now has unusually broad cryptography diversity, but not yet a shared review layer.

At one end, RustCrypto keeps building generic trait families so crates can write code over digest, signature, AEAD, password-hash, and elliptic-curve abstractions rather than binding to one implementation. The `crypto` facade crate exists because those independently versioned trait families need coordinated compatibility.

At another end, protocol-facing stacks like `rustls` have made provider choice explicit with `CryptoProvider`, including a default `aws-lc-rs` provider and an optional `ring` provider. Compliance-sensitive users now have a distinct FIPS lane with both feature-selection and run-time validation consequences.

Meanwhile, secret-handling and review posture are visibly fragmented: `zeroize` handles wipe-on-drop semantics, `secrecy` handles explicit exposure and accidental-leakage minimization, `subtle` frames constant-time helpers as best-effort, and concrete algorithm crates can still warn that they have not been independently audited.

That is exactly the kind of ecosystem moment where a thin, portable artifact family can matter more than one more implementation crate.

## What the contribution would look like
The contribution should be a **Cryptography Surface Kit** built around:
- `crypto-surface/v0`
- `algorithm-family-profile/v0`
- `provider-backend-profile/v0`
- `key-material-profile/v0`
- `sidechannel-audit-profile/v0`
- `compliance-certification-profile/v0`
- `crypto-adapter-profile/v0`
- `crypto-vector-set/v0`
- `crypto-check-report/v0`
- `crypto-pack/v0`

Plus a `cargo cryptosurf` command that scaffolds, validates, diffs, and exports those artifacts.

## Why this matters in practice
This would make several currently-painful reviews much easier:
- “Can we swap `ring` for `aws-lc-rs` in this stack, and what changes in build/compliance posture?”
- “Does this crate really zeroize secrets, or just offer one optional helper?”
- “Is this signature/password-hash lane generic over trait families, or locked to one implementation?”
- “What exactly does the FIPS claim depend on?”
- “Are side-channel and audit claims strong, best-effort, or explicitly absent?”
- “Which target/provider/feature combinations were actually tested?”

Today those answers are scattered across docs, feature flags, CI, and folklore. A cryptography-surface pack would make them reviewable in one place.

## Why Rust is well-positioned
Rust is especially well-suited to pioneer this because:
- it already has a serious generic-traits culture through RustCrypto,
- it already has provider selection becoming first-class in real protocol stacks,
- it already has strong secret-handling point crates,
- and it already attracts both pure-Rust and compliance-sensitive FFI-backed cryptography users.

So Rust has both the fragmentation and the substrate needed for a shared review layer.

## What it should not become
This should not become:
- a centralized blessing mechanism for one backend,
- a fake universal “secure crypto” score,
- a replacement for audits,
- or a flattening of pure-Rust, FFI-backed, provider-swappable, and compliance-focused lanes.

The point is not to erase meaningful differences.
The point is to make them **visible, machine-readable, and reviewable**.

## MVP proposal
A strong MVP would cover:
1. `rustls` provider selection and FIPS posture,
2. `ring` and `aws-lc-rs` backend/build/compliance contrasts,
3. RustCrypto trait-family compatibility via the `crypto` facade,
4. secret-handling wrappers (`secrecy`, `zeroize`),
5. one password-hash / PHC-string lane,
6. one remote-signer/HSM/KMS adapter example through `signature`-style error posture.

If that MVP works, it would immediately improve reviews for a large slice of the Rust security ecosystem.

## Bottom line
A genuinely worthy Rust contribution here would be:

> **Cryptography Surface Kit** — one reviewable boundary for algorithm-family scope, provider/backend posture, key-material handling, side-channel/audit/compliance truth, and evidence across RustCrypto trait crates, pure-Rust algorithm crates, `ring`, `aws-lc-rs`, `rustls` provider selection, password-hash PHC lanes, and secret-handling helpers.

That would be “epic” not because it replaces today’s crypto projects, but because it could make the whole Rust cryptography story far easier to publish, compare, verify, and build on.
