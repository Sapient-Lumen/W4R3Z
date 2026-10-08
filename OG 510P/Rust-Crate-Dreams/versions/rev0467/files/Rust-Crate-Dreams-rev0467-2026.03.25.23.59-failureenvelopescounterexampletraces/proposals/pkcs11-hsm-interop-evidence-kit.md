---
id: P-0221
title: PKCS #11 / HSM Interop & Evidence Kit — token matrix, deterministic traces, and repro bundles
status: idea
domains: [security, crypto, hsm, pkcs11, interop, conformance, enterprise]
last_reviewed: 2026-03-05
evidence:
  - https://docs.oasis-open.org/pkcs11/pkcs11-spec/v3.2/pkcs11-spec-v3.2.pdf
  - https://docs.oasis-open.org/pkcs11/pkcs11-ug/v3.2/pkcs11-ug-v3.2.html
  - https://crates.io/crates/cryptoki
  - https://crates.io/crates/pkcs11
needs:
  - A practical way to ship PKCS#11 integrations that work across real HSMs/smartcards (vendor quirks, mechanism gaps, session semantics).
  - A shareable, redactable “this is what the token did” artifact for debugging support tickets and CI.
risks:
  - Hardware access is expensive and vendor SDKs vary; scope must be adapter-first and evidence-driven.
  - Security foot-guns (PIN handling, key material exposure) require strict redaction defaults.
---

## Problem
PKCS #11 is the interoperability layer for cryptographic tokens, but “works on my HSM” is not a plan. Teams need:
- a **token/driver capability matrix** they can trust,
- a way to **reproduce failures** without handing around secrets or vendor hardware,
- and **portable diagnostics** across OSes and vendor stacks.

## Who this helps
- Platform/security teams integrating HSMs for TLS keys, signing, code-signing, KMS bridges.
- Libraries/tools that want **PKCS#11 support** without becoming vendor-specific.
- CI pipelines for “crypto supply chain” systems that must prove *which token behaviors were exercised*.

## Prior art (insufficient)
- `cryptoki` / `pkcs11` give bindings/wrappers, but not a **conformance harness** or evidence bundles.
- Vendor test tools exist, but are rarely scriptable, comparable, or safe to share outside an org.

## Design goals
- **Evidence-first:** produce a `*.hsmtracebundle.zip` that is redactable by default.
- **Adapter architecture:** support many tokens via drivers/modules, and many test suites via runners.
- **Mechanism-level clarity:** explain “this token fails because mechanism X is absent / flags differ / key type constraints”.
- **CI-grade determinism:** stable canonical trace format and semantic diffs.

Non-goals:
- Being a full PKCS#11 provider.
- Shipping vendor SDKs.

## Architecture sketch
Workspace:
- `hsmkit-core` — canonical trace schema, redaction, diffing, “explain” engine.
- `hsmkit-pkcs11` — runner against a loaded PKCS#11 module (dlopen) + safe session orchestration.
- `hsmkit-suites` — test suites (mechanisms, objects, sessions, RNG, sign/verify, wrap/unwrap).
- `hsmkit-cli` — `probe`, `run`, `bundle`, `diff`, `explain`.
- `hsmkit-ci` — GitHub Actions helpers, matrix runner, artifact upload.

### Bundle format: `*.hsmtracebundle.zip`
- `manifest.json` (token make/model/firmware, module hash, OS, test profile)
- `capabilities.json` (mechanisms + flags, key sizes, curves, object classes)
- `traces/` (canonicalized call stream; hashed arguments; redacted sensitive inputs)
- `results/` (suite outcomes + normalized error taxonomy)
- `notes.md` (operator-entered context)

## Security model
- Default redaction for: PINs, private key handles, plaintext key material, plaintext messages unless explicitly allowed.
- Treat “handle IDs” as sensitive-ish (hash them) to prevent correlation attacks.
- Pluggable “policy profiles”: *support ticket*, *public issue*, *internal CI*.

## MVP (4–8 weeks)
1. `probe` token capabilities (mechanisms + flags + basic session invariants).
2. A small suite: sign/verify for RSA/ECDSA/EdDSA where supported; RNG sanity; object enumeration.
3. Bundle + diff between two tokens/modules.

## De-risk plan
- Start with software tokens (e.g., SoftHSM) for baseline, then add one physical HSM path via adapter.
- Build a “common failure dictionary” mapped to PKCS#11 error codes + observable invariants.

## Maintenance & governance
- Keep suite definitions stable; add new tests behind feature flags.
- Maintain a public “token matrix” only from **opt-in** submissions.

## Open questions
- Best canonical trace level: function-call level vs higher-level operations?
- How to standardize mechanism naming across PKCS#11 versions and vendor extensions?

## Sources
- OASIS PKCS #11 Specification v3.2 (and related artifacts).
- Existing Rust bindings/wrappers: `cryptoki`, `pkcs11`.
