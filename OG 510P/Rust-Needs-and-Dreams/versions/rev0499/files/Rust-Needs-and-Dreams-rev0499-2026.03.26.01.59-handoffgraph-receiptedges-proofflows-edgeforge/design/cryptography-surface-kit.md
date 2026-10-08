# Design: Cryptography Surface Kit (`cargo cryptosurf`, `crypto-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **cryptography surfaces** in Rust: generic RustCrypto trait families, pure-Rust algorithm crates, FFI-backed providers, `rustls` crypto-provider selection, secret-handling wrappers, password-hash interchange, and compliance-sensitive provider lanes.

This should help answer questions like:
- which algorithm families are really exposed,
- whether the surface is generic-over-traits, concrete-over-one-backend, or provider-swappable,
- how key material and secrets are expected to be handled in memory and in transit,
- whether constant-time or opaque-error posture is claimed and with what caveats,
- whether audits or non-audits are declared,
- whether FIPS/compliance posture is real, conditional, or out of scope,
- what targets, toolchains, and build systems are required,
- and what evidence shows the claimed semantics are real.

It should **not** replace crypto crates, bless one backend, or force pure-Rust, FFI-backed, compliance-sensitive, and lightweight lanes into one common denominator.

## Why now
This seam has become strategically relevant because Rust now spans several real but poorly aligned cryptography shapes at once:
- `rustls` has a first-class `CryptoProvider` seam and defaults to `aws-lc-rs` while still supporting `ring`,
- compliance-sensitive users can now enable a FIPS-focused lane in `rustls`, but only with explicit provider and runtime-validation choices,
- `aws-lc-rs` deliberately targets `ring` compatibility while carrying FFI, build-toolchain, and compliance baggage that pure-Rust stacks do not,
- RustCrypto continues to grow an ecosystem of generic trait families, yet also needs a compatibility facade crate because independent trait versioning is itself a coordination burden,
- secret handling is already split across `zeroize`, `secrecy`, `subtle`, remote-signer abstractions, and concrete algorithm crates with varying audit and side-channel language,
- password-hash crates already orbit the PHC string format as an interoperability lane,
- and consumers increasingly need to compare “cryptographic capability” claims without reverse-engineering feature matrices and caveat paragraphs.

That is exactly the moment when a **cryptography-surface contract** becomes more valuable than one more algorithm crate or one more migration blog post.

## Design principles
1. **Do not lie about provider choice.** Pure-Rust, FFI-backed, and provider-swappable lanes are not the same story.
2. **Do not lie about secret handling.** Zeroization, secrecy wrappers, opaque errors, serialization posture, and side-channel notes are separate truths.
3. **Keep algorithm-family truth first-class.** Hashes, signatures, AEADs, KDFs, password hashes, and key exchange are not interchangeable “crypto support”.
4. **Keep compliance posture first-class.** “FIPS-capable”, “FIPS when configured this way”, and “not a compliance story” must remain visibly different.
5. **Keep evidence above folklore.** Known-answer tests, interop vectors, provider matrices, and audit notes matter more than README confidence.
6. **Prefer attachable artifacts over cargo-cult checklists.** Reviewable packs beat “we use crate X so we are secure”.
7. **Do not flatten the ecosystem.** `ring`, `aws-lc-rs`, RustCrypto traits, remote signers, secret wrappers, and protocol consumers should remain visibly different.

## Artifact family
The kit should revolve around a small family of portable artifacts.

### 1) `crypto-surface/v0`
Top-level description of the cryptography surface:
- package/crate identity,
- intended use cases (protocol/TLS, app crypto, password hashing, key management, generic libraries, compliance-sensitive deployments, etc.),
- major lanes exposed,
- whether the surface is algorithm-family-first, provider-first, protocol-first, or mixed,
- artifact versioning and links to checks.

### 2) `algorithm-family-profile/v0`
Describes the algorithm scope:
- digest / MAC / AEAD / cipher / KDF / signature / password hash / key exchange / curve families,
- parameterization posture,
- algorithm identifiers,
- required randomness or entropy dependencies,
- deterministic versus randomized operation notes,
- support for trait-object or generic consumption.

### 3) `provider-backend-profile/v0`
Describes backend/provider identity:
- pure-Rust versus FFI-backed implementation,
- provider name and provenance,
- process-global or scoped provider selection,
- default versus optional providers,
- build dependencies (C/C++ compiler, Go, bindgen, prebuilt objects, etc.),
- `std` / `alloc` / `no_std` posture,
- target and WebAssembly assumptions.

### 4) `key-material-profile/v0`
Describes secret-material handling:
- key/secret wrapper types,
- explicit exposure APIs,
- zeroize-on-drop or explicit wipe posture,
- copy/clone/serde caveats,
- parsing/serialization posture,
- password-hash or key-format interoperability,
- remote-key or HSM/KMS handling.

### 5) `sidechannel-audit-profile/v0`
Describes security-review posture:
- constant-time or best-effort constant-time claims,
- architecture/compiler caveats,
- opaque-error posture,
- audit/review status,
- explicit non-claims,
- debugging or development-build caveats,
- suitability notes for higher-level protocols.

### 6) `compliance-certification-profile/v0`
Describes compliance-sensitive claims:
- FIPS or other certification posture,
- required crate features/providers,
- covered environments and modules,
- runtime validation requirements,
- unsupported or out-of-scope configurations,
- pinning or version-lock recommendations.

### 7) `crypto-adapter-profile/v0`
Describes interop:
- RustCrypto trait compatibility,
- `ring`-compatibility layers,
- `rustls` provider hooks,
- PHC-string or key-format interop,
- remote-signer / HSM / KMS adapters,
- migration shims between providers or trait generations.

### 8) `crypto-vector-set/v0`
Executable checks covering claims such as:
- known-answer and reference-vector checks,
- cross-provider equivalence where meaningful,
- PHC / PEM / PKCS#8 / signature-format roundtrips,
- feature-target matrix checks,
- provider-selection and FIPS-mode checks,
- secret-handling and error-surface checks,
- release-to-release semantic diffs.

### 9) `crypto-check-report/v0`
Machine-readable results of running vectors:
- what ran,
- on which targets/providers/features,
- pass/fail/skip reasons,
- hashes or attachments for evidence,
- which claims remain unchecked.

### 10) `crypto-pack/v0`
Bundle containing the surface description, profiles, vectors, reports, audit notes, migration notes, and human-readable summaries.

## Tooling shape
A `cargo cryptosurf` command should be able to:
- scaffold the artifact family,
- inspect a workspace for likely crypto lanes,
- detect direct `ring`, `aws-lc-rs`, RustCrypto trait crates, secret wrappers, or password-hash usage,
- record provider/build-feature posture,
- run bounded known-answer / provider / feature-target / format-roundtrip vectors,
- diff support claims between releases,
- and export one portable `crypto-pack/v0`.

## Why this is better than today
Today, downstream users infer cryptographic behavior from vague phrases like “secure by default”, “constant-time”, “FIPS-ready”, “generic signature support”, or “zeroizes secrets”.
Those phrases hide the most important questions:
- which backend is actually in use,
- whether the backend is pure Rust or FFI,
- what compliance conditions must be satisfied,
- whether key material may be copied or serialized,
- whether side-channel claims are best-effort or audited,
- whether the crate is generic over trait families or locks callers into one implementation,
- and which checks were ever run.

Cryptography Surface Kit makes those questions first-class without forcing the ecosystem to converge on one backend or one trait family.

## Boundaries with nearby kits
- **Not Randomness Surface Kit:** randomness owns entropy-source and PRNG semantics; this kit owns higher-level cryptographic operations, providers, and secret-handling posture.
- **Not Protocol Surface Kit:** protocol owns wire interactions, ALPN, transport, and RPC posture; this kit owns cryptographic building blocks and provider/compliance truth.
- **Not Identity Surface Kit:** identity owns auth/session/access flows; this kit owns crypto primitives and key-material handling.
- **Not Encoding Surface Kit:** encoding owns serialization format posture broadly; this kit owns crypto-specific encodings and secret-material implications only insofar as they affect cryptographic public claims.
- **Not Validity Surface Kit:** validity owns layout and invalid-value assumptions; this kit owns side-channel, provider, audit, and compliance posture.
- **Not one crypto crate:** this kit records cryptography semantics and evidence; it does not define algorithms or replace existing implementations.

## Non-goals
- No attempt to define one universal crypto trait beyond the ecosystems that already exist.
- No attempt to replace `ring`, `aws-lc-rs`, RustCrypto trait crates, concrete algorithm crates, `rustls`, `secrecy`, `zeroize`, or `subtle`.
- No attempt to reduce cryptography choice to a benchmark chart, audit badge, or blanket security score.
- No attempt to imply that review artifacts themselves prove protocol or application security.

## MVP shape
The first practical MVP should target five lanes:
1. a provider-swappable protocol consumer (`rustls` with `CryptoProvider`),
2. one `ring`-style concrete backend lane,
3. one FFI-backed/provider-and-compliance lane (`aws-lc-rs`),
4. one RustCrypto generic-traits lane (`digest` + `signature` + `aead` or the `crypto` facade),
5. one secret-handling / password-hash lane (`secrecy`, `zeroize`, `password-hash`).

That MVP would already be enough to prove whether one reviewable artifact family can sit above today’s fragmented Rust cryptography ecosystem without flattening it.
