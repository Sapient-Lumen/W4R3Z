# Design note: SDK Productization Stack (SDK Surface + Schema Contract + Identity Productization + Runtime Settings + Library/Release/Support imports)

## Goal
Define the **division of labor and consumer flow** between SDK product surfaces, upstream machine-readable contracts, auth/config activation, release/distribution truth, and support claims so the ecosystem can make **real Rust SDKs** reviewable without anointing one code generator, one protocol family, or one platform provider as the universal answer.

This is **not** a new one-tool mega-platform.
It is a stack note explaining how existing archive pieces should compose, and it should be read together with [`design/sdk-surface-kit.md`](./sdk-surface-kit.md), [`design/sdk-productization-pilot-program.md`](./sdk-productization-pilot-program.md), and [`proposals/epic-sdk-productization-stack.md`](../proposals/epic-sdk-productization-stack.md).

## Why this note is needed now
Rust now clearly has the ingredients for serious API-product work, but still lacks a portable productization layer above them:
- the 2024 State of Rust survey says Rust is especially popular for server backends, web/networking services, and cloud technologies;
- the 2025 State of Rust survey says online docs remain canonical while LLM workflows and agentic editors are rising, which raises the value of bounded machine-readable SDK/product truth;
- `utoipa` and `progenitor` show a healthy code-first OpenAPI → Rust-client path;
- OpenAPI Generator keeps a Rust client lane alive across multiple HTTP-library templates;
- `tonic` and `tonic-build` keep protobuf/gRPC codegen a normal Rust workflow;
- `smithy-rs` proves Rust SDK generation at very large scale, while also being explicit that its internal and external interfaces are unstable;
- the AWS SDK for Rust shows that real SDKs include configuration, examples, and maintenance/support posture; 
- and Oxide’s Rust SDK/CLI repo shows an especially practical Rust-native pattern: one source OpenAPI contract feeding a CLI, SDK, and mock library, with checked-in generated code and CI synchronization.

Together these signals justify treating SDK productization as a **frontier-worthy ecosystem seam** rather than leaving Rust API products as a pile of generator templates, auth examples, runtime builders, checked-in generated files, and support prose.

## Stack layers

### 1) SDK Surface: the public consumer product boundary
SDK Surface owns the **declared public SDK family**:
- package identities
- operation identities
- high-level versus low-level API posture
- runtime/auth/config profile attachments
- CLI/mock companions
- generated-versus-hand-written ownership boundaries
- checked examples and diffs

SDK Surface answers questions like:
- “What Rust API products does this project officially ship?”
- “Which methods/commands are part of the supported surface?”
- “Which crates are generated, hand-written, or mixed?”
- “How does the CLI or mocking crate relate to the library?”

Design rule: **SDK surface must not be inferred only from generated code, README examples, or raw service contracts alone**.

### 2) Schema Contract + Service / Protocol imports: upstream truth
Schema Contract, Service Surface, and Protocol/Productization layers own the **upstream contract truth**:
- machine-readable shape and compatibility
- service/route/operation identity
- protocol/transport/wire posture
- compatibility reasoning and migration attachments

This layer answers questions like:
- “What upstream contract did this SDK derive from?”
- “Was a change wire-level, schema-level, or SDK-level?”
- “Which parts of the SDK are direct projections and which are product sugar?”

Design rule: **the SDK product layer imports upstream contract truth; it does not redefine it.**

### 3) Identity Productization + Runtime Settings: activation truth
Identity Productization, Credentials, and Runtime Settings own the **activation posture** that turns an SDK surface into a usable product:
- auth modes and principal assumptions
- signer/session/token-provider posture
- environment/profile/endpoint selection
- timeout/retry/proxy/TLS settings
- secret-source activation

This layer answers questions like:
- “How does the SDK authenticate?”
- “Which runtime knobs are official?”
- “What is actually required in local, CI, staging, or prod usage?”
- “Which behavior is generator output and which is runtime configuration?”

Design rule: **SDK support must not silently depend on undocumented environment variables, signer hooks, or secret-manager conventions.**

### 4) Library Productization + Release Truth + Distribution Contract: shipped product truth
Library Productization owns the crate-as-product boundary, Release Truth owns what was actually published or released, and Distribution Contract owns what users actually installed.

This layer answers questions like:
- “Which SDK crates or binaries were released?”
- “What provenance and package identity did they have?”
- “Was the CLI installed from binaries, packages, or source?”
- “What release attachments justify the support story?”

Design rule: **source contract truth and shipped SDK truth are related but distinct.**

### 5) Support Envelope + DocProof: support and docs truth
Support Envelope and DocProof own the **supportability boundary** for SDKs:
- target/runtime assumptions
- docs.rs/rustdoc posture
- checked examples and guides
- maintenance/support windows
- source-build versus released-binary differences

This layer answers questions like:
- “Do the docs match the actually supported SDK surface?”
- “Which runtime/platform assumptions are official?”
- “Were the examples checked?”
- “What support or maintenance posture applies?”

Design rule: **SDK support claims must not be inferred from one README snippet or one successful example run.**

### 6) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Release / distribution** consumers can attach SDK packs to crate and binary releases.
- **Support / incident** consumers can reason about config/auth/example truth without reverse-engineering codegen.
- **Atlas / learning / assistants** can describe credible Rust SDK lanes without pretending one generator solved everything.
- **Migration / policy / trust** consumers can compare SDK changes without confusing protocol diffs, SDK sugar, and release/support posture.

Design rule: **consumers import selected evidence; they do not become the new truth engine for SDK products.**

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust API SDK generator.”
It is a portable, reviewable stack with clear boundaries:

1. **SDK family truth first**
   - prove `sdk-surface/v0`, `sdk-operation-map/v0`, and generated/hand-written boundaries on one real SDK family;
2. **Upstream contract alignment second**
   - attach OpenAPI/Smithy/protobuf/service/protocol inputs without pretending they are identical;
3. **Auth/config/runtime third**
   - add runtime/auth profiles and checked examples so support stops living only in builder code and setup docs;
4. **Release/support fourth**
   - attach library/release/distribution/support truth so the product surface survives publication and install;
5. **Consumers fifth**
   - prove release/support/atlas/migration consumers can import the stack honestly.

An eventual aggregate artifact may exist, but it should be a **thin pack of referenced artifacts**, not a new mega-schema that erases the lane boundaries.

## Candidate artifact family
A worthy contribution should stay thin and linked.
A plausible family is:
- `sdk-surface/v0`
- `sdk-operation-map/v0`
- `sdk-runtime-profile/v0`
- `sdk-auth-profile/v0`
- `sdk-check-report/v0`
- `sdk-diff-report/v0`
- `sdk-pack/v0`

These artifacts should mostly reference lower-layer packs and checked attachments instead of replacing them.

## Reference CLI shape
- `cargo sdkcheck surface`
  - emit `sdk-surface/v0`
- `cargo sdkcheck profiles`
  - emit `sdk-runtime-profile/v0` and `sdk-auth-profile/v0`
- `cargo sdkcheck examples`
  - emit checked example attachments and `sdk-check-report/v0`
- `cargo sdkcheck diff --against <ref|version|path>`
  - emit `sdk-diff-report/v0`
- `cargo sdkcheck pack`
  - produce `sdk-pack/v0`

This should remain a **composition layer**, not a hosted platform, auth framework, or transport runtime.

## Ranked first execution lanes
1. **OpenAPI SDK family lane**
   - best first exporter because Rust already has strong code-first and client-generation components (`utoipa`, `progenitor`, OpenAPI Generator) and a concrete Oxide-style CLI/SDK/mock example.
2. **Smithy / large-SDK lane**
   - proves the stack can represent high-level and low-level APIs, runtime/auth layers, and release/support posture without becoming AWS-specific.
3. **gRPC/protobuf lane**
   - proves the stack does not collapse everything into HTTP/OpenAPI assumptions.
4. **Release/support lane**
   - proves docs, publication, binaries, and install reality are part of the SDK product.
5. **Consumer lane**
   - proves migration/support/atlas/release consumers gain value from the artifacts.

## Non-goals
- one universal API generator;
- one universal HTTP/RPC runtime;
- one hosted SDK platform or control plane;
- flattening source contracts, SDK products, auth/config posture, shipped artifacts, and support claims into one fake “SDK readiness” schema;
- pretending checked-in generated code, green CI, or one example run alone proves SDK support.

## Archive implications
- The archive should now treat **SDK Surface + Schema Contract + Identity Productization + Runtime Settings + Library Productization/Release Truth/Support Envelope imports** as a coupled **SDK Productization Stack**.
- Future revisions should prefer **reviewable SDK family identity, source-contract alignment, auth/config/runtime truth, release/support truth, and consumer proofs** over another generator fork, transport wrapper, auth helper, or provider-specific SDK convenience layer.
- When library/service/protocol/release/support work cites “SDK support,” they should import **SDK surface**, **upstream contract truth**, **auth/config activation**, **release/distribution truth**, and **support truth** separately.
