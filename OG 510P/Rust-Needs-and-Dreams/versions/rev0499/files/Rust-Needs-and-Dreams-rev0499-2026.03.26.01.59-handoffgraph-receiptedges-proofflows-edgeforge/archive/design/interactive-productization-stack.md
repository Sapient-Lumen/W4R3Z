# Design note: Interactive Productization Stack (Media Surface + Offload Surface + Client App Surface + Runtime Settings + Observability + Distribution Contract + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust asset/media surfaces, shader/backend/device truth, window/input/frame-loop behavior, runtime/performance activation, shipped/discovered/downloaded artifacts, and support/docs claims so the ecosystem can make **real-time apps, games, visualization tools, and interactive editors** reviewable without anointing one engine, one renderer, one UI toolkit, or one shader lane as the answer.

This is **not** a new top-level mega-framework.
It is a stack note explaining how existing archive pieces should compose:
- [`design/media-surface-kit.md`](./media-surface-kit.md)
- [`design/offload-surface-kit.md`](./offload-surface-kit.md)
- [`design/client-app-surface-kit.md`](./client-app-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)

## Why this note is needed now
Rust’s current signals no longer say only “games and graphics are possible.” They say Rust already has serious interactive ingredients, but still lacks the **productization layer above them**:
- the 2025 State of Rust survey still says online docs are the preferred canonical reference even as AI/editor tooling keeps rising, which means ecosystems increasingly need reviewable machine-usable product surfaces instead of README folklore;
- Bevy now clearly positions itself as a cross-platform engine/app framework, with scenes that can be saved, loaded, and hot-reloaded, assets that can be hot-reloaded, and support across Windows, macOS, Linux, Web, iOS, and Android;
- Bevy 0.17 and 0.18 make the product boundary more obvious, not less: Bevy now has serious tooling/editor-facing widget work, first-party camera-controller lanes, and ongoing experimental high-end rendering work like Solari, which means interactive Rust is already spanning games, tools, and editors rather than one narrow runtime story;
- `wgpu` is now a serious cross-platform graphics substrate over Vulkan, Metal, D3D12, OpenGL, WebGL2, and WebGPU on wasm, and it documents both explicit backend/environment selection and the uncomfortable truth that supported WGSL behavior still depends on how and where it is translated;
- Naga is already a real translation/validation layer, which means shader-language posture and backend portability are first-class contract questions rather than implementation trivia;
- rust-gpu already treats shader crates as a distinct build lane with `spirv-builder` / `build.rs` or manual `.cargo/config` setup, and it requires exact toolchain coordination with the host application;
- window/input/frame behavior is already product truth, not just engine internals: `winit` explicitly positions itself as a low-level brick, and Bevy’s own `WinitSettings::game()` versus `desktop_app()` modes show that update cadence, redraw policy, and power posture materially change what an “interactive app” is;
- renderer/runtime diversity is real across targets: `egui` explicitly describes a per-frame immediate-mode integration contract, while Slint spans embedded/desktop/mobile and documents MCU setups where there is no GPU and software rendering plus a user-driven super loop become the truth, so Rust already has multiple legitimate interactive runtime shapes rather than one obvious default.

Together these signals justify treating interactive shipping quality as a **frontier-worthy ecosystem seam** instead of leaving Rust real-time work split across engine features, shader build glue, asset conventions, window loops, perf dashboards, and release notes.

## Stack layers

### 1) Media Surface: declared asset and content truth
Media Surface owns the **declared interactive asset boundary**:
- scenes, prefabs, dynamic scene/state exports,
- textures, meshes, materials, fonts, audio, video, subtitle, and generated asset lanes,
- asset source posture (embedded, local filesystem, downloaded, cached),
- processing/post-import assumptions,
- and checked asset evidence.

Media Surface answers questions like:
- “Which asset families are part of the supported product surface?”
- “Which assets are shipped in the binary, loaded locally, or fetched at runtime?”
- “What content assumptions are stable enough for support, migration, and release review?”

Design rule: **asset truth must stay separate from shader truth, frame-loop truth, and support truth**.
An image/audio/scene catalog is not the same thing as runtime rendering posture.

### 2) Offload Surface: shader, backend, device, and fallback truth
Offload Surface owns the **actual rendering/compute contract**:
- shader languages and transformation paths,
- backend and device selection,
- required capabilities and feature gates,
- CPU/software or downgraded fallbacks,
- backend-sensitive bugs/waivers,
- and checked backend/device evidence.

Offload Surface answers questions like:
- “Which shader sources and backend paths are actually supported?”
- “Which rendering claims depend on Vulkan/Metal/DX12/WebGPU/WebGL2 or software fallback?”
- “What is stable shader truth versus best-effort translation truth?”

Design rule: **backend and shader posture must not be smuggled inside one vague ‘graphics supported’ claim**.

### 3) Client App Surface: window, input, frame-loop, and presentation truth
Client App Surface owns the **interactive runtime boundary**:
- windowing and display identities,
- event-loop and wakeup/redraw posture,
- input families and priority rules,
- game-mode versus desktop-app versus low-power behavior,
- presentation/update cadence,
- and checked platform behavior.

This layer answers questions like:
- “Is this a continuously-rendered game loop, a reactive desktop tool, or a mixed interactive app?”
- “Which input and focus behaviors are part of the promise?”
- “Which parts of the experience depend on one platform/windowing stack?”

Design rule: **window/input/frame-loop truth must not be inferred from screenshots or engine marketing pages**.

### 4) Runtime Settings + Observability: activation and evidence truth
Runtime Settings and Observability together own the **activation/evidence boundary**:
- quality/performance presets,
- backend, adapter, and feature selection,
- hot-reload and asset-cache toggles,
- telemetry/profiling/frame graphs,
- content/debug overlays,
- and runtime reports that correlate user-visible behavior with activated settings.

This layer answers questions like:
- “Which settings materially changed what the app rendered or how fast it ran?”
- “How were assets discovered, cached, or embedded?”
- “What evidence exists for frame times, backend choice, and runtime degradations?”

Design rule: **runtime-quality and performance stories must not live only in environment-variable docs, profiler screenshots, or issue comments**.

### 5) Distribution Contract + Support Envelope: shipped artifact and promise truth
Distribution Contract and Support Envelope own the **what actually shipped and what is actually supported** boundary:
- source-build versus prebuilt versus store/package-manager paths,
- whether assets are embedded, bundled, downloaded, or cached,
- platform/runtime floors and GPU/software-renderer support posture,
- checked docs/examples/install snippets,
- and release/support attachments that explain what interactive features are truly promised.

This layer answers questions like:
- “What content, shaders, and renderer assumptions shipped with this product?”
- “Which platforms or backends are officially supported versus merely tolerated?”
- “What can support, QA, release review, and downstream packagers legitimately conclude?”

Design rule: **a demo video, one benchmark, or one successful build is not the support contract**.

### 6) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **release/review** consumers can attach asset, backend, runtime, and support evidence to real releases;
- **support/incident** consumers can reconstruct how a real-time product was configured and rendered instead of guessing from bug reports;
- **atlas/learning** consumers can compare serious Rust interactive stacks without pretending engines and UI toolkits are interchangeable;
- **LLM/editor/documentation** consumers can read a portable interactive story instead of scraping engine-specific prose and repo glue.

Design rule: **consumers import selected evidence; they do not redefine the source-of-truth layers**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the one true Rust game engine” or “the universal renderer wrapper.”
It is a portable, reviewable stack with clear boundaries:

1. **asset/media truth first**
   - prove scene/texture/material/font/audio/shader asset families, source posture, and checked content evidence on one real product;
2. **shader/backend truth second**
   - attach backend/device/shader/fallback reports without flattening them into the asset catalog;
3. **window/input/frame truth third**
   - make continuous-vs-reactive behavior, wakeups/redraws, and input families explicit and diffable;
4. **runtime/perf activation fourth**
   - make quality presets, hot reload, cache/backend selection, and frame/perf evidence explicit;
5. **distribution/support consumers fifth**
   - prove release, support, docs, and atlas consumers can import the artifacts without reverse-engineering the engine or repo layout.

An eventual aggregate artifact may exist, but it should be a **thin referenced pack** such as `interactive-product-pack/v0`, not a new truth engine that erases asset, shader, client, runtime, and support boundaries.

## Ranked first execution lanes
1. **Bevy desktop asset lane**
   - best first exporter because it can prove local assets, hot reload, scene/content identities, and runtime asset-source posture without immediately forcing every backend/platform story.
2. **wgpu native/web shader lane**
   - proves shader/backend/device/fallback truth and makes native-vs-browser differences explicit.
3. **interactive tool/editor lane**
   - proves game-mode versus desktop-app/low-power posture, UI overlays, and mixed app/tool behavior can be modeled honestly.
4. **embedded/mobile/software-renderer lane**
   - proves the stack still works when there is no full GPU path, when software rendering matters, or when event loops are more constrained.
5. **release/support/customer-handoff lane**
   - proves shipped/bundled/downloaded asset posture and supported backend/platform claims can travel into real release and support workflows.

## Non-goals
- one universal game engine or app framework;
- one universal renderer or shader abstraction;
- another asset manager, hot-reload gimmick, or benchmark-only dashboard;
- flattening asset/media truth, shader/backend truth, frame-loop/input truth, runtime/perf activation, and support claims into one fake “interactive readiness” schema;
- pretending games, tools, visualization apps, and embedded UI runtimes all have the same product boundary.

## Archive implications
- The archive should now treat **Media Surface + Offload Surface + Client App Surface + Runtime Settings + Observability + Distribution Contract + Support Envelope** as a coupled **Interactive Productization Stack** in frontier discussions.
- Future revisions should prefer **asset/media truth, shader/backend/device truth, window/input/frame-loop truth, runtime/perf activation, and shipped/support truth** over another engine bake-off, renderer wrapper, asset manager, shader convenience layer, or benchmark-only graphics story.
- When Client, Release, Support, Atlas, Scientific, Firmware, or Documentation work cites interactive readiness, they should import **asset truth**, **shader/backend truth**, **frame/input truth**, **runtime/perf truth**, and **support truth** separately.

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Bevy product/release signals:
  https://bevy.org/
  https://bevy.org/news/bevy-0-17/
  https://bevy.org/news/bevy-0-18/
  https://docs.rs/bevy/latest/bevy/asset/struct.AssetServer.html
  https://docs.rs/bevy/latest/bevy/asset/macro.embedded_asset.html
  https://bevy.org/examples/window/low-power/
- wgpu / Naga / shader portability signals:
  https://docs.rs/wgpu/latest/wgpu/
  https://github.com/gfx-rs/wgpu
  https://wgpu.rs/doc/naga/index.html
  https://rust-gpu.github.io/rust-gpu/book/writing-shader-crates.html
- windowing / UI runtime signals:
  https://docs.rs/crate/winit/latest
  https://docs.rs/egui/latest/egui/
  https://docs.slint.dev/latest/docs/slint/
  https://docs.rs/slint/latest/slint/docs/mcu/
