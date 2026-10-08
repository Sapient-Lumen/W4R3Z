# Pilot program: Cryptography Productization Stack

## Goal
Exercise the smallest set of crypto-facing lanes that prove the archive’s proposed **Cryptography Productization Stack** is real and useful: provider/compliance truth, randomness and secret-material posture, runtime/key-source activation, and support/docs truth.

This pilot program should produce reusable artifacts and comparison notes.
It should not try to standardize all of cryptography.

## Pilot artifact families
- `crypto-surface/v0`
- `provider-backend-profile/v0`
- `key-material-profile/v0`
- `compliance-certification-profile/v0`
- `randomness-profile/v0`
- `crypto-check-plan/v0`
- `crypto-check-report/v0`
- `crypto-pack/v0`
- imported support/docs attachments from Support Envelope / DocProof

## Ranked pilot lanes

### Pilot 1: `rustls` provider-selection + runtime-validation lane
**Why first:**
It proves the narrowest serious lane with immediate downstream value.
It is enough to show that provider identity, process-default activation, runtime validation, and protocol attachment belong together.

**Candidate substrates:**
- `rustls` with default `aws-lc-rs`
- `rustls` with optional `ring`
- one custom-provider override or HSM-style key-loader example

**What to export:**
- crypto surface identity;
- provider lane and selection mode (per-process default vs explicit provider);
- runtime validation posture (`ClientConfig::fips()` / `ServerConfig::fips()` style checks where relevant);
- key-loading posture and custom-provider notes;
- checked handshake/config evidence.

**Success condition:**
A reviewer can tell exactly which provider was used, how it was selected, whether validation happened at runtime, and what downstream TLS/product claims are justified.

### Pilot 2: `aws-lc-rs` FIPS/non-FIPS build-and-pin lane
**Why second:**
It proves that compliance posture is not a badge but a materially different build, pinning, and support story.

**Candidate substrates:**
- `aws-lc-rs` default non-FIPS build
- `aws-lc-rs` FIPS build
- one pinned-version lane for teams tied to a previous validated module

**What to export:**
- FFI/provider identity;
- non-FIPS vs FIPS feature posture;
- build requirements and toolchain notes;
- module/version pinning posture;
- runtime/compliance caveats and checked evidence.

**Success condition:**
A reviewer can distinguish “compiled with crypto crate X” from “supports this compliance-sensitive provider/module/version story on these environments”.

### Pilot 3: RustCrypto generic-traits lane
**Why third:**
The ecosystem already has generic algorithm families, but their compatibility story is easy to handwave.
This pilot proves algorithm-family truth and facade compatibility are real product facts.

**Candidate substrates:**
- RustCrypto `crypto` facade
- `digest`, `aead`, `signature`, `password-hash` families
- one concrete algorithm implementation plugged through the trait lane

**What to export:**
- declared algorithm families;
- trait/facade compatibility posture;
- generic-vs-concrete support notes;
- unsupported-family or parameter notes;
- checked vector/interchange reports.

**Success condition:**
A reviewer can see what belongs to the generic cryptography contract and what belongs to one concrete implementation.

### Pilot 4: secret-handling / side-channel lane
**Why fourth:**
Real crypto products keep making claims like “secrets are wiped”, “comparison is constant-time”, or “errors are safe to expose”.
Those claims need explicit artifacts.

**Candidate substrates:**
- `secrecy`
- `zeroize`
- `subtle`
- `signature::Error`

**What to export:**
- wrapper/exposure posture;
- wipe-on-drop posture;
- best-effort constant-time or opaque-error posture;
- debug-build / serialization / copy caveats;
- checked or intentionally unchecked notes.

**Success condition:**
A reviewer can distinguish exposure policy, wipe policy, side-channel posture, and remote-signer error posture instead of hearing one vague “secure secret handling” story.

### Pilot 5: password-hash / remote-signer / downstream-consumer lane
**Why fifth:**
The stack matters only if other archive surfaces can import it honestly.
PHC-string and remote-signer lanes are also a good proof that crypto product surfaces are bigger than in-process primitives.

**Candidate substrates:**
- `password-hash`
- PHC-string-using crates like `argon2` or `scrypt`
- remote signer / HSM / KMS adapters via `signature`
- downstream protocol or identity consumers

**What to export:**
- PHC/interchange profiles;
- remote-key or external-signer posture;
- source-error vs crypto-error distinctions;
- one identity/protocol/service consumer import;
- one support/policy consumer import.

**Success condition:**
A consumer can reuse cryptography-productization facts without re-describing provider, key-source, secret-handling, or compliance truth.

## Comparison questions the pilots should answer
- Which facts are stable crypto-product facts versus provider-specific facts?
- Which compliance claims are compile-time, runtime-validated, environment-specific, or out of scope?
- Which key-material behaviors are public contract versus best-effort implementation detail?
- Which failures are crypto failures versus external-key/auth/I/O failures?
- Which docs/examples are checked support evidence versus illustrative material only?

## Early artifacts worth standardizing
- `crypto-surface/v0`
- `provider-backend-profile/v0`
- `key-material-profile/v0`
- `compliance-certification-profile/v0`
- `randomness-profile/v0`
- `crypto-check-report/v0`
- `crypto-pack/v0`

These are enough to prove the seam without freezing a giant schema too early.

## What this pilot program should resist
- becoming a new cryptography facade or primitive library;
- becoming a fake ecosystem security score;
- assuming provider choice is invisible plumbing;
- treating build-time feature selection as equivalent to runtime validation;
- calling tutorial snippets “support evidence” without checked reports.

## Recommended first implementation order
1. `rustls` provider-selection/runtime-validation lane
2. `aws-lc-rs` FIPS/non-FIPS build-and-pin lane
3. RustCrypto generic-traits lane
4. secret-handling/side-channel lane
5. password-hash/remote-signer/downstream-consumer lane

## Expected archive follow-ons
- Promote Cryptography Productization Stack in frontier and priority docs.
- Add cryptography-specific amnesia resistance language.
- Make future protocol, identity, service, client, and policy revisions import cryptography-productization facts instead of re-deriving them.
