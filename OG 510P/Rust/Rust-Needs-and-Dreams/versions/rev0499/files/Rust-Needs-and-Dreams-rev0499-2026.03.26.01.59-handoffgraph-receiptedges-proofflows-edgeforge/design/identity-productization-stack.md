# Design: Identity Productization Stack (Identity Surface + Runtime Settings + Credentials + Support Envelope + Service/Client/Data Attachments)

## Goal
Turn Rust authentication, authorization, session, token, and principal support into a **portable productization stack** instead of leaving each application to publish its identity story as a tangle of middleware wiring, provider dashboards, callback URLs, cookie settings, secret sources, route guards, and README prose.

The stack should **not** replace `tower-sessions`, `axum-login`, `oauth2`, `openidconnect`, `webauthn-rs`, `password-auth`, `cedar-policy`, `oso`, `casbin`, `tower-http`, or framework-specific auth helpers.
It should make them compose better and make supported identity/access behavior reviewable.

## Why this note is needed now
Rust’s current productization signals now make identity impossible to treat as a side detail:
- the 2024 State of Rust survey says Rust is especially popular for **server backends, web and networking services, and cloud technologies**;
- the 2025 survey says the broad shape is similar, online docs remain the preferred canonical reference, and debugging/resource friction remain real;
- the archive has already promoted Service Productization, Client Productization, and Data Productization as frontier seams, which makes the missing auth boundary easier to see;
- AreWeWebYet’s auth topic is still a **mixed list of crates from different layers**, not a shared support model;
- `tower-sessions` already provides pluggable sessions, `axum-login` already provides user identification/authentication/authorization middleware for `axum`, `oauth2` and `openidconnect` already cover federation, `webauthn-rs` already covers passkeys/WebAuthn, `password-auth` already provides a high-level password lane, `tower-http` and `axum-extra` already expose HTTP auth and signed/private cookie seams, and `cedar-policy`, `oso`, and `casbin` already prove authorization policy is not one-model-only.

Together, those signals argue that the missing contribution is **not** another auth framework or JWT helper. It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Identity Surface: declared auth and principal truth
Identity Surface owns the **declared supported identity surface** for an application, service, workspace, or product line:
- supported authentication methods,
- principal and claims models,
- public versus internal identity attributes,
- token/session/cookie modes,
- required reauth, logout, refresh, recovery, and step-up flows,
- route/resource/action access requirements,
- and checked positive/negative access-flow evidence.

Identity Surface answers questions like:
- “Which login methods are actually supported?”
- “What is the official principal model?”
- “What are the public claim, role, group, and scope semantics?”
- “Which routes or actions require which access posture?”

Design rule: **middleware choices and provider dashboards must not be the only durable description of the identity surface**.

### 2) Service / command / schema / client attachments: protected-surface truth
Identity does not live only at the login screen. It also attaches to real application surfaces:
- Service Surface for HTTP routes and service operations,
- Command Surface for admin and automation commands,
- Schema Contract for API/RPC/message-level security requirements,
- Client App Surface for app capabilities, deeplinks, and platform-specific auth posture.

This layer answers questions like:
- “Which routes require a session versus a bearer token?”
- “Which RPC or resource operation expects which principal attributes?”
- “Which admin command is machine-only or operator-only?”
- “Which client capability depends on passkeys, browser cookies, or external provider redirects?”

Design rule: **protected surfaces may import identity requirements, but they must not redefine identity truth from scratch**.

### 3) Runtime Settings + Credentials: provider and activation truth
Runtime Settings and Credentials own the **activation posture** that turns declared identity support into reality:
- issuer URLs and discovery documents,
- callback and redirect URLs,
- cookie names, flags, and key sources,
- session backend/store selection,
- JWKS / verifier / audience settings,
- client ids, secrets, passkey relying-party parameters,
- machine credential and key-rotation posture,
- and secret-source activation rules across local, CI, staging, and production.

This layer answers questions like:
- “Which provider configuration powered the deployed auth surface?”
- “Where did the cookie or signing key come from?”
- “Was passkey support or OIDC support actually activated in this profile?”
- “Which claims, issuers, or session backends were merely documented versus actually configured?”

Design rule: **identity support claims must not silently depend on unstated environment variables or secret-manager conventions**.

### 4) Support Envelope + DocProof: support and docs truth
Support Envelope and DocProof own the **supportability boundary** for identity behavior:
- browser/platform/runtime assumptions,
- target and cfg caveats,
- docs.rs / guide / example posture,
- source-build versus release-artifact differences,
- supported provider families and support levels,
- and checked docs/examples for login, logout, denial, recovery, and operator workflows.

This layer answers questions like:
- “Is passkey support official or best-effort on this client stack?”
- “What cookie/browser assumptions are part of the support promise?”
- “Which examples and docs were actually checked?”
- “What is supported for source builds versus released binaries?”

Design rule: **README auth setup instructions and screenshots are not the support contract**.

### 5) Transition and archaeology truth
Identity evolves over time, often painfully. The stack therefore needs a dedicated migration lane:
- provider swaps,
- password → passkey transitions,
- role/scope/claim model changes,
- session-store or token-verifier changes,
- stricter cookie posture,
- and auth-flow breakage or denial-surface regressions.

This lane answers questions like:
- “What changed in the supported identity model?”
- “Did public auth requirements change?”
- “Was the principal model migrated or merely wrapped?”
- “Which changes were additive, breaking, or only internal?”

Design rule: **identity changes are product and support events, not just middleware refactors**.

### 6) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **Release / policy** consumers can review auth changes without scraping routes and env vars.
- **Support / incident** consumers can answer login, denial, and cookie/session questions from artifacts rather than team memory.
- **Service / client / schema** consumers can import auth requirements without becoming the new source of truth.
- **Atlas / learning** consumers can describe real Rust auth lanes without pretending one framework or policy engine won.
- **Migration** consumers can compare identity changes without flattening provider, principal, and secret posture into one diff.

Design rule: **consumers import selected identity facts; they do not redefine the identity stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “Rust finally gets Django auth” or “the one true policy engine.”
It is a portable boring stack with clear boundaries:

1. **supported-auth and principal truth first**
   - prove `identity-surface/v0`, `principal-claims-schema/v0`, and `auth-check-report/v0` on one real app/service;
2. **protected-surface attachments second**
   - attach auth/access requirements to routes, RPCs, commands, and client capabilities without making those lanes the identity authority;
3. **runtime activation third**
   - attach provider/issuer/cookie/session/key posture through `runtime-settings` and `credentials` imports;
4. **support/docs fourth**
   - prove docs, browser/runtime assumptions, and support levels instead of leaving them to issue trackers and setup pages;
5. **transition and downstream consumers fifth**
   - prove identity changes, provider swaps, and password→passkey migrations can be reviewed and imported by release/support/policy consumers.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a new mega-schema that erases the lane boundaries.

## Ranked first execution lanes
1. **Supported-auth / principal lane**
   - best first exporter because most real Rust apps can already declare their login methods, principal model, and token/session posture even before deeper integrations stabilize.
2. **Protected-surface attachment lane**
   - proves identity matters beyond the login handler and can attach cleanly to routes, commands, RPCs, and app surfaces.
3. **Runtime activation lane**
   - proves provider metadata, cookie keys, verifier posture, and secret activation can be made reviewable.
4. **Support/docs lane**
   - proves passkey/browser/runtime-floor/support truth is part of the product surface.
5. **Transition / consumer lane**
   - proves the stack matters when auth models change, not just when greenfield apps are designed.

## Non-goals
- one batteries-included auth framework;
- one universal JWT/session abstraction;
- one policy language or authorization engine to replace the others;
- flattening auth methods, principals, provider activation, protected surfaces, docs/support, and transitions into one fake “secure auth” badge;
- pretending one successful login or one provider integration test proves the supported identity surface.

## Archive implications
- The archive should now treat **Identity Surface + Runtime Settings + Credentials + Support Envelope** as a coupled **Identity Productization Stack**, with Service Surface, Command Surface, Schema Contract, and Client App Surface as importing attachment lanes rather than competing truth engines.
- Future revisions should prefer **supported-auth truth, principal/claim truth, protected-surface attachments, runtime activation truth, docs/support truth, and transition evidence** over another batteries-included auth framework, JWT helper, framework-local guard library, or giant auth control-plane pitch.
- When service/client/data/release/support work cites “auth support,” it should import **identity surface**, **protected-surface requirements**, **runtime settings/credentials posture**, **support/docs truth**, and **transition evidence** separately.

The explicit proposal-layer candidate for this stack is now [`proposals/epic-identity-productization-stack.md`](../proposals/epic-identity-productization-stack.md): a thin `cargo identity-product` / `identity-product-pack/v0` layer above Identity Surface + Runtime Settings + Credentials + Support Envelope rather than another auth framework or policy-engine winner story.

## References (signals)
- 2024 State of Rust survey results:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- AreWeWebYet topics / auth:
  https://www.arewewebyet.org/topics/
- `tower-sessions`:
  https://docs.rs/tower-sessions/latest/tower_sessions/
- `axum-login`:
  https://docs.rs/axum-login
- `password-auth`:
  https://docs.rs/password-auth
- `oauth2`:
  https://docs.rs/oauth2/latest/oauth2/
- `openidconnect`:
  https://docs.rs/openidconnect
- `webauthn-rs`:
  https://docs.rs/webauthn-rs/latest/webauthn_rs/
- `tower-http` auth middleware:
  https://docs.rs/tower-http/latest/tower_http/auth/index.html
- `axum-extra` cookie extractors:
  https://docs.rs/axum-extra/latest/axum_extra/extract/cookie/index.html
- `cedar-policy`:
  https://docs.rs/cedar-policy
- `oso`:
  https://docs.rs/oso/
- `casbin`:
  https://docs.rs/casbin/
