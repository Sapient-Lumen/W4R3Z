# Design: Wasm Component pilot program

The archive already had the right instinct: Rust WebAssembly Components are strategically important, but the ecosystem still lacked an **execution order** for turning that importance into a credible contribution.

Current signals sharpen the problem:
- Rust’s 2026 flagships explicitly include **Wasm Components** and call out adding/stabilizing targets plus experimenting with Wasm-specific language features.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `wasm32-wasip2` is already Tier 2, so plain-toolchain component builds are not niche anymore.
  https://blog.rust-lang.org/2024/11/26/wasip2-tier-2/
- The official component-model Rust guide now says Rust has first-class component targets, shows `cargo build --target wasm32-wasip2`, and explicitly says `cargo-component` is being deprecated as native tooling can be used directly. But the same guide also says the toolchain cannot yet auto-generate bindings for custom WIT, so `wit-bindgen` still matters.
  https://component-model.bytecodealliance.org/language-support/building-a-simple-component/rust.html
- `cargo component` is still experimental, still supports important non-WASI/custom-WIT workflows, still carries adapter behavior, can publish to a Warg registry, and still asks rust-analyzer users to override the check command.
  https://github.com/bytecodealliance/cargo-component
- `wkg` / `wasm-pkg-tools` already provide shared configuration and a standardized `wkg.lock`, explicitly intended to be usable by other language-specific tooling and to fetch/publish components through OCI or Warg registries.
  https://docs.rs/crate/wasm-pkg-common/0.13.0

That combination means the worthy contribution is **not** “pick the winner” between plain Cargo and `cargo-component`.

It is the transition-safe contract layer that keeps:
- native Cargo component builds,
- custom-WIT binding generation,
- composition/import satisfaction,
- registry/package identity,
- and runtime/consumer handoff

reviewable while the ecosystem is still converging.

## Execution posture
Treat this file as the ranked rollout for:
- [`design/wasm-component-kit.md`](./wasm-component-kit.md)
- [`proposals/epic-wasm-component-kit.md`](../proposals/epic-wasm-component-kit.md)
- [`gaps/wasm-component-workflows-and-wit-packaging.md`](../gaps/wasm-component-workflows-and-wit-packaging.md)

The kit should start by exporting truth from real lanes before it tries to standardize compatibility policy or publication workflow broadly.

## Pilot 1 — Native Cargo export lane
**Who this is for:** teams building straightforward WASI 0.2 components with plain Cargo.

**Why this should be first**
- It is the smallest lane aligned with the official direction of travel.
- It proves the archive understands the post-`cargo-component` transition instead of staying anchored to older assumptions.
- It keeps the first pack grounded in what Rust upstream already treats as mainstream: `wasm32-wasip2`, `wit_bindgen`, and `wasm-tools` inspection.

**Minimum output**
- `component-subject/v0`
- `component-surface-report/v0`
- `component-vectors/v0` (small examples only)
- attached `wasm-tools component wit` / inspection output

**Success condition**
A maintainer can answer, from one bundle, “what world/interface did we intend, what component did plain Cargo emit, and what does inspection say it actually exports/imports?”

## Pilot 2 — `cargo-component` bridge lane
**Who this is for:** teams using non-WASI WIT interfaces, dependency-resolution through `Cargo.toml`, or adaptation behavior not yet covered by plain `wasm32-wasip2` workflows.

**Why it matters**
- The official guide points toward native tooling, but `cargo-component` still owns real workflows today.
- The archive must not confuse “directionally being deprecated” with “already irrelevant.”
- This lane is where adapter truth, generated-binding provenance, and editor/check-command posture become operationally important.

**Minimum output**
- `component-subject/v0` with explicit build lane
- `wit-resolution-lock/v0`
- `component-surface-report/v0`
- adapter attachment/digest when used
- consumer note for rust-analyzer / `cargo component check` posture when relevant

**Success condition**
A maintainer or reviewer can tell exactly which parts of the build came from upstream Cargo versus `cargo-component` behavior, and where migration back toward native tooling is or is not currently possible.

## Pilot 3 — Composition and host-requirement lane
**Who this is for:** teams whose components are not self-contained after build, or whose runtime host must satisfy/import interfaces explicitly.

**Why it matters**
- Composition is where component workflows stop looking like ordinary crate workflows.
- This is the point where import satisfaction, adapter use, and host requirements need attachable evidence instead of comments and tribal knowledge.

**Minimum output**
- `component-host-requirement-profile/v0`
- `composition-plan/v0`
- `composition-run-report/v0`
- explicit unresolved-import state when composition did not happen or did not finish

**Success condition**
A host/runtime author can answer “what imports must I satisfy, what was assumed to be runtime-provided, and what exactly succeeded or failed during composition?”

## Pilot 4 — Registry / package identity lane
**Who this is for:** teams fetching or publishing WIT/components through `wkg`, OCI, or Warg registries.

**Why it matters**
- The registry story is already plural.
- `wkg.toml`, `wkg.lock`, namespace mapping, protocol preference, and publish identity are exactly the sort of layered facts that disappear when teams rely on build logs alone.
- This is also the point where Rust-specific tooling has to stay honest about cross-language package identity.

**Minimum output**
- `wit-resolution-lock/v0` with `wkg`/registry attachments
- `component-publish-report/v0`
- explicit protocol / namespace / registry mapping truth
- attached digests for published components and WIT

**Success condition**
A downstream consumer can tell which package identity was resolved, which registry/protocol was used, and whether the published component still matches the reviewed build/composition subject.

## Pilot 5 — Runtime / release / policy consumer lane
**Who this is for:** runtime operators, plugin hosts, policy engines, release systems, and support/reliability consumers.

**Why it comes last**
- Consumers should import component truth only after the lower layers are stable enough to export honestly.
- This is where many ecosystems overreach early and invent a giant “component platform status” dashboard.

**Minimum output**
- stable consumer-import profile docs
- explicit mapping from `component-pack/v0` into Release Pipeline / Policy Kit / Support Envelope / Plugin Surface / Runtime Capability consumers
- visible `UNKNOWN` / `NOT_EVALUATED` / `INCOMPLETE` outcomes where imports are partial

**Success condition**
Other kits can consume component evidence without quietly becoming the new source of truth for WIT/package/build/composition identity.

## Guardrails
- **Do not standardize a universal host model in v0.** Host requirements should stay descriptive before they become prescriptive.
- **Do not collapse Cargo package identity, WIT package identity, component artifact identity, and published package identity.**
- **Do not pretend native Cargo and `cargo-component` are already equivalent.**
- **Do not route browser-focused `wasm-bindgen` stories through this lane.**
- **Do not let policy/release consumers define the base schema.** They import it later.

## Archive decision
The next credible Wasm-component move is now a ranked pilot program:
1. native Cargo export lane,
2. `cargo-component` bridge lane,
3. composition/host-requirement lane,
4. registry/package identity lane,
5. runtime/release/policy consumer lane.

That is a stronger and more realistic execution order than another wrapper around `cargo-component`, another WIT helper crate, or a vague call to make components “first-class”.
