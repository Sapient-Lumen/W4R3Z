# Gap: authentication, authorization, and session contracts

## What is missing
Rust has real authentication and authorization building blocks, but it still lacks a **shared identity/access contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which authentication methods an application actually supports,
- which session or token mechanisms back those methods,
- how claims, identities, roles, groups, scopes, or attributes map into application principals,
- which routes, RPCs, commands, or resource operations require which access conditions,
- what cookie/token/session security assumptions are part of the support promise,
- what logout/refresh/reauth/recovery/step-up flows exist,
- and what evidence exists that the documented access surface still matches the shipped program.

That missing layer matters because Rust applications increasingly rely on a mix of password auth, cookies/sessions, OIDC/OAuth2 federation, passkeys/WebAuthn, bearer tokens, and embedded policy engines. The ecosystem has strong parts, but teams still ship the **supported identity surface** as a pile of middleware wiring, route guards, env vars, provider metadata, and prose.

Sources:
- https://www.arewewebyet.org/topics/auth/
- https://docs.rs/password-auth
- https://docs.rs/tower-sessions/latest/tower_sessions/
- https://docs.rs/axum-login
- https://docs.rs/oauth2/latest/oauth2/
- https://docs.rs/openidconnect
- https://docs.rs/webauthn-rs/latest/webauthn_rs/
- https://docs.rs/cedar-policy
- https://docs.rs/oso/
- https://docs.rs/casbin/
- https://docs.rs/tower-http/latest/tower_http/auth/index.html
- https://docs.rs/axum-extra/latest/axum_extra/extract/cookie/

## The current seam is awkward
The ecosystem clearly has ingredients:
- `password-auth` provides a high-level password-authentication lane,
- `tower-sessions` provides pluggable session middleware,
- `axum-login` layers user identification/authentication/authorization on top of `tower`,
- `oauth2` and `openidconnect` cover federation/client flows,
- `webauthn-rs` covers passkey/WebAuthn relying-party workflows,
- `tower-http` exposes HTTP-authorization middleware seams,
- `axum-extra` exposes signed/private cookie jars,
- and `cedar-policy`, `oso`, and `casbin` cover materially different authorization-policy styles.

But each real project still hand-assembles its identity story out of:
- provider-specific login handlers,
- callback and redirect wiring,
- cookie/session settings,
- token validation glue,
- claim extraction and normalization,
- route/resource permission checks,
- role/scope/group conventions,
- admin bootstrap rules,
- recovery/reauth/logout semantics,
- and ad hoc tests proving some happy-path logins and denials work.

The result is not that Rust lacks auth crates.
The result is that there is no portable way to say:
- “these are the supported authentication methods,”
- “these are the issuer/session/token assumptions,”
- “these are the public principal and claim shapes,”
- “these routes/resources/actions require these access conditions,”
- or “these login, refresh, logout, and denial paths were actually checked.”

AreWeWebYet’s auth page is revealing here: it is a grab-bag of crates from very different layers, not a shared support model. That is exactly the pattern this archive should notice: strong building blocks, weak shared boundary.

Sources:
- https://www.arewewebyet.org/topics/auth/
- https://docs.rs/password-auth
- https://docs.rs/tower-sessions/latest/tower_sessions/
- https://docs.rs/axum-login
- https://docs.rs/oauth2/latest/oauth2/
- https://docs.rs/openidconnect
- https://docs.rs/webauthn-rs/latest/webauthn_rs/
- https://docs.rs/cedar-policy
- https://docs.rs/oso/
- https://docs.rs/casbin/
- https://docs.rs/tower-http/latest/tower_http/auth/index.html
- https://docs.rs/axum-extra/latest/axum_extra/extract/cookie/

## Why this matters
This gap is bigger than “nicer auth middleware.”
It affects:
1. **security reviewability** — cookie flags, session fixation posture, issuer/audience assumptions, key rotation, and public-vs-internal claim exposure are support claims, not trivia;
2. **application compatibility** — changing scopes, roles, claims, login methods, or callback/session behavior can be a real breaking change;
3. **documentation quality** — login methods, required headers/cookies, passkey support, and protected-route assumptions drift unless they derive from one declared model;
4. **cross-framework portability** — apps should be able to preserve their access contract while moving between tower/axum/actix/tonic or when swapping providers;
5. **testing realism** — most teams check a few route guards, but do not carry a portable artifact that states which positive and negative identity/access flows were covered;
6. **ecosystem composition** — Schema Contract Kit, Command Surface Kit, Runtime Settings Kit, Credentials Kit, Diagnostic Surface Kit, and Observability Kit all need a coherent identity/access story without owning it.

Rust service and web stacks are mature enough that identity is now part of the application’s supported interface. The ecosystem still treats it too often as framework glue.

Sources:
- https://docs.rs/tower-sessions/latest/tower_sessions/
- https://docs.rs/axum-login
- https://docs.rs/oauth2/latest/oauth2/
- https://docs.rs/openidconnect
- https://docs.rs/webauthn-rs/latest/webauthn_rs/
- https://docs.rs/cedar-policy
- https://docs.rs/oso/
- https://docs.rs/casbin/

## What “good” looks like
A worthy contribution here is **not** another batteries-included auth framework, another JWT helper, or another policy engine.

It is a shared identity/access boundary:
- one `identity-surface/v0` describing supported auth methods, principal models, token/session/cookie modes, external-provider assumptions, and supported recovery/logout/step-up behaviors,
- one `principal-claims-schema/v0` describing normalized principals, exposed claims/attributes, role/group/scope semantics, and redaction rules,
- one `access-requirements-map/v0` mapping routes/RPCs/resources/actions to authentication and authorization requirements,
- one `auth-flow-plan/v0` describing login/callback/refresh/logout/passkey/recovery flows and their important security toggles,
- one `auth-check-report/v0` recording checked positive and negative flows, protected-surface coverage, claim-mapping results, session/cookie policy checks, and policy-evaluation fixtures,
- one optional `auth-transition-report/v0` for identity-provider swaps, scope/role model changes, password→passkey transitions, or session/token changes,
- and one `identity-pack/v0` bundle for CI, docs, release review, and archaeology.

That would let Rust teams treat authentication and authorization as a reviewable support surface instead of a fragile pile of middleware choices.
