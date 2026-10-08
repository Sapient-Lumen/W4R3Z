# Design: Cryptography Productization Stack (Cryptography Surface + Randomness Surface + Runtime Settings + Support Envelope)

## Goal
Turn Rust crypto-facing products into a **portable productization stack** instead of leaving each project to express its cryptographic story as a mix of primitive crates, provider defaults, key wrappers, init code, compliance caveats, and scattered support prose.

The stack should **not** replace `rustls`, `ring`, `aws-lc-rs`, RustCrypto traits, `secrecy`, `zeroize`, `subtle`, `password-hash`, HSM/KMS integrations, or future provider-specific innovation.
It should make them compose better and make supported cryptographic behavior reviewable.

## Why this note is needed now
Rust’s current crypto signals say the missing problem is no longer “can Rust do serious cryptography at all?”
They say the missing problem is **what a Rust crypto product can honestly claim to ship and support**:
- `rustls` now has a first-class `CryptoProvider` seam, two built-in provider lanes, process-default installation semantics, custom-provider escape hatches, and explicit custom key-loading examples. That means provider choice and key-loading posture are already public-support concerns.
- `rustls`’s FIPS guidance is explicit that feature selection is not enough: users must enable the `fips` feature, use the FIPS provider, and validate FIPS status at run time.
- `aws-lc-rs` is explicit that it is `ring`-compatible, FFI-backed, and that FIPS builds require materially different tooling (`CMake`, `Go`, and sometimes `bindgen`) than default non-FIPS builds.
- RustCrypto’s `crypto` facade exists specifically because independently versioned crypto-trait crates still need a compatibility layer. That is a strong sign that generic algorithm-family support is real, but not frictionless.
- `secrecy`, `zeroize`, and `subtle` already describe different truths: exposure policy, wipe policy, best-effort constant-time posture, and debug-build caveats.
- `signature::Error` is deliberately opaque to avoid side-channel leakage, while still allowing source errors for remote signers such as HSM/KMS integrations. That is exactly the kind of boundary a productization layer should preserve.
- `password-hash` and PHC strings show that some crypto-facing product surfaces are already interchange-heavy and parameter-rich rather than single-crate-internal.
- The 2025 State of Rust survey still says online docs are the canonical reference while LLM/editor workflows rise, and maintainer/developer support pressure remains visible. That is a strong reason to prefer portable evidence and support artifacts over more README archaeology.

Together, those signals argue that the next worthy contribution here is **not** another primitive crate, not another universal abstraction, and not a fake ecosystem security score.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Cryptography Surface: algorithm, provider, key-material, and compliance truth
Cryptography Surface owns the declared crypto-facing product boundary:
- algorithm-family scope,
- provider/backend identity,
- provider-swappable versus concrete lanes,
- key-material handling and exposure posture,
- side-channel/audit posture,
- compliance-sensitive claims,
- remote signer / HSM / KMS / PHC / key-format adapters,
- and checked vector/evidence attachments.

This layer answers questions like:
- “What cryptographic families are actually public here?”
- “Is this product pure-Rust, FFI-backed, provider-swappable, or provider-fixed?”
- “What does ‘FIPS’, ‘constant-time’, ‘zeroizes secrets’, or ‘HSM-backed’ mean here in practice?”

Design rule: **crypto truth must not remain an accidental byproduct of feature flags, proc initialization, or README warnings**.

### 2) Randomness Surface: entropy, seeding, and reproducibility posture
Crypto-facing products depend on randomness posture even when they do not own the RNG crate directly.
Randomness Surface owns:
- entropy-source posture,
- deterministic-test versus production-randomness lanes,
- target/backend RNG assumptions,
- seed/reproducibility boundaries,
- and imported randomness evidence.

This layer answers questions like:
- “Does this crypto product require OS entropy, remote entropy, deterministic test vectors, or custom RNG injection?”
- “Which behaviors are reproducible for tests, and which are intentionally not reproducible in production?”

Design rule: **entropy assumptions must not hide behind `thread_rng()` or “uses secure randomness by default” handwaving**.

### 3) Runtime Settings: provider selection, feature activation, key source, and runtime validation truth
Crypto products change materially through settings:
- provider choice and installation mode,
- feature-driven compliance or non-compliance posture,
- key/cert/token/source selection,
- secret location (env/file/HSM/KMS/remote service),
- dev/test/prod differences,
- and runtime validation or health-check posture.

This layer answers questions like:
- “Which provider was actually selected?”
- “Was FIPS merely compiled in, or validated at runtime?”
- “Are keys local, file-backed, remote-signer-backed, or process-external?”

Design rule: **activation posture is product truth, not launcher trivia**.

### 4) Support Envelope + DocProof: what is actually promised
Support Envelope and DocProof together own:
- supported target/runtime/toolchain floors,
- supported provider/feature combinations,
- supported compliance-sensitive environments,
- supported secret/key-management lanes,
- docs/examples/tutorial truth,
- and release/support-facing claims.

This layer answers questions like:
- “Which provider/target/compliance combinations are actually supported versus merely possible?”
- “Do docs reflect real provider-installation, HSM, PHC, and FIPS/runtime-validation behavior?”
- “What can support, security review, and release teams safely promise?”

Design rule: **one working example is not a support contract**.

### 5) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **protocol** consumers can attach TLS/provider/compliance facts without redefining them;
- **identity** consumers can import password-hash, signer, and secret-material truths without making new cryptography claims;
- **service/client/web/polyglot** consumers can import key-source/provider/support posture instead of re-expressing them as product folklore;
- **policy/support/release** consumers can distinguish algorithm/provider/support/compliance truth from vague “secure” language.

Design rule: **consumers import selected cryptography-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust crypto abstraction.”
It is a portable boring stack with clear boundaries:

1. **provider and compliance truth first**
   - prove stable product identity, provider identity, FIPS/non-FIPS posture, runtime validation posture, and key-source posture on one serious lane;
2. **generic algorithm-family truth second**
   - prove RustCrypto-trait/facade lanes can be described honestly without flattening them into one magical backend-free story;
3. **secret-material and side-channel truth third**
   - prove wrapper, wipe, exposure, opaque-error, and best-effort constant-time posture can be attached explicitly;
4. **interchange and remote-signer truth fourth**
   - prove PHC strings, key/cert formats, and HSM/KMS/remote-signer lanes can be described without pretending they are local in-process keys;
5. **consumer imports fifth**
   - prove protocol, identity, service, policy, and support consumers can reuse the same facts instead of re-deriving them.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases provider truth, randomness truth, activation truth, and support truth.

## Ranked first execution lanes
1. **`rustls` provider-selection + runtime-validation lane**
   - best first exporter because it proves provider identity, process-default activation, runtime validation, and downstream protocol attachment all at once.
2. **`aws-lc-rs` FIPS/non-FIPS build-and-pin lane**
   - proves build/toolchain and compliance posture are materially different product truths.
3. **RustCrypto generic-traits lane**
   - proves algorithm-family truth and cross-trait compatibility need first-class treatment rather than crate-by-crate guesswork.
4. **secret-handling / side-channel lane**
   - proves exposure/wipe/constant-time/opaque-error claims need explicit product artifacts.
5. **password-hash / remote-signer / downstream-consumer lane**
   - proves interchange and external-key lanes can be imported by identity/service/policy consumers honestly.

## Non-goals
- one universal Rust cryptography facade that erases meaningful differences;
- one backend winner or compliance badge to rule them all;
- replacing protocol, identity, or policy work with crypto-only metadata;
- flattening primitive, provider, secret-handling, randomness, and support truth into one fake “secure by default” blob.

## Archive implications
- The archive should now treat **Cryptography Surface + Randomness Surface + Runtime Settings + Support Envelope** as a coupled **Cryptography Productization Stack** in frontier discussions.
- Future revisions should prefer **provider/compliance truth, randomness posture, runtime/key-source activation, and support/docs truth** over another primitive crate debate, wrapper crate, or ecosystem-wide “best crypto” recommendation.
- When Protocol, Identity, Service, Client, Web, Release, or Policy work touches cryptographic support, it should import cryptography-productization facts rather than re-explain provider/key/compliance posture from scratch.

## Read this together with
- `design/cryptography-surface-kit.md`
- `design/randomness-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `design/identity-productization-stack.md`
- `design/protocol-productization-stack.md`

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `rustls` CryptoProvider:
  https://docs.rs/rustls/latest/rustls/crypto/struct.CryptoProvider.html
- `rustls` FIPS guide:
  https://docs.rs/rustls/latest/rustls/manual/_06_fips/index.html
- `aws-lc-rs`:
  https://docs.rs/aws-lc-rs/latest/aws_lc_rs/
- `aws-lc-rs` crate page / build notes:
  https://docs.rs/crate/aws-lc-rs/latest
- RustCrypto `crypto` facade:
  https://docs.rs/crate/crypto/latest
- `secrecy`:
  https://docs.rs/secrecy/latest/secrecy/
- `zeroize`:
  https://docs.rs/zeroize/latest/zeroize/
- `subtle`:
  https://docs.rs/subtle/latest/subtle/
- `signature::Error`:
  https://docs.rs/signature/latest/signature/struct.Error.html
- `password-hash`:
  https://docs.rs/password-hash/latest/password_hash/
