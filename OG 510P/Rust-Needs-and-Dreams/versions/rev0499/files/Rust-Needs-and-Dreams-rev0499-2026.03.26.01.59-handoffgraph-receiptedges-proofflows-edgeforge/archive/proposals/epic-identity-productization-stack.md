# Epic proposal: Identity Productization Stack (`cargo identity-product`, `identity-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **identity-enabled products** that links **supported-auth and principal truth**, **protected-surface requirements**, **provider/session/cookie/key activation**, **authorization-engine attachments**, **support/docs/platform truth**, and **migration evidence** into one portable review boundary without pretending sessions, OIDC/OAuth2, passkeys, API keys, and policy engines have already converged into one framework.

## Why this is now worth doing
Rust’s identity story is real, but it is still spread across non-equivalent lanes:
- The 2024 State of Rust survey says Rust is especially popular for **server backends, web and networking services, and cloud technologies**, and also says employers value Rust for helping them build relatively correct and bug-free software. That makes authentication and authorization part of the practical product boundary, not just framework glue.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference while debugging/resource friction stays real and some learning traffic appears to be shifting toward LLM tooling. That increases the value of machine-readable, supportable identity truth instead of README folklore and issue-thread archaeology.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- AreWeWebYet’s auth topic is still a mixed crate catalog rather than a shared support model. That is exactly the shape of ecosystem evidence that says “the higher product contract is still missing.”
  https://www.arewewebyet.org/topics/
- The session/auth lane is already substantial: `tower-sessions` explicitly offers pluggable storage backends and minimal-overhead middleware placement, while `axum-login` explicitly provides identification, authentication, authorization, route protection, and custom backend support on top of `tower-sessions`.
  https://docs.rs/tower-sessions/latest/tower_sessions/
  https://docs.rs/axum-login
- Federation and provider-driven auth are also serious lanes: `oauth2` documents Authorization Code + PKCE as the common flow and points users toward `openidconnect` for authentication; `openidconnect` provides extensible strongly typed interfaces, discovery, ID token handling, and both blocking and async client modes.
  https://docs.rs/oauth2/latest/oauth2/
  https://docs.rs/openidconnect
- Passkeys/WebAuthn are no longer hypothetical, but they remain operationally nuanced: `webauthn-rs` explicitly treats different passkey definitions as carrying different usability implications and says some usernameless flows are not yet enabled because platform/browser UX is not good enough.
  https://docs.rs/webauthn-rs/latest/webauthn_rs/
- The authorization layer is clearly plural rather than solved by one engine: `cedar-policy` frames authorization as principal/action/resource/context policy evaluation, `oso` is an embedded declarative authorization engine, and `casbin` centers an `Enforcer` for authorization enforcement and policy management.
  https://docs.rs/cedar-policy
  https://docs.rs/oso/
  https://docs.rs/casbin/
- Cookie/header activation details are already real support surfaces: `axum-extra` exposes signed and private cookie jars plus the underlying cryptographic `Key`, and `tower-http` exposes Authorization-header middleware lanes.
  https://docs.rs/axum-extra/latest/axum_extra/extract/cookie/
  https://docs.rs/tower-http/latest/tower_http/auth/index.html

What is still missing is the **stack-level boundary that says one identity-enabled product subject was reviewed with these supported auth methods, these principal models, these protected surfaces, these activated providers/secrets/cookies, these authorization attachments, these support caveats, and this bounded handoff to consumers**.

## Working name
- CLI: `cargo identity-product`
- primary artifact: `identity-product-pack/v0`

## Scope
### This epic should own
- identity-product subject identity
- imported identity-surface / runtime-settings / credentials / support attachments
- imported protected-surface maps and authorization-engine references
- diffable review points across auth methods, principal schema, provider posture, cookie/session/token posture, and docs/support claims
- bounded release / support / policy / schema / client / atlas / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- a universal auth framework
- a hosted identity-control plane
- a universal JWT/session abstraction
- one policy engine to replace Cedar/Oso/Casbin and similar tools
- redefining route schemas or client-app policy as the identity source of truth
- a one-number "secure auth" badge

## Candidate artifact family
### `identity-product-brief/v0`
Why the product exists, intended consumer set, identity lanes in scope, supported environments, freshness budget, and review status.

### `identity-product-subject/v0`
The exact product/build/release subject, deployment or profile identity, imported identity surface(s), comparison base, and environment/support scope.

### `identity-product-pack/v0`
The portable review bundle linking:
- imported `identity-surface` / `principal-claims-schema` / `access-requirements-map` attachments
- imported runtime-settings / credentials / cookie-key / session-store / provider metadata attachments
- imported auth-check / denial / transition evidence
- imported support/docs/platform and optional release handoffs
- local notes, waivers, and caveats
- integrity metadata

### `identity-product-diff/v0`
What changed between two review points, with separate sections for:
- supported auth methods
- principal/claim schema
- protected-surface requirements
- provider/session/cookie/token activation posture
- authorization backend references
- support/docs/platform claims
- migration requirements and user/operator actions

### `identity-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support review
- policy/security review
- schema/client/import consumers
- atlas/adoption review
- assistant/editor rendering

## Recommended rollout
1. supported-auth + principal lane
2. protected-surface attachment lane
3. provider / cookie / session / key activation lane
4. docs / support / browser-runtime behavior lane
5. transition / release / policy / incident handoff lane

This should be driven by [`design/identity-productization-pilot-program.md`](../design/identity-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer session middleware,
- a nicer JWT helper,
- a nicer OIDC client wrapper,
- a nicer passkey onboarding crate,
- or a nicer policy-engine adapter.

An epic contribution here instead gives Rust one **portable identity-product contract** above those lanes.
That is strategically different because it can:
- make release/support/policy/schema/client reviews share the same subject and evidence boundary;
- let session, federation, passkey, cookie, and authorization engines stay specialized without pretending any one defines the whole product;
- keep supported auth methods, principal schema, protected-surface requirements, runtime activation, support/platform truth, and transition evidence distinct but linked;
- and give atlas/assistant consumers a bounded surface to import instead of re-scraping docs, middleware setup, provider config, and issue threads.

## Design principles
- **Supported auth truth is not provider activation truth.**
- **Protected-surface requirements do not replace identity surface truth.**
- **Authorization-engine choice does not define the whole identity product.**
- **Cookie/session/token posture stays explicit.**
- **Support/docs/platform caveats are part of the product boundary.**
- **Migration evidence matters because identity changes strand users and operators.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact identity-enabled product subject,”
- “these are the auth methods and principal shapes we actually support,”
- “these are the routes/resources/commands that import those requirements,”
- “these are the providers, cookies, session stores, keys, and verifier settings that were actually activated,”
- “these are the docs/support/platform caveats,”
- “this is what changed from the prior review,”
- and “this is what release/support/policy/schema/client/atlas consumers may safely conclude,”

without inventing a bespoke auth-readiness schema for every repository.

## Read this with
- `design/identity-productization-stack.md`
- `design/identity-productization-pilot-program.md`
- `design/identity-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/credentials-kit.md`
- `design/service-surface-kit.md`
- `design/command-surface-kit.md`
- `design/schema-contract-kit.md`
- `design/client-app-surface-kit.md`
- `design/support-envelope-kit.md`
