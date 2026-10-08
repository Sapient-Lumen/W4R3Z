# Pilot Program: SDK Productization Stack

## Purpose
Turn the SDK-productization idea into a ranked execution plan that can prove value quickly without overcommitting to one generator, one protocol family, or one provider ecosystem.

This pilot program assumes the archive now distinguishes:
- **upstream contract truth** (schema / service / protocol),
- **SDK product truth** (crate/CLI/mock family, operations, examples, runtime/auth posture),
- **release/distribution truth**,
- and **support/docs truth**.

The goal is to leave behind a thin, reusable substrate other Rust SDK projects could actually adopt.

## Ranked pilot order

### 1) OpenAPI SDK family lane
**Why first**
- Best leverage-to-effort ratio.
- Rust already has strong ingredients: `utoipa`, `progenitor`, OpenAPI Generator, `reqwest`, and real repos like Oxide showing CLI + SDK + mock generation from one spec.
- Good lane for proving generated-versus-hand-written boundaries and example validation.

**What to prove**
- `sdk-surface/v0` for one SDK family
- `sdk-operation-map/v0` mapped to OpenAPI/service ids
- `sdk-runtime-profile/v0` for endpoints/retries/timeouts/proxies
- `sdk-auth-profile/v0` for API-key/OAuth-style hooks
- checked example catalog for SDK + CLI + mock usage
- a diff report that distinguishes protocol changes from SDK-only/product changes

**Success signal**
- A project can review one release of a Rust SDK family without reconstructing truth from generated code, README prose, and raw OpenAPI diffs.

### 2) Smithy / large-SDK lane
**Why second**
- Proves the stack is not just “OpenAPI plus wrappers.”
- Smithy/AWS-style SDKs force clarity on high-level versus low-level API posture, signer/credential layers, runtime selection, and large generated surfaces.

**What to prove**
- import of Smithy-derived source identities
- explicit high-level versus low-level SDK surface support
- auth/signer/profile capture
- runtime/profile separation from source-contract identity
- compatibility notes for generation/runtime changes not visible in wire diffs alone

**Success signal**
- The stack can describe a serious generated SDK family without pretending the generator internals are stable or turning the whole archive into AWS-specific process lore.

### 3) gRPC / protobuf lane
**Why third**
- Prevents the stack from becoming HTTP/OpenAPI-specific.
- gRPC introduces streaming, descriptor/codegen posture, and different CLI/mock/testing expectations.

**What to prove**
- mapping from generated client methods to protobuf/gRPC identities
- streaming and pagination posture where relevant
- auth/runtime profile imports
- checked examples and fixture/mocking support
- honest diff reason codes for schema/protocol versus SDK-product changes

**Success signal**
- The artifact family still makes sense when the source contract is a descriptor/service model rather than OpenAPI.

### 4) Release / support lane
**Why fourth**
- A Rust SDK is only a product if users can install, read, and support it.
- This lane proves the stack matters beyond generation time.

**What to prove**
- attach `sdk-pack/v0` to crate releases and optional CLI binary releases
- attach docs/support/example validation
- model source-build versus released-binary truth where relevant
- attach install/distribution notes for CLI companions
- show versioning policy that distinguishes API change, generator change, and support-policy change

**Success signal**
- Release review and support work consume the same artifacts instead of rebuilding separate truths.

### 5) Downstream consumer lane
**Why fifth**
- Prevents the stack from becoming a producer-only abstraction.
- Shows why the artifacts are worth keeping around.

**What to prove**
- one atlas/learning consumer
- one release/support consumer
- one migration/diff consumer
- one trust/policy or package-admission consumer where applicable

**Success signal**
- At least one downstream consumer clearly benefits from importing SDK product artifacts rather than scraping repos or cargo metadata.

## Candidate adapters and reference ecosystems
- **OpenAPI lane:** `utoipa`, `progenitor`, OpenAPI Generator, Oxide-style generated SDK/CLI/mock repos
- **Smithy lane:** `smithy-rs`, AWS SDK for Rust design/runtime patterns
- **gRPC lane:** `tonic`, `tonic-build`, descriptor attachments
- **Runtime/auth lane:** `reqwest`, tower/hyper-style middleware, identity/runtime/credential imports already tracked elsewhere in the archive
- **Release/support lane:** rustdoc/docs.rs, crate publishing, optional CLI release tooling, checked examples

## Artifact family to prove in the pilot
- `sdk-surface/v0`
- `sdk-operation-map/v0`
- `sdk-runtime-profile/v0`
- `sdk-auth-profile/v0`
- `sdk-check-report/v0`
- `sdk-diff-report/v0`
- `sdk-pack/v0`

## Suggested reference CLI
- `cargo sdkcheck surface`
- `cargo sdkcheck profiles`
- `cargo sdkcheck examples`
- `cargo sdkcheck diff`
- `cargo sdkcheck pack`

The tool should start as an adapter + explainer + packer, not as a generator or hosted service.

## Anti-goals for the pilot
- not another OpenAPI or Smithy generator fork;
- not another HTTP client wrapper pretending to be an SDK platform;
- not another auth framework;
- not a platform-specific cloud SDK grand unification project;
- not a fake “one number” SDK health/readiness score.

## Why this pilot is strategically interesting
This seam is unusually valuable because it touches:
- schema/service/protocol truth,
- library-as-product reality,
- auth/config/runtime ergonomics,
- docs/support quality,
- release/versioning posture,
- and multi-artifact product families (crate + CLI + mocks).

It is exactly the kind of territory where Rust has strong components but still lacks a **portable boring contract**.
