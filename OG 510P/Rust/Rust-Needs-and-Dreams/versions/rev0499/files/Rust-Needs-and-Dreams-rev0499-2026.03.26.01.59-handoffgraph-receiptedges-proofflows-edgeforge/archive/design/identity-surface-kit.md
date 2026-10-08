# Design: Identity Surface Kit (`cargo identity`, `identity-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust application’s supported identity and access surface: authentication methods, principal/claim models, sessions/tokens/cookies, access requirements, important security assumptions, and evidence that the declared surface still matches the program.

This should **not** replace `tower-sessions`, `axum-login`, `oauth2`, `openidconnect`, `webauthn-rs`, `password-auth`, `cedar-policy`, `oso`, `casbin`, or framework-specific middleware.
It should make them compose better and make identity/access support claims reviewable.

## References (signals)
- AreWeWebYet’s auth topic page is still a mixed list of crates from very different layers rather than a unified support model.
  https://www.arewewebyet.org/topics/auth/
- `password-auth` already provides a deliberately high-level password-authentication lane.
  https://docs.rs/password-auth
- `tower-sessions` provides pluggable session middleware and explicitly positions itself as substrate for generalized auth solutions.
  https://docs.rs/tower-sessions/latest/tower_sessions/
- `axum-login` explicitly provides user identification, authentication, and authorization as `tower` middleware for `axum`.
  https://docs.rs/axum-login
- `oauth2` provides a strongly typed OAuth2 implementation and points authentication users toward `openidconnect`.
  https://docs.rs/oauth2/latest/oauth2/
  https://github.com/ramosbugs/oauth2-rs
- `openidconnect` provides strongly typed OpenID Connect interfaces for authentication providers.
  https://docs.rs/openidconnect
- `webauthn-rs` provides a secure server-side WebAuthn/passkey lane for Rust applications.
  https://docs.rs/webauthn-rs/latest/webauthn_rs/
- `axum-extra` and related cookie tooling expose signed/private cookie jars and key management seams that directly affect session security posture.
  https://docs.rs/axum-extra/latest/axum_extra/extract/cookie/
- `tower-http` exposes request-authorization middleware seams at the HTTP layer.
  https://docs.rs/tower-http/latest/tower_http/auth/index.html
- `cedar-policy`, `oso`, and `casbin` show that Rust already supports multiple materially different authorization models.
  https://docs.rs/cedar-policy
  https://docs.rs/oso/
  https://docs.rs/casbin/
- `axum-sessions` explicitly moved development to `tower-sessions`, which is a reminder that framework-level auth/session stacks evolve and need portable contracts above them.
  https://docs.rs/axum-sessions

## Core components

### 1) `identity-surface/v0`
A design-time declaration of the supported identity surface for a binary/service/workspace.

Required ideas:
- subject identity (crate / workspace / service / deployment profile)
- supported authentication methods:
  - password
  - passkey/WebAuthn
  - session cookie
  - bearer token
  - API key
  - OAuth2/OIDC federation
  - anonymous/guest
  - service-to-service / machine credentials
- method posture:
  - `official`, `best-effort`, `experimental`, `deprecated`, `internal`
- provider assumptions:
  - issuers/discovery endpoints/provider ids
  - audience/client-id expectations
  - PKCE/nonce/state expectations
  - callback/redirect modes
- session/token/cookie modes:
  - session store type
  - token family (opaque/JWT/PASETO/etc.)
  - cookie transport requirements
  - rotation/expiry/refresh posture
- lifecycle/support lanes:
  - login
  - refresh
  - logout
  - reauthentication / step-up
  - recovery / reset / bootstrap admin

### 2) `principal-claims-schema/v0`
A portable declaration of the application’s normalized identity model.

Required ideas:
- principal kinds (`user`, `service`, `admin`, `anonymous`, etc.)
- normalized ids and display identifiers
- supported claims/attributes:
  - issuer
  - subject
  - email / username
  - roles / groups / scopes
  - tenancy / organization / project fields
  - auth-strength / MFA / WebAuthn-related markers
- exposure policy:
  - internal only
  - user-visible
  - loggable/redacted
  - transport-safe / not transport-safe
- normalization/mapping rules:
  - external provider claim → internal principal field
  - missing-claim handling
  - rename/alias rules

This must preserve the distinction between **external claims** and **internal principal truth**.

### 3) `access-requirements-map/v0`
A map from protected surface to access requirements.

Potential subjects:
- HTTP routes/endpoints
- RPC methods
- GraphQL operations
- message topics
- CLI/admin commands
- resource actions (`read`, `write`, `approve`, `delete`, etc.)

Required ideas:
- required authentication state
- accepted principal kinds
- required scopes/roles/groups/attributes
- authorization backend references:
  - inline requirements
  - policy-engine query handles
  - Cedar/Oso/Casbin policy references
- denial posture:
  - unauthenticated vs unauthorized distinctions
  - redaction of resource existence
- linked external artifacts where available:
  - OpenAPI/Schema Contract operation ids
  - Command Surface ids

### 4) `auth-flow-plan/v0`
A concrete plan for the supported auth flows.

Required ideas:
- login/callback/refresh/logout/passkey registration + auth/recovery steps
- required runtime settings and secrets references
- required cookies / headers / CSRF / nonce / PKCE/state assumptions
- session-store or token-verifier assumptions
- local-dev/test identity fixtures and fake providers
- important unsupported or intentionally omitted lanes

This is where the kit stops pretending “crate exists” equals “flow is reviewable.”

### 5) `auth-check-report/v0`
Evidence from tests, checks, and fixtures.

Possible contents:
- successful login/logout/refresh/passkey-auth runs
- negative-path checks (bad password, wrong issuer, expired token, missing scope, policy deny)
- claim-normalization results
- protected-surface coverage summary
- cookie/session policy checks (secure/httpOnly/same-site/prefix posture where relevant)
- callback/redirect verification outcomes
- authorization-policy evaluation fixtures/results
- drift findings:
  - undocumented auth method
  - route missing from access map
  - stale scope/role claim
  - provider mismatch
  - recovery/logout docs drift
- redaction/telemetry policy checks for identity-bearing fields

### 6) `auth-transition-report/v0` (optional)
For compatibility-sensitive changes:
- password → passkey adoption
- OIDC provider swap
- token-family change
- scope/role/group model change
- session-store/backend migration
- callback/cookie policy tightening
- admin bootstrap or recovery-flow changes

Should distinguish:
- surface additions
- surface removals
- tighter requirements
- backward-compatible aliases
- manual operator/user action required

### 7) `identity-pack/v0`
Bundle format containing:
- `identity-surface/v0`
- `principal-claims-schema/v0`
- `access-requirements-map/v0`
- optional `auth-flow-plan/v0`
- one or more `auth-check-report/v0`
- optional `auth-transition-report/v0`
- optional raw attachments: provider metadata snapshots, policy fixtures, example tokens (redacted/synthetic), cookie/session configs, and route inventories

This is the unit that should travel through CI, docs, release review, and later archaeology.

### 8) `cargo identity`
Reference UX:
- `cargo identity init`
- `cargo identity schema`
- `cargo identity check`
- `cargo identity diff`
- `cargo identity docs`
- `cargo identity pack`

`cargo identity` should begin as an explainer / adapter / packer.
It should not pretend to be the one true auth framework.

## Default policy
- **Separate supported auth methods from principal schema, access requirements, and run evidence.**
- **Separate external-provider claims from internal principal truth.**
- **Treat sessions, cookies, and tokens as support surfaces, not just implementation details.**
- **Record denial semantics and redaction policy explicitly.**
- **Preserve raw policy-engine/provider truth as attachments rather than flattening everything into one fake model.**
- **Distinguish checked flows from illustrative flows** so docs can be honest.

## What the kit should provide to others
- **Schema Contract Kit:** attach auth requirements to API operations without making OpenAPI the source of truth for login/session behavior.
- **Command Surface Kit:** describe admin/maintenance commands that require certain principals or credentials.
- **Runtime Settings Kit:** reference the settings that control issuers, client ids, callback URLs, cookie keys, and session backends without absorbing runtime configuration itself.
- **Credentials Kit:** identify which keys/secrets/provider credentials power the auth surface without taking over secret storage or leak prevention.
- **Diagnostic Surface Kit:** align auth/access denial codes and public failure metadata with declared requirements.
- **Observability Kit:** declare which identity fields may be logged/exported/redacted without turning telemetry into the identity source of truth.

## Overlap boundaries
- **Not another auth framework:** framework ergonomics remain with `axum-login`, framework middleware, provider-specific helpers, etc.
- **Not another policy engine:** Cedar/Oso/Casbin and similar systems remain distinct; this kit packages declared access requirements and evidence across them.
- **Not Credentials Kit:** key storage, secret retrieval, and leak prevention are separate concerns.
- **Not Runtime Settings Kit:** settings such as issuer URLs, cookie secrets, and session backends remain runtime settings, though this kit references them.
- **Not Schema Contract Kit:** API schemas may mention security schemes, but the supported identity surface is broader than HTTP schema metadata.
- **Not a hosted IdP or control plane:** the value is the artifact and review workflow, not a new cloud auth product.

## Hard problems (explicitly scoped)
1. **Auth surfaces are protocol-diverse**
   - passwords, sessions, bearer tokens, OAuth2/OIDC, and WebAuthn do not collapse cleanly into one runtime object model.
   - v0 should model the differences explicitly.

2. **Authorization models vary substantially**
   - inline RBAC, claims-based checks, Cedar, Oso, and Casbin are not the same thing.
   - the kit should reference backend capabilities and requirement handles instead of flattening them.

3. **Identity fields are privacy-sensitive**
   - public docs, logs, traces, and error surfaces must not all expose the same identity material.

4. **Routes/resources drift faster than docs**
   - a map of protected surfaces and access requirements must be derivable or checkable against code/framework inventories.

5. **Compatibility is easy to underestimate**
   - changing auth methods, claims, or scopes can strand users, scripts, or other services.
   - those changes deserve explicit transition artifacts.

## Minimal adoption path
1. Publish schemas for `identity-surface/v0`, `principal-claims-schema/v0`, `access-requirements-map/v0`, and `auth-check-report/v0`.
2. Add adapters for `tower-sessions`, `axum-login`, `oauth2`, `openidconnect`, `webauthn-rs`, and common middleware stacks.
3. Add policy-engine adapters or attachment conventions for Cedar, Oso, and Casbin.
4. Add docs generation for supported auth methods, protected surfaces, and operator-facing identity notes.
5. Add transition/diff support so releases can review auth/access surface changes explicitly.

## Why this is an ecosystem contribution, not just repo hygiene
Rust’s web/service ecosystem is mature enough that identity and access behavior is part of the product’s supported interface.
The missing contribution is not one more auth crate.
The missing contribution is a portable identity/access contract that can travel through docs, CI, release review, and security archaeology.
