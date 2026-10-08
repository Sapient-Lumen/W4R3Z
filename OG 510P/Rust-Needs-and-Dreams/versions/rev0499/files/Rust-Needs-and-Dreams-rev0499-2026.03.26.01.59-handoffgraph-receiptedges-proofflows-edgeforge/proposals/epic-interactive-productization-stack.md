# Epic proposal: Interactive Productization Stack (`cargo interactive-product`, `interactive-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **interactive and real-time products** that links **asset/content truth**, **shader/backend/device truth**, **window/input/frame-loop truth**, **runtime/performance activation**, and **shipped/support truth** into one portable review boundary without pretending one engine, one renderer, one UI toolkit, or one shader lane has already won.

## Why this is now worth doing
Rust’s interactive story is now strong enough that the missing contribution looks like a **product boundary above the ingredients** rather than another ingredient:
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference even as LLM/editor tooling rises. That increases the value of machine-usable product artifacts over README folklore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Bevy 0.17 and 0.18 make the gap more obvious, not less. Bevy now has serious tooling-facing UI work (Feathers widgets for the upcoming editor), first-party camera-controller lanes, and an experimental real-time raytraced renderer with ongoing improvements. That means “interactive Rust” now spans games, tools, and editors rather than one narrow game-engine story.
  https://bevy.org/news/bevy-0-17/
  https://bevy.org/news/bevy-0-18/
- `wgpu` is explicit that it is a cross-platform safe Rust graphics API running on Vulkan, Metal, D3D12, OpenGL, WebGL2, and WebGPU on wasm, and its docs expose backend selection via `WGPU_BACKEND`. Backend/runtime selection is already a public contract surface, not a hidden implementation detail.
  https://docs.rs/wgpu/
  https://docs.rs/wgpu/latest/wgpu/struct.Backends.html
- `winit`, `egui`, and Slint sharpen the runtime split rather than resolving it. `winit` calls itself a low-level brick in a hierarchy of libraries; `egui` is explicit about immediate-mode per-frame UI; and Slint’s MCU docs describe software-rendered super-loop setups with no GPU. That is exactly the pattern where Rust needs a portable review layer above multiple real lanes.
  https://docs.rs/crate/winit/latest
  https://docs.rs/egui/latest/egui/
  https://docs.slint.dev/latest/docs/rust/slint/docs/mcu/
- rust-gpu also reinforces the point from the shader/build side. `spirv-builder` exists to build shader crates and the docs explicitly require a very specific nightly toolchain / exact-version coordination. Shader truth is already its own product lane.
  https://docs.rs/spirv-builder/latest/spirv_builder/
  https://rust-gpu.github.io/rust-gpu/book/writing-shader-crates.html

What is still missing is the **stack-level boundary that says one interactive product subject was reviewed with these assets, these shader/backend/device paths, these frame/input/runtime modes, these activated settings, these shipped/downstream artifacts, and these bounded support conclusions**.

## Working name
- CLI: `cargo interactive-product`
- primary artifact: `interactive-product-pack/v0`

## Scope
### This epic should own
- interactive product subject identity
- imported media / offload / client-app / runtime-settings / observability / distribution / support attachments
- diffable review points across asset/source posture, shader/backend/device/fallback posture, frame/input/update behavior, activated runtime/perf settings, and shipped/support claims
- bounded release / support / atlas / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- a universal game engine or editor platform
- a universal renderer abstraction
- a universal asset pipeline
- a benchmark theater dashboard
- a fake one-number “interactive readiness” badge
- flattening games, reactive desktop tools, embedded HMIs, and visualization apps into one runtime model

## Candidate artifact family
### `interactive-product-brief/v0`
Why the product exists, intended consumer set, interactive lanes in scope, supported environments, freshness budget, and review status.

### `interactive-product-subject/v0`
The exact app/workspace/release/deployment subject, imported media/offload/client/runtime/distribution/support surfaces, comparison base, and environment/support scope.

### `interactive-product-pack/v0`
The portable review bundle linking:
- imported `media-surface` / asset-catalog / content-source attachments
- imported shader/backend/device/fallback attachments
- imported window/input/frame/update attachments
- imported runtime-settings / observability / perf attachments
- imported distribution / support / docs attachments
- local notes, waivers, caveats, and integrity metadata

### `interactive-product-diff/v0`
What changed between two review points, with separate sections for:
- asset/content/catalog and source posture
- shader/backend/device/fallback posture
- window/input/frame/update behavior
- runtime/perf/quality activation
- shipped/install/download/cache posture
- support/docs/platform claims

### `interactive-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support / incident review
- atlas / adoption review
- distribution / packaging review
- assistant / editor rendering

## Recommended rollout
1. local/bundled asset lane
2. shader / backend / fallback lane
3. frame / input / presentation lane
4. runtime / performance activation lane
5. support / release / customer-handoff lane

This should be driven by [`design/interactive-productization-pilot-program.md`](../design/interactive-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer renderer wrapper,
- a nicer asset helper,
- a nicer event-loop integration,
- a nicer profiling HUD,
- or a nicer Bevy/wgpu starter template.

An epic contribution here instead gives Rust one **portable interactive product contract** above those lanes.
That is strategically different because it can:
- make release/support/atlas reviews share the same subject and evidence boundary;
- let engines, renderers, UI toolkits, and shader pipelines stay specialized without pretending any one defines the whole product;
- keep asset truth, shader/backend truth, frame-loop truth, runtime/perf activation, and shipped/support truth distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping build scripts, engine feature flags, env vars, shader folders, profiler screenshots, and issue-thread archaeology.

## Design principles
- **Asset truth is not renderer truth.**
- **Shader/backend truth is not frame-loop truth.**
- **Interactive tools/editors are not the same runtime shape as continuously-rendered games.**
- **Runtime/perf settings are part of the support surface.**
- **Downloaded/cached content is not the same as shipped content.**
- **Support/docs/platform caveats are part of the product boundary.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact interactive product subject,”
- “these are the assets/content families and source postures we actually support,”
- “these are the shader/backend/device/fallback combinations that were actually exercised,”
- “these are the frame/input/update/runtime modes that materially changed behavior,”
- “these are the settings and evidence attached to performance or quality claims,”
- “these are the shipped, downloaded, or cached artifacts,”
- “these are the docs/support/platform caveats,”
- “this is what changed from the prior review,”
- and “this is what release/support/atlas consumers may safely conclude,”

without inventing a bespoke readiness schema for every Bevy, wgpu, Slint, egui, or custom runtime repository.

## Read this with
- `gaps/interactive-apps-games-and-real-time-rendering-productization-contracts.md`
- `design/interactive-productization-stack.md`
- `design/interactive-productization-pilot-program.md`
- `design/media-surface-kit.md`
- `design/offload-surface-kit.md`
- `design/client-app-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
