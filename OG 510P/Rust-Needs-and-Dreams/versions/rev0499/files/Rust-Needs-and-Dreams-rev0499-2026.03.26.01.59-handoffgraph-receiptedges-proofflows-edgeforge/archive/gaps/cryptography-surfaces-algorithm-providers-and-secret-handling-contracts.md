# Gap: cryptography surfaces, algorithm/provider splits, secret handling, and compliance contracts

## What is missing
Rust now has **real cryptography diversity**, but the ecosystem still lacks a **portable way to describe what a cryptographic surface actually promises**.

Today there is no standard way to say:
- which algorithm families are really in play (digest, MAC, AEAD, signatures, key exchange, password hashing, KDFs, etc.),
- whether the implementation is pure Rust, FFI-backed, provider-swappable, or tied to one cryptographic backend,
- whether the crate is built around trait families, concrete algorithms, or a protocol/provider abstraction,
- how secret material is expected to be handled in memory: explicit exposure, zeroization-on-drop, serialization posture, and accidental-copy caveats,
- whether constant-time or side-channel resistance is claimed, and whether that claim is framed as best-effort, architecture-limited, audited, or not audited,
- whether compliance stories such as FIPS are in scope, what features/providers must be enabled, and whether run-time validation is required,
- what platform/build assumptions exist: `no_std`, heap requirements, C/C++ toolchains, bindgen, WebAssembly, target-specific entropy features, or provider-specific dependencies,
- how interoperable the surface is with RustCrypto trait families, `ring`-style APIs, `rustls` providers, password-hash PHC strings, remote signers, HSM/KMS adapters, or protocol consumers,
- and what evidence actually supports the surface: known-answer tests, cross-provider vectors, Wycheproof-style tests, audit notes, FIPS/runtime checks, side-channel caveats, or interop reports.

That gap matters because Rust already has meaningful point solutions:
- `rustls` now exposes a first-class `CryptoProvider` seam with built-in `aws-lc-rs` and `ring` providers,
- `aws-lc-rs` explicitly aims at `ring` compatibility while also exposing FIPS and build-environment posture,
- `ring` exposes target-specific randomness and platform feature caveats,
- RustCrypto trait crates (`digest`, `signature`, `aead`, `password-hash`, `elliptic-curve`, etc.) already make generic algorithm interop real, while the `crypto` facade crate exists specifically to keep trait-version compatibility sane,
- `zeroize`, `secrecy`, and `subtle` already cover different slices of secret-handling and side-channel posture,
- password-hash crates already orbit the PHC string format,
- and concrete algorithm crates can differ sharply in audit posture even when they share trait-level APIs.

So the missing contribution is not one magical crypto crate.
It is a **reviewable cryptography-surface layer** for publishing algorithm-family scope, provider/backend posture, secret-material handling, side-channel/audit/compliance truth, and evidence honestly.

Sources:
- https://docs.rs/rustls/latest/rustls/crypto/struct.CryptoProvider.html
- https://docs.rs/rustls/latest/rustls/manual/_06_fips/index.html
- https://docs.rs/aws-lc-rs/latest/aws_lc_rs/
- https://docs.rs/ring/latest/ring/
- https://docs.rs/crate/crypto/latest
- https://docs.rs/crate/digest/latest
- https://docs.rs/crate/signature/latest
- https://docs.rs/crate/aead/latest
- https://docs.rs/password-hash/latest/password_hash/struct.PasswordHash.html
- https://docs.rs/secrecy/latest/secrecy/
- https://docs.rs/zeroize/latest/zeroize/
- https://docs.rs/subtle/latest/subtle/
- https://docs.rs/p256/latest/p256/

## The current seam is awkward
Rust already spans several materially different cryptography lanes, but most of that truth is split across crate docs, feature flags, and folklore:
- `rustls` says it has two built-in crypto providers and that the implicit default provider is configured once per process, which means provider choice is already part of the public support surface rather than a hidden implementation detail,
- `rustls`’s FIPS docs say users must enable a crate feature, install the FIPS provider, and validate FIPS status at run time; that is strong evidence that compliance claims need explicit artifacts rather than a README badge,
- `aws-lc-rs` documents `ring` compatibility, FIPS and non-FIPS feature separation, C/C++ build requirements, and that it currently does not support `#![no_std]`,
- `ring` documents target-specific “less-safe” randomness features and a Web API feature for `wasm32-unknown-unknown`, which means platform posture is part of the crypto story,
- RustCrypto trait crates make algorithm-generic code real for digests, signatures, AEADs, password hashing, and elliptic-curve code, but the existence of the `crypto` facade crate is itself evidence that trait-version compatibility is still a real coordination problem,
- `secrecy` explicitly tries to limit accidental exposure and zeroize on drop, but also warns that serde input paths can still make extra copies,
- `zeroize` explicitly says it provides portable zeroing guarantees using stable Rust primitives, which is different from full secret-memory protection,
- `subtle` explicitly frames its constant-time story as best-effort and warns that side-channel resistance is not a property of software alone,
- concrete algorithm crates like `p256` can aim for constant-time behavior while also warning that they have not been independently audited,
- and the `signature` crate intentionally uses opaque errors to avoid side-channel leakage while still allowing external-signer/HSM/KMS transport errors as sources.

These are not small implementation details.
They determine compliance posture, build/toolchain cost, target support, interop, secret-handling guarantees, and what downstream reviewers can honestly trust.

Sources:
- https://docs.rs/rustls/latest/rustls/crypto/struct.CryptoProvider.html
- https://docs.rs/rustls/latest/rustls/manual/_06_fips/index.html
- https://docs.rs/aws-lc-rs/latest/aws_lc_rs/
- https://docs.rs/ring/latest/ring/
- https://docs.rs/crate/crypto/latest
- https://docs.rs/secrecy/latest/secrecy/
- https://docs.rs/zeroize/latest/zeroize/
- https://docs.rs/subtle/latest/subtle/
- https://docs.rs/p256/latest/p256/
- https://docs.rs/signature/latest/signature/struct.Error.html

## Why this matters
This gap matters because cryptography choices cut across several important Rust futures at once:
1. **transport and protocol stacks** — TLS and other protocol layers increasingly want provider selection, compliance posture, and backend-swappability to be explicit.
2. **secure application engineering** — secret handling, serialization of key material, constant-time comparisons, and opaque error posture are not optional details.
3. **regulated and enterprise environments** — FIPS or other compliance claims require sharper boundaries than “secure by default”.
4. **trait-based ecosystem composition** — RustCrypto’s trait families make generic crypto code practical, but trait compatibility and capability fit still need visible artifacts.
5. **build and portability decisions** — pure-Rust versus FFI-backed, `no_std` versus `std`, and WebAssembly/target support all influence adoption.
6. **review and archaeology** — audits, non-audits, best-effort side-channel notes, and cross-provider vector coverage need to survive version churn.

A worthy contribution here is therefore not another “best crypto crate” argument.
It is a way to treat cryptographic public support surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://docs.rs/rustls/latest/rustls/crypto/struct.CryptoProvider.html
- https://docs.rs/rustls/latest/rustls/manual/_06_fips/index.html
- https://docs.rs/crate/crypto/latest
- https://docs.rs/secrecy/latest/secrecy/
- https://docs.rs/zeroize/latest/zeroize/
- https://docs.rs/subtle/latest/subtle/
- https://docs.rs/password-hash/latest/password_hash/struct.PasswordHash.html
- https://docs.rs/signature/latest/signature/trait.RandomizedDigestSigner.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## What “good” looks like
A worthy contribution here is **not** one universal cryptography abstraction that erases meaningful differences.

It is a shared cryptography-surface boundary:
- one `crypto-surface/v0` describing the top-level surface identity, intended use, and whether the package is provider-first, algorithm-family-first, protocol-facing, secret-handling-first, or mixed,
- one `algorithm-family-profile/v0` for digest/MAC/AEAD/signature/KDF/password-hash/elliptic-curve/key-exchange families, parameterization posture, and randomness dependencies,
- one `provider-backend-profile/v0` for pure-Rust versus FFI, backend/provider identity, process-default/scoped selection, build requirements, platform assumptions, and target support,
- one `key-material-profile/v0` for secret exposure policy, zeroization posture, parsing/serialization posture, copy/clone caveats, and wrapper types,
- one `sidechannel-audit-profile/v0` for constant-time claims, opaque-error posture, architecture caveats, audit/review posture, and non-claims,
- one `compliance-certification-profile/v0` for FIPS or other compliance-relevant claims, required features/providers, covered environments, runtime-validation requirements, and out-of-scope conditions,
- one `crypto-adapter-profile/v0` for RustCrypto trait compatibility, `ring`-compat layers, `rustls` provider hooks, password-hash PHC interop, and remote-signer/HSM/KMS adapters,
- one `crypto-vector-set/v0` for known-answer tests, cross-provider vectors, interop vectors, error-surface checks, key-format roundtrips, and feature/target matrix runs,
- one `crypto-check-report/v0` recording which vectors actually ran on which targets/providers/channels,
- and one `crypto-pack/v0` bundle for docs, CI, audit notes, migration notes, and archaeology.

That would let Rust teams review “uses FIPS crypto”, “supports generic signatures”, “zeroizes secrets”, or “constant-time comparison” claims using explicit artifacts instead of guessing from README prose and scattered feature flags.

## Non-goals
This gap should not be used to:
- define all security or protocol soundness in Rust,
- replace `ring`, `aws-lc-rs`, RustCrypto trait crates, concrete algorithm crates, or secret-handling helpers,
- flatten pure-Rust, FFI-backed, provider-swappable, compliance-focused, and lightweight/no-std lanes into one fake universal model,
- or turn crypto choice into a shallow leaderboard or false blanket “safe” badge.

The job is smaller and sharper:
**make cryptography surfaces legible, honest, and checkable across algorithm families, provider/backend lanes, secret handling, audit/compliance posture, and evidence.**
