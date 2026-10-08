# Design: Interactive Productization Pilot Program (Asset Truth → Shader/Backend Truth → Frame/Input Truth → Runtime/Perf Activation → Support/Release Consumers)

## Goal
Turn the **Interactive Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust interactive products are built, profiled, shipped, and supported?

The pilot program should not chase a universal engine or rendering framework.
It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Interactive Rust work is unusually easy to romanticize.
A pretty demo, a benchmark graph, one cross-platform screenshot, or one polished editor/tooling preview can hide all the things that actually determine whether a product is shippable:
- what content is shipped, embedded, downloaded, or cached,
- which backend/device/shader paths really worked,
- whether the app is a continuously-rendered loop or a reactive desktop tool,
- which runtime settings changed the behavior,
- and what the project actually supports when users show up with mismatched GPUs, OSs, or asset caches.

A credible plan therefore needs to decide:
- when asset/media truth is already enough,
- when backend/shader truth must be attached,
- when frame/input/update behavior becomes part of the contract,
- when runtime/perf activation evidence is required,
- and which release/support consumers justify graduation.

## Principles
1. **Start from shipped content truth, not rendering ideology**
   - a pack that proves what assets exist and how they are sourced is worth more than a vague renderer manifesto.
2. **Keep asset truth, backend truth, and frame-loop truth separate**
   - they travel together in products, but they are not the same source of truth.
3. **Support the downgrade paths honestly**
   - software renderers, downlevel backends, WebGL fallbacks, and reduced-quality modes are real product truth.
4. **Runtime settings are part of the support story**
   - adapter selection, hot reload, caching, perf overlays, and present/update modes should graduate before big platform claims do.
5. **Cross-target claims need evidence**
   - native, browser, mobile, and embedded support should be reviewable, not implied by a homepage bullet list.
6. **Consumers import; they do not reinterpret**
   - release, support, atlas, docs, and incident consumers should import artifacts instead of becoming the hidden truth engine.

## Common artifacts this program should drive
- `interactive-lane-brief/v0` — declare which pilot lane is being exercised, scope, targets, and non-goals.
- `asset-runtime-brief/v0` — bounded summary of asset families, sources, embedding/downloading/cache posture, and content-processing assumptions actually activated.
- `shader-backend-brief/v0` — explicit summary of shader languages, translation paths, backends, devices, and fallback posture exercised.
- `frame-loop-brief/v0` — explicit summary of event-loop, wakeup/redraw, input, and presentation/update-mode behavior for the lane.
- `interactive-runtime-brief/v0` — quality/perf/backend/settings activation summary with links to runtime evidence.
- `interactive-consumer-handoff/v0` — what release/support/docs/atlas consumers may conclude from the pilot and what remains out of scope.
- `interactive-readiness-scorecard/v0` — not a fake maturity score; a lane-by-lane checklist showing which truths exist and which remain absent.
- `interactive-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Local/bundled asset lane
**Why first:** it proves the most universal interactive claim with the least platform coercion.

**Concrete scope**
- scene/prefab/texture/material/font/audio/shader identities where relevant,
- bundled versus embedded versus local-on-disk asset posture,
- hot-reload or content-update posture when present,
- content dependencies and load-state behavior,
- checked docs/examples that state the asset story honestly.

**Graduation bar**
- the pack can explain what content exists, where it comes from, what ships in the artifact, and what remains runtime-discovered or illustrative.

### 2) Shader / backend / fallback lane
**Why second:** once content truth is real, the next hidden source of pain is whether rendering claims depend on one backend or translation path.

**Concrete scope**
- shader language families and generated artifacts,
- backend/device combinations exercised,
- required features/capabilities,
- software/downlevel/browser fallbacks,
- translation/validation waivers and limitations,
- backend-specific evidence attachments.

**Graduation bar**
- a reviewer can tell which shader/backend/device combinations actually ran, what fell back, and what remained best-effort.

### 3) Frame / input / presentation lane
**Why third:** this is where real-time apps, games, and tools start to diverge sharply from one another.

**Concrete scope**
- continuous rendering versus reactive redraw posture,
- input families and focus/cursor behavior,
- present/update cadence,
- low-power or desktop-app modes,
- windowing/event-loop assumptions,
- checked platform behavior across at least one non-trivial target pair.

**Graduation bar**
- the pack can explain what kind of interactive runtime it is and how user input and redraw behavior actually worked.

### 4) Runtime / performance activation lane
**Why fourth:** performance and quality are often the hidden runtime contract for interactive products.

**Concrete scope**
- backend selection settings,
- quality/performance presets,
- cache and hot-reload settings,
- frame-time/profiling/diagnostic evidence,
- runtime degradations or quality downgrades,
- reproducible runtime configurations for support.

**Graduation bar**
- the pack can explain which activated settings materially changed the rendering/runtime story and what evidence accompanied them.

### 5) Support / release / customer-handoff lane
**Why fifth:** this is where the stack proves it matters beyond demos and internal experimentation.

**Concrete scope**
- supported platform/backend/content combinations,
- shipped-versus-downloaded asset posture,
- checked docs/examples and install snippets,
- release attachments importing asset/runtime/support evidence,
- support/playbook handoff and atlas-friendly summaries.

**Graduation bar**
- a release or support consumer can answer what interactive story is actually supported and what evidence shipped with it.

## What to defer
- a universal engine/runtime/editor platform;
- one magical asset/shader pack that hides all backend differences;
- policy-first hard gates before the evidence lanes exist;
- benchmark or graphics-showcase theater without product-boundary artifacts;
- vague “works on desktop/web/mobile” claims that skip asset, backend, and support truth.

## Immediate archive consequences
- Treat **Media Surface Kit** as the anchor of a broader interactive-productization seam rather than an isolated codec/content note.
- Treat **Offload Surface + Client App Surface** as the rendering/runtime half of the story instead of letting engine docs silently absorb them.
- Treat **Runtime Settings + Observability** as activation/evidence lanes that support must import instead of rediscovering from issue reports.
- Treat **Distribution Contract + Support Envelope + DocProof** as downstream import lanes that should consume lower-layer interactive evidence instead of retelling it.
- Add a specific amnesia resistor so later revisions cannot collapse asset/media truth, shader/backend/device truth, frame/input/update truth, runtime/perf activation, and support/release conclusions into one fake readiness story.

## Read this together with
- `design/interactive-productization-stack.md`
- `design/media-surface-kit.md`
- `design/offload-surface-kit.md`
- `design/client-app-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
