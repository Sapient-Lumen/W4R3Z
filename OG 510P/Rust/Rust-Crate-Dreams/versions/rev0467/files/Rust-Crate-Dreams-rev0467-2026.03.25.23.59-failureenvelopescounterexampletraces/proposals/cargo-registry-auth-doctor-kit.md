---
id: P-0492
title: Cargo Registry Auth Doctor Kit — provider-chain receipts, auth-required sparse-registry diagnosis, and redacted login/fetch/publish support bundles
status: idea
domains: [cargo, registries, security, devtools, ci, support, tooling]
last_reviewed: 2026-03-07
evidence:
  - https://doc.rust-lang.org/cargo/reference/registry-authentication.html
  - https://doc.rust-lang.org/cargo/reference/credential-provider-protocol.html
  - https://doc.rust-lang.org/cargo/reference/registry-index.html
  - https://doc.rust-lang.org/cargo/reference/registries.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
---

# Problem

Cargo’s registry-authentication story is no longer “just paste a token into `~/.cargo/credentials.toml`.”

The substrate is already real and has become meaningfully more complex:

- Cargo authenticates with **credential providers**, which may be built-in or external.
- Cargo documents a **JSON stdin/stdout protocol** for external credential providers.
- Alternative registries can require authenticated sparse-index, download, and search access via `auth-required = true`.
- Cargo supports both **git** and **sparse** registry protocols.
- Config/env/CLI layering can change which registry, which provider, or which token source wins.
- crates.io trusted publishing adds another auth path for publish-time identity.

That is all useful progress, but it also creates a fresh maintainer-support seam.

Ordinary teams still lack a boring answer to questions like:

- which registry URL and protocol Cargo actually used,
- which credential provider chain was consulted and in what order,
- whether the failure happened during **login**, **index access**, **crate download**, **search**, or **publish**,
- whether a failure came from provider configuration, token scope, registry `auth-required` policy, protocol mismatch, or environment drift,
- which facts can be shared with support engineers without leaking live tokens,
- and how the registry-auth story changed between two CI runners, two toolchains, or two releases.

Today the workflow is still improvised:

- turn on `CARGO_LOG`,
- paste fragments of redacted logs into a ticket,
- inspect several `.cargo/config.toml` layers by hand,
- guess whether a provider executable ran,
- and manually reconstruct whether the failure was before or after registry identity was established.

The missing crate is **not** another credential store and **not** another registry server.

The missing crate is a **Cargo Registry Auth Doctor Kit**: a crate and cargo-adjacent tool that capture provider-chain behavior, auth-required registry facts, and operation-level failure context into a durable **diagnosis receipt**.

# What it provides

- `registry-auth-policy.toml` — declares which registries are in scope, which operations matter (`login`, `fetch`, `download`, `search`, `publish`), redaction posture, and whether the bundle is advisory or CI-blocking.
- `registry-targets.manifest.json` — normalized registry names, canonical URLs, protocol family (`git`, `sparse`), expected auth requirements, and operation coverage.
- `provider-chain.receipt.json` — which provider entries were configured, which were attempted, which returned credentials, which were skipped, and which fell back.
- `auth-session.report.json` — operation-scoped verdicts such as `login_ok`, `provider_not_found`, `provider_protocol_error`, `unauthorized_index`, `download_unauthorized`, `publish_identity_mismatch`, `manual_review_required`.
- `registry-capabilities.report.json` — records `auth-required`, API/index/download/search expectations, and whether the observed behavior matched declared registry policy.
- `redaction.map.json` — keeps secrets, raw tokens, and sensitive endpoints out of bundles while preserving structural evidence.
- `auth-drift.diff.json` — compares two bundles and classifies `provider_changed`, `registry_policy_changed`, `protocol_changed`, `auth_scope_changed`, `failure_moved_stage`, and `manual_review_required`.
- `cargo registry-auth-doctor capture` — probe one configured registry/auth environment and emit a bundle.
- `cargo registry-auth-doctor probe --op fetch|publish|search` — run one operation-shaped diagnosis pass.
- `cargo registry-auth-doctor diff <old> <new>` — compare two auth environments or CI runs.
- `*.authdoctor.zip` — portable support bundle for CI maintainers, registry operators, credential-provider authors, and crate publishers.

# What the crate should provide other people

1. **A boring support artifact** for registry-auth failures that is safer to share than raw logs.
2. **A provider-chain view** that makes Cargo’s credential-provider behavior explainable.
3. **Operation-level blame** so teams can distinguish login, fetch, download, search, and publish failures.
4. **A migration aid** when moving from stored tokens to provider-based or trusted-publishing workflows.
5. **A diffable environment receipt** for “works on my machine” versus “fails in CI” registry issues.

# Persona / who it’s for

- maintainers using crates.io plus one or more alternative registries
- CI and release engineers diagnosing publish or fetch failures
- platform teams standardizing credential-provider policy
- registry operators supporting authenticated sparse registries
- credential-provider authors who need a stable support artifact

# Users & user stories

- **Release engineer**: “Tell me whether this publish failed because trusted publishing identity was wrong or because Cargo never got usable credentials.”
- **Registry operator**: “Show me whether the client honored our `auth-required` policy and which stage failed.”
- **Maintainer**: “Give me one redacted bundle I can attach to a ticket instead of dumping logs and config snippets.”
- **Provider author**: “Show me whether my provider was invoked, returned a credential, or failed the protocol.”

# Prior art (and why it’s insufficient)

- Cargo already documents registry authentication and credential providers.
- Cargo already documents the external provider protocol.
- Cargo already supports authenticated sparse registries and alternative registries.
- crates.io trusted publishing already gives one modern publish-time identity path.
- The archive already has **P-0477 Cargo Publish Receipt Join Kit**, which is about post-publish release confirmation and provenance.
- The archive already has **trusted-publishing-tooling-kit** and **sparse-registry-reference-server-kit**, which are about server-side or workflow enablement.

What remains missing is the **client-side diagnosis artifact** that explains what Cargo believed about registries, providers, operations, and failures.

# Design goals

1. **Diagnosis-first** — optimize for supportability and blame, not for storing or minting credentials.
2. **Operation-shaped** — login, fetch, download, search, and publish should remain visibly distinct.
3. **Redaction-first** — bundles should travel safely without live secrets.
4. **Config-aware** — environment/config/provider precedence must be first-class.
5. **Registry-honest** — keep crates.io, authenticated sparse indexes, and alternative registries visibly distinct.

# MVP surface

- Minimal types: `RegistryAuthPolicy`, `RegistryTargetsManifest`, `ProviderChainReceipt`, `AuthSessionReport`, `RegistryCapabilitiesReport`, `AuthDrift`, `AuthDoctorBundle`
- Minimal functions:
  - `capture_registry_targets()`
  - `capture_provider_chain()`
  - `classify_auth_session()`
  - `diff_auth_bundles()`
  - `write_redacted_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `zip`
  - `markdown`
  - `providers`
  - `trusted-publishing`

# Compatibility story

- Must work above crates.io and alternative registries.
- Must record whether the registry protocol is `git` or `sparse`.
- Must treat `auth-required` as an observed or declared policy fact, not a guess.
- Must keep provider-chain facts stable even if Cargo adds more built-in providers later.
- Should remain useful when the final auth mechanism is OIDC trusted publishing, because support teams still need one client-side diagnosis bundle.

# Conformance & fixtures

- crates.io token-based login fixture with successful fetch and publish-disabled environment.
- alternative sparse registry fixture with `auth-required = true` and missing provider configuration.
- provider executable fixture returning protocol error or malformed JSON.
- trusted-publishing fixture where publish identity is expected but unavailable on one runner.
- diff fixtures for `git` → `sparse` protocol migration and token-file → provider-based migration.

# Path to boring stability

- Freeze the stage/verdict taxonomy before adding deep provider-specific adapters.
- Start with capture and classification, not interactive login orchestration.
- Keep redaction defaults conservative.
- Prefer explicit `manual_review_required` outcomes over pretending every auth stack can be fully inferred.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A cargo subcommand that reads Cargo registry config/provider setup, probes one operation, and emits a redacted bundle saying which registry, protocol, provider chain, and operation stage succeeded or failed.

# De-risk plan

1. Start with read-only probing and redacted receipts rather than any interactive credential setup.
2. Keep the first registry-policy model intentionally small: protocol, `auth-required`, operation stages.
3. Support crates.io plus one authenticated sparse registry fixture before wider generalization.
4. Treat trusted publishing as an observed publish-identity fact, not a full CI orchestrator.

# Non-goals

- Not a credential manager or secret store.
- Not a registry implementation.
- Not a replacement for Cargo’s own auth system.
- Not a publish pipeline service.

# Architecture & API sketch

```rust
pub enum AuthStage {
    Login,
    IndexAccess,
    Download,
    Search,
    Publish,
}

pub fn capture_provider_chain(cx: &Context) -> Result<ProviderChainReceipt>;
pub fn classify_auth_session(bundle: &ProbeInputs) -> AuthSessionReport;
pub fn write_redacted_bundle(bundle: &AuthDoctorBundle, out: &std::path::Path) -> Result<()>;
```

# Why now / why this is newly possible

Cargo’s registry-auth world crossed a threshold. Credential providers are real. Authenticated sparse registries are real. Trusted publishing is real. But the maintainer-facing support artifact is still mostly a pile of logs and folk knowledge.

That is exactly the kind of seam where a worthy Rust crate can make something newly boring.
