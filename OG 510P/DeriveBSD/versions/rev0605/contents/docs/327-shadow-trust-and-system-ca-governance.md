# Shadow trust and system CA governance (preventing “apps ship their own roots”)

DeriveBSD wants trust roots to be **versioned, auditable artifacts** (see `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`).
A common failure mode in real fleets is **shadow trust**:
applications silently ship their own CA bundle(s) or private trust DBs, bypassing fleet policy.

Greenfield advantage: bake in countermeasures early.
The product-default answer for how hard we push these countermeasures in A/B/C/D now lives in `docs/480-trust-bundle-posture-by-profile.md`.

## Why this matters

If different libraries trust different roots, you lose:
- consistent incident response (“what roots were trusted?”)
- revocation/blacklist effectiveness
- fleet-wide TLS posture guarantees

It also creates a downgrade channel: an app can keep trusting a compromised root even after the fleet removes it.

## Prior art: a unified trust store adapter (p11-kit)

Many Linux systems unify system trust via **p11-kit’s trust module**:
- a PKCS#11 module exposing system trust and policy as a shared interface
  - https://p11-glue.github.io/p11-glue/trust-module.html
- tooling to extract/maintain consolidated stores (e.g., `update-ca-trust`)
  - https://man.archlinux.org/man/update-ca-trust.8

This pattern is attractive for DeriveBSD because it:
- separates *source of truth* from *interop renderers*
- gives a single place to audit and gate trust changes

## DeriveBSD proposal

### 1) Trust bundle is an artifact (source of truth)

- `trust.bundle` is produced by the Derive pipeline (channel/policy controlled).
- It is stored in the CAS and referenced from the host generation.
- Renderers derive:
  - OpenSSL-style PEM bundle
  - hashed cert dir
  - optional PKCS#11 trust module view (p11-kit-shaped)
  - optional NSS shared DB outputs

### 2) A “trust portal” for workloads

Workloads should not read trust roots from arbitrary files by default.
Instead, provide a small **trust portal** API:

- request: “give me a verification context for purpose X”
- response: a handle to the correct trust material (or a denial)

This keeps purpose scoping possible (e.g., stricter roots for update channels).

### 3) Policy: block shadow trust in official channels

Add an optional gate:

- scan closures/artifacts for known “embedded trust store” patterns
  - `ca-bundle.crt`, `cacert.pem`, `cert.pem`, `certifi` bundles, `cert9.db`/`cert8.db`, `key4.db`/`key3.db`, etc.
- if found:
  - fail promotion for official channels OR
  - require an explicit waiver with justification

### 4) Runtime containment for third-party binaries

For “foreign” apps where you can’t patch easily:

- use mount views to **mask common bundle locations** (deny-by-default)
- provide compatibility shims:
  - set `SSL_CERT_FILE` / `SSL_CERT_DIR` (where applicable)
  - provide an NSS module path or shared DB adapter if the stack supports it

Do not pretend this is perfect: some apps will still ship bespoke trust logic.
The goal is to make bypasses **detectable and reviewable**.

## Evidence objects (optional)

If we want this to be explainable and exportable:

- a rendered trust-bundle receipt — which bundle was rendered for this generation
- a shadow-trust scan report — scan findings for an artifact closure (counts + digests + paths)
- a signed waiver object — references the findings when shadow-trust exceptions are explicitly approved

These objects should be small; do not dump raw certs into receipts by default.

The official system-trust answer for “what view should have been active here?” is now the canonical `pki-trust-bundle` plus the joined `pki.trust.bundle.apply.receipt`, not whichever local renderer/distributor API happened to expose a file or module.

## Operational advice

- Prefer linking TLS stacks to a single system trust interface.
- Prefer purpose-scoped roots for high-risk operations (update verification, publisher auth).
- Keep the trust bundle lifecycle in the same PR/review path as other high-impact policy.

Last updated: 2026-03-21r352
