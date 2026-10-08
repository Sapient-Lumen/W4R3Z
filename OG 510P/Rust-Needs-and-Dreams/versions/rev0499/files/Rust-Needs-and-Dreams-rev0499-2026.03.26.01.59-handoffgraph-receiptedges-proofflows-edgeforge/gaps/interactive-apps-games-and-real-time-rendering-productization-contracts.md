# Gap: Interactive apps, games, and real-time rendering productization contracts

Rust already has serious interactive ingredients: Bevy is now a credible cross-platform engine/app framework with scenes, hot reload, web assets, tooling widgets, frame-time graphs, and increasingly high-end rendering paths; `wgpu` is a serious cross-platform graphics substrate; rust-gpu already gives Rust-authored shader crates their own build lane; `winit`, `egui`, and Slint each expose very different but very real runtime/UI/event-loop truths.

What Rust still lacks is the **portable boring boundary above those ingredients**.

Today, serious interactive projects still publish their support story as a tangle of:
- engine version numbers,
- shader source folders and build scripts,
- asset conventions,
- backend/env-var lore,
- event-loop and redraw folklore,
- screenshots/benchmarks,
- and platform caveats scattered across READMEs and issue threads.

That leaves the ecosystem unable to answer routine product questions cleanly:
- Which assets actually ship, and which are downloaded or cached later?
- Which shader languages, backends, and fallback paths are really supported?
- Is this a continuously-rendered game loop, a low-power desktop tool, or something in between?
- Which settings changed the backend, quality, frame pacing, or hot-reload behavior?
- Which platforms/backends/content modes are truly supported and tested?

The missing contribution is therefore **not** another engine, renderer wrapper, asset manager, or shader convenience layer.
It is a **productization/evidence stack** that keeps:
- asset/media truth,
- shader/backend/device truth,
- frame/input/update truth,
- runtime/perf activation,
- and shipped/support truth

separate while still letting them compose.

## Why this matters
Interactive Rust work sits at the intersection of multiple archive territories:
- **Client Productization** already covers app/package/capability/platform truth.
- **Media Surface** already covers content/format/runtime assumptions.
- **Offload Surface** already covers backend/device/kernel/fallback truth.
- **Runtime Settings** and **Observability** already cover activation and evidence.
- **Distribution Contract** and **Support Envelope** already cover shipping and promises.

Without a synthesis layer, real-time apps and games remain a seam where all of those truths get flattened into “works on my machine”, “runs on web”, or “uses wgpu/Bevy”.

## Contribution shape that would count as worthy
A worthy contribution would:
1. define a thin importable artifact family for interactive products;
2. keep content, shader/backend, runtime, and support truth distinct;
3. make downgrade paths and software-renderer/backoff stories explicit;
4. give release/support/atlas consumers something durable to import;
5. work across game, tool, visualization, and embedded-interactive lanes without pretending they are identical.

## Archive direction
This gap should now be treated as an explicit **Interactive Productization Stack** opportunity rather than scattered follow-on work under client, media, or offload notes.
