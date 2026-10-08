# secrets-kit product plan — 2026-03-20

This note sharpens **P-0037 secrets-kit** into an implementation-ready `0.1` direction.

## Main judgment

A worthwhile `0.1` should **not** try to become:

- a new secret manager,
- a replacement for Vault / KMS / SOPS / keychains,
- or a generic privacy/redaction framework for all data.

It should instead become a **secret-handling contract layer** that helps a crate or app publish one reviewable answer to four boring but high-value questions:

1. **How is each secret actually revealed to the process?**
2. **What persistence posture does the backend really have?**
3. **What in-process memory posture is actually being claimed?**
4. **What export / serialization / logging posture is actually in force?**

The missing value is the contract layer above today’s wrappers, store adapters, and protected-memory primitives.

## Why this lane got stronger

Current Rust secret-handling substrate makes the gap more actionable than it used to be:

- `secrecy` now gives a crisp low-level contract around explicit access, debug redaction, and zeroize-on-drop — and also explicitly says it does **not** provide `mlock`/`mprotect`-style protection.
- `secrecy` is also explicit that deserializing secrets can introduce intermediate plaintext that callers must clean up themselves.
- `zeroize` now gives a clear and portable zeroization story, but equally clearly stops short of register clearing or broader memory-protection claims.
- `keyring` now gives a well-documented cross-platform store substrate with explicit feature gating, mock stores, and bring-your-own stores — which makes persistence posture and test substitution real review surfaces.
- `secrets` provides materially stronger protected-memory behavior, which makes “zeroize-only” versus “protected-memory” an honest boundary rather than a theoretical one.

That means the ecosystem no longer mainly lacks primitives.
It lacks a **shared product-shape** for publishing secret-handling support truth.

## What the crate should provide other people

For app teams, library authors, reviewers, and downstream adopters, the crate should provide:

1. **One revelation-path receipt** instead of guessing whether a secret passed through plaintext intermediates.
2. **One persistence-posture receipt** instead of conflating keychains, file envelopes, env vars, remote stores, and mocks.
3. **One memory-posture receipt** instead of flattening ordinary heap, zeroize-only wrappers, and protected memory into one fake “safe secret” claim.
4. **One export-posture report** instead of discovering late that `serde` or custom reveal helpers widened exfiltration risk.
5. **One compact contract-check report** that keeps imported substrate, observed adapters, declared policy, and manual-review zones visibly separate.

## Four first-class review objects

### 1. `revelation-path.receipt`

This artifact should answer:

- what source class supplied the secret,
- whether retrieval was direct or involved plaintext intermediates,
- whether decryption happened locally or remotely,
- whether the path is prod/dev/ci/test,
- and whether the claim is observed, imported, or declared.

### 2. `persistence-posture.receipt`

This artifact should answer:

- whether the backend is persistent, session-bound, ephemeral, mock-only, or externally managed,
- whether persistence lives in an OS secure store, file/envelope, process memory, or remote infrastructure,
- and whether the posture is conditional on target/feature/backend availability.

### 3. `memory-posture.receipt`

This artifact should answer:

- whether the runtime posture is `ordinary_heap`, `zeroize_only`, `protected_memory`, `hybrid`, or `manual_review_required`,
- whether zeroization is guaranteed,
- whether `mlock`/`mprotect`-class behavior exists,
- and whether copying back out to unprotected memory is still part of normal use.

### 4. `export-posture.report`

This artifact should answer:

- whether `Debug`/`Display` are redacted,
- whether `serde` serialization is disabled, opt-in, or effectively open through custom hooks,
- whether explicit reveal helpers exist,
- whether cloning is denied, best-effort prevented, or allowed,
- and which export paths are intentionally left open.

## Recommended `0.1` command surface

### `cargo secrets-contract capture`
Capture the declared/generated contract and emit:
- `revelation-path.receipt.json`
- `persistence-posture.receipt.json`
- `memory-posture.receipt.json`
- `export-posture.report.json`

### `cargo secrets-contract check`
Run conservative checks and emit:
- `secret-contract-check.report.json`

### `cargo secrets-contract diff`
Compare two contract bundles and emit:
- `secret-contract-diff.report.json`

### `cargo secrets-contract bundle`
Produce one compact `.secretcontractbundle.zip`.

## Workspace split

- `secret_contract_model`
- `secret_contract_capture`
- `secret_contract_keyring`
- `secret_contract_secrecy`
- `secret_contract_protected_memory`
- `cargo-secrets-contract`

## Discovery order

1. **Capture revelation path**
   - env / file / keystore / remote / mock
   - plaintext intermediates
   - local decrypt or remote reveal
2. **Capture persistence posture**
   - persistent / session / ephemeral / mock / external
3. **Capture memory posture**
   - ordinary heap / zeroize-only / protected memory / hybrid
4. **Capture export posture**
   - debug / display / serde / reveal helpers / clone posture
5. **Bundle and diff**
   - export one compact review bundle

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- `secrecy::SecretBox`
- `zeroize::Zeroize` / `Zeroizing`
- `keyring` store builders and mock builders
- protected-memory wrappers from `secrets`
- app/provider-chain configuration

### Do not flatten into one fake verdict
- “uses secrecy”
- “uses zeroize”
- “uses keyring”
- “uses protected memory”
- “supports secret handling”

Those are ingredients, not the contract.

## Preferred proving grounds

- a CLI with env-in-dev and keyring-in-prod sourcing,
- a desktop/mobile app with native-store persistence and mock-backed tests,
- a service that deserializes secret config into `SecretBox<T>` and needs to disclose plaintext intermediates,
- a crypto app that uses `secrets` and wants to prove it is stronger than zeroize-only posture.

## Non-goals

- not a new key-management product,
- not a generic PII/redaction system,
- not a side-channel-complete memory hardening framework,
- not an authorization policy engine for who may reveal which secret.
