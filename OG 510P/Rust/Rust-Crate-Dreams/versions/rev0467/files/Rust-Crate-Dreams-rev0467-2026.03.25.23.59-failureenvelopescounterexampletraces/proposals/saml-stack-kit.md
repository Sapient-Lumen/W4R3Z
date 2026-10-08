---
id: P-0070
title: saml-stack-kit — secure SAML2 SP/IdP building blocks + XML signature primitives
status: idea
domains: [identity, saml, xml, security, web]
last_reviewed: 2026-03-01
evidence:
  - https://crates.io/crates/samael
  - https://github.com/terminaloutcomes/saml-rs
  - https://users.rust-lang.org/t/xml-enveloped-signature/70040
  - https://crates.io/crates/samael/0.0.19
---
# Problem
SAML2 is still widely deployed in enterprise SSO, but implementing it safely requires correct XML parsing, canonicalization, signature verification, replay protection, and strict validation of assertion conditions. Rust has some SAML crates, but the ecosystem lacks a strongly opinionated “secure defaults” kit with a conformance suite and clear adapter layers for common web frameworks.

# Users & user stories
- **B2B SaaS developers** want to ship SAML SSO without writing XML signature code or adopting fragile defaults.
- **Identity platform developers** (IdP projects) want a reusable assertion/signature stack and test vectors.
- **Security reviewers** want strict parsing (no entity expansion), bounded processing, and deterministic validation behavior.

# Prior art (and why it’s insufficient)
- `samael` is a SAML2 crate, but its signing/verifying story depends on xmlsec bindings (via a modified `rust-xmlsec`) and has historically had limited testing surface. https://crates.io/crates/samael
- `saml-rs` exists and emphasizes strict parsing/crypto policy, but describes itself candidly as an evolving implementation focused on specific project needs. https://github.com/terminaloutcomes/saml-rs
- The Rust community repeatedly asks for XML signature guidance, reflecting a tooling gap for “secure XML signatures in Rust.” https://users.rust-lang.org/t/xml-enveloped-signature/70040

# Design goals
- **Secure XML substrate**: strict parsing defaults (reject DOCTYPE/DTD/entity expansion), bounded DOM depth, and explicit canonicalization.
- **XML Signature primitives**: canonicalization + digest + signature verification with a narrow, auditable API.
- **SAML validation correctness**: clock skew handling, audience/recipient checks, InResponseTo correlation, replay cache hooks.
- **Framework adapters**: axum/tower first (request extraction + session correlation helpers).
- **Conformance fixtures**: known-good and known-bad SAML responses, including signature wrapping attacks and expiry cases.

# Non-goals
- Full “everything SAML” (metadata exchange, all bindings, every encryption mode) in 0.x.
- A new XML library from scratch.

# Architecture & API sketch
## Crate layout
- `xmlsig-core` (reusable):
  - `Canonicalizer`
  - `SignatureVerifier`
  - `ReferenceResolver` (controls what can be signed)
- `saml-core`:
  - schema model for key SAML elements (Response, Assertion, Conditions)
  - `Validator` producing `ValidationReport { verdict, reasons }`
- `saml-stack-kit` (public facade + adapters):
  - `SpFlow` helpers (create AuthnRequest, verify Response)
  - `IdpFlow` helpers (issue assertions) in later milestone

## Example SP flow (sketch)
- `let req = SamlSp::new(cfg).authn_request();`
- `let resp = SamlSp::new(cfg).verify_http_post(form).await?;`
- `let attrs = resp.attributes();`

# Security / safety model
- Default to **strict parsing** and **explicit allowlists** (algorithms, signed elements, bindings).
- Provide hooks for **replay protection** and **clock policy**; do not hide these decisions.
- Guard against **signature wrapping** by constraining reference resolution and verifying signed element identity.

# Maintenance & governance plan
- Keep `xmlsig-core` small and heavily fixture-tested.
- Establish a public “interop matrix” (IdPs tested: Okta/AzureAD/etc.) without embedding proprietary data—record only behavioral notes.

# Milestones
- **0.1**: `xmlsig-core` + strict XML parsing wrapper + minimal SAML Response verification (HTTP-POST).
- **0.2**: Conditions validation (audience/recipient/notBefore/notOnOrAfter), replay cache trait, axum adapter.
- **0.3**: Metadata parsing + key rollover support + expanded fixture corpus.
- **0.4**: Optional encryption support (only if fixtures + threat model are ready).

# Open questions
- How to balance “pure Rust” vs “xmlsec bindings” while keeping audits feasible?
- What is the minimal acceptable binding set for practical SP integration (POST + Redirect)?

# Sources
- https://crates.io/crates/samael
- https://github.com/terminaloutcomes/saml-rs
- https://users.rust-lang.org/t/xml-enveloped-signature/70040
