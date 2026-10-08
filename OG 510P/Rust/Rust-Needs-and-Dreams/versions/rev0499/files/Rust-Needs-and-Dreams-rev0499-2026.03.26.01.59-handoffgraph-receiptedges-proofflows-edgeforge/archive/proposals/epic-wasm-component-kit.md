# Epic Proposal: Wasm Component Kit (`cargo wit`)

## One-sentence pitch
Turn Rust Wasm components into first-class, diffable, publishable artifacts: capture WIT/package identity, build lane, import satisfaction, compatibility drift, and publication evidence in one portable pack.

## Deliverables
- `cargo-wit` reference implementation
- Schemas:
  - `component-subject/v0`
  - `wit-resolution-lock/v0`
  - `component-surface-report/v0`
  - `component-host-requirement-profile/v0`
  - `composition-plan/v0`
  - `composition-run-report/v0`
  - `component-compat-report/v0`
  - `component-publish-report/v0`
  - `component-vectors/v0`
  - `component-pack/v0`
- Adapters/integrations:
  - plain `cargo build --target=wasm32-wasip2`
  - `cargo-component`
  - `wit-bindgen`
  - `wasm-tools`
  - `wkg` / `wasm-pkg-tools`
  - Warg / OCI publication lanes
- Docs:
  - WIT compatibility-policy guide
  - composition and host-requirement reason-code reference
  - release / registry / CI patterns

## Why now (signals)
- Rust’s 2026 flagships explicitly say Wasm Components are a focus area and call out adding/stabilizing three compiler targets plus Wasm-specific language experimentation.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Rust 1.82 made `wasm32-wasip2` Tier 2, so direct compiler support for WASI 0.2 components is no longer exotic.
  https://blog.rust-lang.org/2024/11/26/wasip2-tier-2/
- The official component-model guide now says Rust has first-class component targets, shows `cargo build --target wasm32-wasip2`, says `cargo-component` is being deprecated as native tooling can be used directly, and also notes that the toolchain cannot yet auto-generate custom-WIT bindings. That is exactly the sort of mixed transition state that benefits from an explicit contract layer.
  https://component-model.bytecodealliance.org/language-support/building-a-simple-component/rust.html
- `cargo component` remains experimental, still carries important adaptation/package behavior that upstream Cargo does not yet replace, still publishes to Warg, and still requires a rust-analyzer override in some workflows.
  https://github.com/bytecodealliance/cargo-component
- `wasm-pkg-tools` / `wkg` already support OCI and Warg, ship a shared config format, and generate a standardized `wkg.lock` intended for reuse by other language-specific tooling, which makes a cross-tool contract layer much more plausible.
  https://docs.rs/crate/wasm-pkg-common/0.13.0
- Warg already exists as a reference registry protocol/server/client for components and interfaces, which means publication identity is real enough to deserve first-class artifacts.
  https://github.com/bytecodealliance/registry

## Non-goals
- Replacing `cargo-component` or forcing all users onto one builder
- Standardizing one universal host model or one universal registry service in v0
- Collapsing browser `wasm-bindgen` workflows and component-model workflows into one vague mega-tool
- Solving all Wasm packaging, runtime, policy, and security questions at once

## Strategic value
This kit has high leverage because it connects:
- Rust’s official Wasm Components push,
- plugin-style architecture and sandboxed extension points,
- multi-language package/registry workflows,
- release evidence and provenance,
- and future host/runtime/policy tooling.

It gives the archive a concrete answer to a growing seam: Wasm Components are becoming mainstream in Rust, but their artifact boundaries are still too ad hoc.

## Milestones
Use [`design/wasm-component-pilot-program.md`](../design/wasm-component-pilot-program.md) as the ranked rollout for this epic:
1. native Cargo export lane,
2. `cargo-component` bridge lane,
3. composition / host-requirement lane,
4. registry / package identity lane,
5. runtime / release / policy consumer lane.

Schema maturity should follow the pilots rather than race ahead of them:
- **v0**: `component-subject` + `component-surface-report` + `component-pack` for native Cargo and inspection-first lanes
- **v0.2**: add `wit-resolution-lock`, bridge-lane attachments, and `composition-*` reports
- **v0.3**: add `component-publish-report` with OCI/Warg/WIT identity attachments
- **v1**: stabilize consumer imports for Release / Policy / Support / Plugin / Runtime consumers
