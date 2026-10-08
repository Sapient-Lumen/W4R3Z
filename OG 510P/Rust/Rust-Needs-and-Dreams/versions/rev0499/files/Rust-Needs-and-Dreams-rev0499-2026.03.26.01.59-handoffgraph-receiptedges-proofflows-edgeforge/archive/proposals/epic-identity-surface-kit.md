# Epic proposal: Identity Surface Kit

## Thesis
Rust already has serious ingredients for authentication and authorization.
The next high-leverage contribution is not another batteries-included auth stack.
It is a **shared identity/access layer** that turns supported auth methods, principal models, session/token assumptions, access requirements, and checked auth-flow evidence into durable engineering artifacts.

That would be a worthy ecosystem contribution because it helps:
- application authors treat identity as a supported interface rather than framework glue,
- reviewers understand whether a release changed claims/scopes/sessions/login methods,
- docs and protected-route inventories stay tied to the same declared model,
- and teams compare or swap frameworks/providers/policy engines without losing the application’s actual access contract.

## Why now
The timing is good because Rust already has the ingredients, but still not the contract:
- AreWeWebYet’s auth topic still looks like a mixed list of crates from different layers,
- `password-auth` makes password auth straightforward,
- `tower-sessions` and `axum-login` make session + auth middleware practical,
- `oauth2` and `openidconnect` cover federated identity flows,
- `webauthn-rs` covers passkeys/WebAuthn,
- `tower-http` and cookie helpers expose lower-level authorization/session seams,
- and Rust already has multiple serious authorization engines (`cedar-policy`, `oso`, `casbin`) with different strengths.

Sources:
- https://www.arewewebyet.org/topics/auth/
- https://docs.rs/password-auth
- https://docs.rs/tower-sessions/latest/tower_sessions/
- https://docs.rs/axum-login
- https://docs.rs/oauth2/latest/oauth2/
- https://docs.rs/openidconnect
- https://docs.rs/webauthn-rs/latest/webauthn_rs/
- https://docs.rs/tower-http/latest/tower_http/auth/index.html
- https://docs.rs/axum-extra/latest/axum_extra/extract/cookie/
- https://docs.rs/cedar-policy
- https://docs.rs/oso/
- https://docs.rs/casbin/
- https://docs.rs/axum-sessions

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `identity-surface/v0`, `principal-claims-schema/v0`, `access-requirements-map/v0`, `auth-flow-plan/v0`, `auth-check-report/v0`, optional `auth-transition-report/v0`, and `identity-pack/v0`
2. adapters for common Rust session/auth/federation frameworks and policy engines
3. generated docs/reference support for supported login methods, protected surfaces, and principal/claim notes
4. validation/reporting support for positive + negative auth paths, claim normalization, policy decisions, cookie/session assumptions, and drift between docs/config/code
5. release/CI examples showing identity packs attached to services, admin CLIs, docs, and migrations

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one axum/tower service using sessions + password auth + protected routes
- one OIDC-backed service with callback/refresh/logout documentation and checked provider assumptions
- one passkey/WebAuthn pilot with synthetic fixtures and checked registration/authentication flows
- one service using a policy engine (Cedar, Oso, or Casbin) with route/resource requirement maps and denial fixtures

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve auth method identity, principal mappings, and protected-surface references
2. **v0.2 adapters**
   - support `tower-sessions`, `axum-login`, `oauth2`, `openidconnect`, `webauthn-rs`, and common cookie/token layers
   - support attachment conventions for Cedar/Oso/Casbin policies
3. **v0.3 cross-kit integration**
   - integrate with Schema Contract, Runtime Settings, Credentials, Diagnostic Surface, and Observability workflows
   - support diff/baseline workflows across releases and deployment modes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one exact auth framework stack

## Success metrics
- Teams can review identity/access changes as explicit interface artifacts rather than reading middleware diffs and blog posts.
- Supported auth methods, scopes/roles/claims, and protected surfaces remain documented from one declared source.
- Cookie/session/token assumptions become visible and discussable in review.
- Policy-engine use becomes easier to audit because the application-facing access contract is explicit even when the backend differs.
- Rust applications become easier to migrate across frameworks/providers without losing security clarity.

## Archive fit
This proposal adds a strategically important but currently underrepresented domain to the concise archive: **identity and access as a supported interface**.
It also fills a deliberate hole left by Credentials Kit, Runtime Settings Kit, Schema Contract Kit, Diagnostic Surface Kit, and Observability Kit. Those proposals touch auth from adjacent angles, but none of them tries to become the portable contract for supported login methods, claims/principals, protected surfaces, and checked access behavior themselves.
Identity Surface Kit is the missing substrate that can travel alongside docs, releases, and security review without being absorbed by any one framework or policy engine.
