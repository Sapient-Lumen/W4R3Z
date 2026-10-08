---
id: P-0037
title: secrets-kit — secret-handling contract kit for revelation path, persistence posture, memory posture, and export posture
status: idea
domains: [security, secrets, configuration, application, devtools]
last_reviewed: 2026-03-20
evidence:
  - https://docs.rs/secrecy/latest/secrecy/
  - https://docs.rs/zeroize/latest/zeroize/
  - https://docs.rs/keyring/latest/keyring/
  - https://docs.rs/secrets/latest/secrets/
---

# Problem

Rust now has meaningful secret-handling substrate, but ordinary teams still lack one boring, reviewable answer to what their application is **actually promising** when it says “we handle secrets safely”.

Current crates already cover real slices:

- `secrecy` makes secret access explicit, redacts `Debug`, and zeroizes on drop, but it is also explicit that it does **not** provide `mlock(2)` / `mprotect(2)`-style memory protection and that deserialization can introduce intermediate plaintext that callers must clean up themselves.
- `zeroize` gives stable, portable zeroization guarantees, but it is equally explicit that it is **only** about reliably zeroing memory and not about registers, `mlock`, `mprotect`, or broader storage/runtime policy.
- `keyring` gives a real cross-platform secure-store substrate with platform-specific stores, explicit feature gating, bring-your-own credential stores, and a platform-independent mock store with **no persistence**.
- `secrets` offers materially stronger in-process memory protection with guard pages, `mprotect`, `mlock`, zero-on-drop, and borrow-gated access, but that is still only one part of the app-level story.

That leaves real teams stuck answering high-value questions by folklore:

- did this secret come from a process environment string, a decrypted file, an OS secure store, a network fetch, or a test-only mock?
- was it ever materialized as an ordinary `String` / `Vec<u8>` before being wrapped?
- is the runtime promise merely “zeroize on drop”, or is there stronger protected-memory posture?
- does test mode silently switch to a mock or non-persistent backend?
- do `Debug`, logging, and `serde` still refuse to export secrets by default, or did the app opt into serialization / explicit reveal hooks?

So the missing crate is no longer best described as just “a provider chain plus typed secrets”.

The missing crate is better described as a **secret-handling contract kit**: a small Rust crate and cargo tool that lets an app publish one honest, reviewable support bundle for how secrets are sourced, materialized, persisted, protected in memory, and exposed back out.

# What it provides

- `secret-profile.toml` — declares source policy, backend classes, export policy, and whether mock/test backends are permitted.
- `revelation-path.receipt.json` — how each secret class is sourced and what plaintext/intermediate materialization steps are part of that path.
- `persistence-posture.receipt.json` — whether each backend is persistent, session-bound, mock-only, in-memory, file-backed, OS-store-backed, or externally managed.
- `memory-posture.receipt.json` — whether the runtime uses ordinary heap values, `zeroize`/`secrecy`-style zeroize-on-drop wrappers, or protected-memory mechanisms such as `mlock` / `mprotect`.
- `export-posture.report.json` — whether `Debug`, `Display`, `serde`, cloning, and explicit reveal methods are allowed, denied, or manual-review-only.
- `secret-contract-check.report.json` — compact warnings when an app claims stronger secret posture than the imported substrate supports.
- `cargo secrets-contract capture` — inspect configured secret paths and emit one contract bundle.
- `cargo secrets-contract check` — run conservative checks on persistence, memory posture, and export posture.
- `cargo secrets-contract diff <old> <new>` — compare contract drift across app versions or environment profiles.
- `*.secretcontractbundle.zip` — portable support/review artifact.

# What the crate should provide other people

1. **One revelation-path receipt** instead of guessing whether “uses `secrecy`” hides ordinary `String` intermediates.
2. **One persistence-posture receipt** instead of conflating a native keychain/backend with a mock store or a plain env var.
3. **One memory-posture receipt** instead of flattening zeroize-on-drop, protected memory, and ordinary heap residency into one fake “secret-safe” claim.
4. **One export-posture report** instead of discovering too late that `serde` or custom reveal helpers made exfiltration possible.
5. **One compact contract-check report** that keeps imported substrate, declared app policy, observed adapters, and manual-review-only zones visibly separate.

# Main review objects

## 1. `revelation-path.receipt`

This artifact should answer:

- which backend class supplied the secret (`env`, `file`, `keyring`, `network`, `k8s`, `vault`, `mock`, `manual`, `other`),
- whether retrieval was direct or passed through intermediate plaintext objects,
- whether decryption happened locally, remotely, or not at all,
- whether the receipt was observed directly, imported from configuration, or declared manually,
- and whether the path is production, development, CI, or test only.

## 2. `persistence-posture.receipt`

This artifact should answer:

- whether the secret is persistent, session-bound, ephemeral, mock-only, or externally managed,
- whether persistence is in a platform store, a file/envelope, process memory only, or remote infrastructure,
- whether persistence support is guaranteed on the current target or conditional on feature flags,
- and whether a test/mock backend is substituting for a production store.

## 3. `memory-posture.receipt`

This artifact should answer:

- whether in-process handling is `ordinary_heap`, `zeroize_only`, `protected_memory`, `hybrid`, or `manual_review_required`,
- whether zeroization on drop is guaranteed by imported substrate,
- whether protected-memory mechanisms such as `mlock`/`mprotect` are in play,
- whether the value may be copied out into unprotected memory during normal use,
- and whether the claim is directly witnessed or inferred from wrapper types.

## 4. `export-posture.report`

This artifact should answer:

- whether `Debug`/`Display` are redacted, denied, or manual-review-required,
- whether `serde` serialization is disabled by default, explicitly opted into, or inferred via wrapper escapes,
- whether explicit reveal helpers are public and what audience they are intended for,
- whether cloning is denied, best-effort prevented, or allowed,
- and which exfiltration paths remain intentionally open.

# Why this is still missing

The ecosystem has ingredients, but not this compact receiver-facing support contract:

- `secrecy` is good at **explicit access + redaction + zeroization**, but does not claim protected memory and warns about intermediate plaintext during deserialization.
- `zeroize` is good at **portable wipe semantics**, but explicitly stops short of broader memory-protection guarantees.
- `keyring` is good at **secure-store adapters + mock/test substrate**, but does not answer the app-level question of what contract the app is publishing across production, CI, dev, and tests.
- `secrets` is good at **strong in-process memory protection**, but does not solve multi-backend source policy, persistence classification, or export-surface reporting.

That means another team can still see “we use keyring + secrecy” and remain unable to tell:

- whether production uses a native store but tests use a mock,
- whether values were first read into a plain environment string,
- whether a secret is only zeroized or actually memory-protected,
- whether serialization was deliberately re-enabled,
- or whether a support bundle is describing a live app path or merely a declared policy.

# Recommended `0.1` scope

## Commands

### `cargo secrets-contract capture`
Emit:
- `revelation-path.receipt.json`
- `persistence-posture.receipt.json`
- `memory-posture.receipt.json`
- `export-posture.report.json`

### `cargo secrets-contract check`
Emit:
- `secret-contract-check.report.json`

### `cargo secrets-contract diff`
Emit:
- `secret-contract-diff.report.json`

### `cargo secrets-contract bundle`
Produce one `.secretcontractbundle.zip`.

## Workspace split

- `secret_contract_model`
- `secret_contract_capture`
- `secret_contract_keyring`
- `secret_contract_secrecy`
- `secret_contract_protected_memory`
- `cargo-secrets-contract`

# Discovery order

1. **Capture revelation path**
   - env / file / keystore / remote / mock source class
   - local decrypt or remote fetch details
   - ordinary plaintext intermediates versus direct protected import
2. **Capture persistence posture**
   - persistent vs session-bound vs ephemeral vs mock
   - platform-store / file / remote / in-memory classification
3. **Capture memory posture**
   - ordinary heap vs zeroize-only vs protected memory
   - wrapper/witness basis
4. **Capture export posture**
   - debug/display
   - serde behavior
   - reveal helpers and clone posture
5. **Check and bundle**
   - emit warnings for overclaimed safety
   - export one compact contract bundle

# What to import from substrate, and what not to flatten

## Import, but do not flatten
- `secrecy::SecretBox` and `ExposeSecret`
- `zeroize::Zeroize` and `Zeroizing`
- `keyring` platform stores, credential builders, and mock builders
- protected-memory wrappers from `secrets`
- provider-chain / config-layer adapters from app code or optional glue crates

## Do not flatten into one fake verdict
- “uses `secrecy`”
- “uses `zeroize`”
- “uses keychain / keyring”
- “uses protected memory”
- “supports secret management”

Those are ingredients, not the contract.

# Preferred proving grounds

- a CLI that reads an API token from env in dev and a native keyring in prod,
- a desktop/mobile app with keyring-backed persistence and mock-backed tests,
- a service that deserializes secret config into `SecretBox<T>` and needs to disclose plaintext intermediates,
- a crypto app that uses `secrets` for protected memory and wants to prove it is stronger than zeroize-only handling.

# Non-goals

- Not a new secrets manager.
- Not a replacement for Vault, KMS, keychains, SOPS, or K8s secret systems.
- Not a generic PII redaction framework for all telemetry.
- Not a promise of perfect in-process secrecy or side-channel resistance.
- Not a full policy DSL for secret authorization.

# Architecture & API sketch

```rust
pub enum SourceClass {
    Env,
    File,
    Keyring,
    Remote,
    Mock,
    Other(String),
}

pub enum MemoryPosture {
    OrdinaryHeap,
    ZeroizeOnly,
    ProtectedMemory,
    Hybrid,
    ManualReviewRequired,
}

pub fn capture_secret_contract(root: &Path) -> Result<SecretContractBundle>;
pub fn classify_revelation_paths(bundle: &SecretContractBundle) -> Vec<RevelationPathReceipt>;
pub fn classify_persistence_posture(bundle: &SecretContractBundle) -> Vec<PersistencePostureReceipt>;
pub fn classify_memory_posture(bundle: &SecretContractBundle) -> Vec<MemoryPostureReceipt>;
pub fn classify_export_posture(bundle: &SecretContractBundle) -> ExportPostureReport;
pub fn diff_secret_contracts(old: &SecretContractBundle, new: &SecretContractBundle) -> SecretContractDiff;
```

Bundle draft: `secret-profile.toml`, `revelation-path.receipt.json`, `persistence-posture.receipt.json`, `memory-posture.receipt.json`, `export-posture.report.json`, `secret-contract-check.report.json`, `notes.md`.

# Security / safety model

- Treat declared paths as weaker than directly observed paths.
- Never claim `protected_memory` when imported substrate only guarantees zeroization.
- Never claim `persistent_native_store` when tests or unsupported platforms silently fall back to mock or in-memory behavior.
- Never claim export safety if `SerializableSecret`, custom serializers, or explicit reveal helpers widen the export surface.
- Preserve enough metadata to explain support truth without exporting raw secret values.

# Maintenance & governance plan

- Track `secrecy`, `zeroize`, `keyring`, and protected-memory crates for posture changes.
- Keep schemas compact and versioned.
- Maintain fixtures for env/materialization surprises, keyring/mock substitution, protected-memory upgrades, and serialization opt-ins.
- Prefer conservative claims and fail closed when direct evidence is missing.

# Milestones

## 0.1
- revelation-path receipts
- persistence-posture receipts
- memory-posture receipts
- export-posture reports
- conservative contract checks

## 0.2
- keyring adapter
- `secrecy` / `zeroize` adapter
- protected-memory adapter
- diff support

## 1.0
- multi-profile support (dev / ci / prod / test)
- richer bundle summaries
- stronger import hooks for common config/provider stacks
