---
id: P-0063
title: Passkey Stack Kit — batteries-included WebAuthn/passkeys integration for Rust web backends
status: idea
domains: [security, web, auth]
last_reviewed: 2026-03-01
evidence:
  - https://crates.io/crates/webauthn-rs
  - https://crates.io/crates/passkey
  - https://ktaka.blog.ccmp.jp/2025/01/implementing-passkeys-authentication-in-rust-axum.html
needs:
  - “Protocol crates” exist, but teams need end-to-end flows and secure defaults.
  - Framework integration must be easy (Axum/Actix/Warp), or adoption stays niche.
risks:
  - Becoming a monolith that competes with underlying protocol crates.
  - Subtle security bugs from trying to abstract too much.
---

## Problem
Passkeys/WebAuthn are “ready” for mainstream use, but Rust teams still struggle to ship them:
- session + challenge storage is easy to get wrong,
- attestation policy and authenticator metadata are confusing,
- frontend/browser API wiring is repetitive,
- framework integration varies wildly.

There are strong protocol implementations (`webauthn-rs`, `passkey`), yet developers still write end-to-end implementations from scratch, indicating missing integration glue and secure defaults.

## Users & user stories
- **Web app**: “Add passkeys with a small, audited integration layer that doesn’t leak challenges or weaken origin checks.”
- **Enterprise**: “Enforce attestation rules and device policies, with an audit trail.”
- **SaaS multi-tenant**: “Support per-tenant RP IDs, origins, and migration from passwords.”

## Prior art (and why it’s insufficient)
- `webauthn-rs`: secure server-side WebAuthn implementation, but integration patterns vary by framework. https://crates.io/crates/webauthn-rs
- `passkey` / passkey-rs: comprehensive WebAuthn/CTAP2 components, but it’s a library set, not an opinionated end-to-end kit. https://crates.io/crates/passkey
- Blog posts still describe building the flows manually for Axum, showing the gap for batteries-included integration. https://ktaka.blog.ccmp.jp/2025/01/implementing-passkeys-authentication-in-rust-axum.html

## Design goals / non-goals
**Goals**
- Provide **secure defaults** and explicit escape hatches.
- Offer framework adapters: Axum first, then Actix.
- Provide reference frontend snippets (JS + optional wasm-bindgen helper) for register/auth flows.
- Make storage pluggable: in-memory (dev), Redis, SQL.

**Non-goals**
- Replacing protocol crates; the kit should wrap/adapt them.
- Being a full IAM product.

## Architecture & API sketch
Crate layout:
- `passkey-stack-core`: types, configuration, error model, policy.
- `passkey-stack-axum`: extractors/handlers, session/challenge storage adapters.
- `passkey-stack-ui`: tiny frontend helpers (optional).

Core API:
- `PasskeyService::begin_registration(user)` -> `PublicKeyCredentialCreationOptions`
- `PasskeyService::finish_registration(response)` -> `Credential`
- `begin_authentication` / `finish_authentication`

Policy:
- `AttestationPolicy` (none / indirect / direct + allowlists)
- `AuthenticatorHints` & metadata hooks

## Security / safety model
- Strong origin/RP ID validation; no implicit wildcards.
- Explicit, time-bounded challenge storage with one-time use.
- Rate-limit hooks and structured audit logs for auth attempts.
- Conservative defaults for resident keys / user verification.

## Maintenance & governance plan
- Security review checklist + fuzzing for parsing layers.
- Keep adapters thin; core logic centralized.
- Provide a “known-good” example app with tests.

## Milestones
**0.1**
- Core + Axum adapter + in-memory store + example app.
- Golden tests for register/auth with WebAuthn test vectors.

**0.2**
- Redis store + cookie/session integration helpers.
- Attestation policy basics + audit log hooks.

**1.0**
- Actix adapter + metadata integration + migration cookbook (password -> passkey).

## Open questions
- Best way to ship browser-side helpers without forcing a frontend stack?
- How to model multi-tenant RP IDs cleanly?

## Sources
- https://crates.io/crates/webauthn-rs
- https://crates.io/crates/passkey
- https://ktaka.blog.ccmp.jp/2025/01/implementing-passkeys-authentication-in-rust-axum.html
