# Design: Media Productization Stack (Media Surface + Service Surface + Client App Surface + Runtime Settings + Offload Surface + Observability + Distribution Contract + Support Envelope)

## Goal
Turn Rust media-facing products into a **portable productization stack** instead of leaving each project to express its media story as a tangle of format tables, plugin instructions, native-library install notes, backend toggles, asset fixture folders, demo clips, and README folklore.

The stack should **not** replace `image`, Symphonia, `ffmpeg-next`, `video-rs`, GStreamer Rust, `mp4parse`, `rav1e`, or future media frameworks.
It should make them compose better and make supported media behavior reviewable.

## Why this note is needed now
Rust’s current media signals say the missing problem is no longer “can Rust touch media at all?”
They say the missing problem is **what a Rust media product can honestly claim to ship and support**:
- `image` is now a richer image lane than a simple decode/encode crate: it exposes low-level decoder/encoder control, format hooks, and recent release notes show support for XMP/IPTC/ICC metadata handling and broader TIFF/color behavior.
- Symphonia is explicit about being a 100% pure Rust audio-decoding and multimedia-demuxing framework, and it makes default-vs-feature-gated format/codec support explicit. That is already product-boundary material, not just library trivia.
- `ffmpeg-next` is explicit that it is in maintenance mode and aims to stay compatible with FFmpeg 3.4 through 8.0. That means Rust media work still often depends on native version/runtime truth that deserves first-class evidence.
- GStreamer Rust explicitly targets writing GStreamer-based applications and plugins, which means runtime/plugin inventories are already part of real Rust product behavior.
- `video-rs` shows another real lane: a stable-and-Rusty interface on top of `libav`/FFmpeg for reading, writing, muxing, encoding, and decoding, while also warning that the crate is still work-in-progress. That is a sharp reminder that product claims need more than crate selection.
- `tracing-gstreamer` proves observability is already entering the media lane directly: GStreamer logs and tracers can be bridged into Rust `tracing`, and plugin-based tracer installation is part of the real runtime story.
- `rav1e` proves Rust media is not just wrapper territory: encode-heavy paths, color-depth/chroma choices, and speed/bitrate/profile reality are part of the ecosystem too.

Together, those signals argue that the missing contribution is **not** another codec wrapper, pipeline DSL, or media framework bake-off.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Media Surface: format, operation, metadata, and processing truth
Media Surface owns the **declared media-facing product boundary**:
- supported operations,
- supported media families,
- container/codec/image/timed-text identities,
- metadata/tag support,
- color/sample/timing/processing posture,
- and checked media examples.

This layer answers questions like:
- “Do we inspect this format, decode it, transcode it, or round-trip it?”
- “Which metadata survives?”
- “Is this a strict playback/streaming lane, an editing lane, or an analysis lane?”

Design rule: **media truth must not remain an incidental side effect of one crate’s features, one pipeline string, or one demo asset**.

### 2) Service Surface + Client App Surface: ingress, playback, capture, and runtime-role truth
Real media products almost always have service or client attachment points.
These layers own:
- upload/download/live-ingest/export APIs,
- playback/capture/device/window/package assumptions,
- streaming and session role boundaries,
- and app/service-facing behavior above raw format support.

This layer answers questions like:
- “Is this a backend transcoder, a player/editor, or both?”
- “Which media truths belong to the service API versus the local client?”
- “Which capture/playback/device assumptions are part of the supported interface?”

Design rule: **media products must keep media semantics distinct from app/API attachment semantics**.

### 3) Runtime Settings + Offload Surface: native/plugin/device/backend activation truth
Media products change materially through runtime posture:
- FFmpeg/libav versus GStreamer/plugin lanes,
- hardware acceleration and fallback,
- plugin/library discovery paths,
- CPU/SIMD/device/backend selection,
- codec/quality/preset/profile choices,
- and env/config overrides that materially alter behavior.

This layer answers questions like:
- “Did this run through a pure-Rust lane, a native library lane, or a plugin-discovered lane?”
- “Which device/backend/acceleration path was actually active?”
- “Which settings turn a supported format into a failing or degraded one?”

Design rule: **activation posture is product truth, not mere launcher trivia**.

### 4) Observability + check reports: fidelity, runtime, and failure evidence
Media behavior is easy to overclaim.
This layer owns:
- media check plans and reports,
- fidelity and round-trip findings,
- timing/seek/gapless findings,
- transcoder/runtime logs,
- tracing/profiling attachments,
- and evidence explaining whether a failure was format-, processing-, runtime-, plugin-, or support-boundary-related.

This layer answers questions like:
- “What was really tested?”
- “Was metadata preserved?”
- “Did the failure come from unsupported media, missing plugins, backend mismatch, or an activation mistake?”

Design rule: **one clip working on one developer machine is not support evidence**.

### 5) Distribution Contract + Support Envelope + DocProof: shipped artifact and public promise truth
Media products often ship more than a binary:
- native libraries,
- plugin bundles,
- sample assets,
- downloaded codecs/models/filters,
- platform caveats,
- and documentation/tutorial promises.

These layers own:
- what ships versus what is fetched later,
- supported platform/runtime floors,
- plugin/native redistribution assumptions,
- checked docs/examples/tutorials,
- and release/support-facing claims.

This layer answers questions like:
- “What must be present at install time?”
- “What is bundled versus downloaded?”
- “Which docs/examples actually reflect supported behavior?”

Design rule: **a demo pipeline and a release contract are not the same thing**.

### 6) Downstream consumers
The stack matters when real consumers can import it honestly:
- **Interactive** products can attach asset/media/runtime truth without redefining codecs and processing posture.
- **Web and Client** products can attach playback/capture/export behavior without pretending browser/app/runtime truth replaces media truth.
- **Service** products can attach ingest/transcode/stream APIs without flattening runtime/plugin/backend truth.
- **Model** and **Dataset** consumers can attach media-input/output expectations without pretending media families are just tensor payloads.
- **Release / Support / Atlas** consumers can reuse the same facts instead of reverse-engineering them from issue threads and setup docs.

Design rule: **consumers import selected media-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust media framework.”
It is a portable boring stack with clear boundaries:

1. **operation / format / processing truth first**
   - prove stable declarations for inspect/decode/encode/transcode/playback/capture plus format/metadata/processing posture on one real product;
2. **runtime / plugin / native truth second**
   - prove FFmpeg/GStreamer/pure-Rust/native-library choices can be expressed honestly instead of implied by setup docs;
3. **service / client attachment truth third**
   - prove backend ingest/transcode/stream APIs and local playback/capture/export posture can attach cleanly;
4. **checked behavior and observability fourth**
   - prove fidelity/runtime reports and trace/log attachments can travel as durable evidence;
5. **shipping / support / consumer imports fifth**
   - prove release/support/interactive/web/model/dataset consumers can reuse the same facts.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases media truth, runtime truth, app/API truth, and support truth.

## Ranked first execution lanes
1. **pure-Rust image/audio lane**
   - best first exporter because it proves operation/format/metadata/processing truth without immediately depending on plugin discovery.
2. **FFmpeg / GStreamer runtime lane**
   - proves native-library, plugin, version, and activation posture are real product truths.
3. **service ingest / transcode / stream lane**
   - proves media truth can attach to backend APIs without becoming “just another endpoint spec.”
4. **client playback / capture / export lane**
   - proves app/package/device/window/capture behavior can attach without replacing media truth.
5. **observability + downstream-consumer lane**
   - proves runtime evidence and release/support/interactive/web/model imports are possible without flattening the stack.

## Non-goals
- one universal Rust media framework;
- one universal codec/container abstraction;
- replacing FFmpeg or GStreamer;
- pretending images, audio, video, subtitles, live streams, and metadata-only lanes all want one identical contract;
- treating runtime/plugin/native assumptions as invisible plumbing;
- calling demos, screenshots, or one benchmark plot “support evidence.”

## Archive implications
- The archive should now treat **Media Surface + Service Surface + Client App Surface + Runtime Settings + Offload Surface + Observability + Distribution Contract + Support Envelope** as a coupled **Media Productization Stack** in frontier and priority discussions.
- Future revisions should prefer **operation/format/processing truth, runtime/plugin/backend activation truth, service/client attachments, observability/fidelity evidence, and shipped/support truth** over another transcoder wrapper, codec matrix, pipeline DSL, or FFmpeg-replacement fantasy.
- Interactive, Web, Client, Service, Model, Dataset, Release, and Support work should import media-productization artifacts rather than re-explaining codec/runtime/support posture from scratch.

## Read this together with
- `design/media-surface-kit.md`
- `design/service-surface-kit.md`
- `design/client-app-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/offload-surface-kit.md`
- `design/observability-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
- `design/interactive-productization-stack.md`

## References (signals)
- `image`:
  https://docs.rs/image/latest/image/
- `image` changes:
  https://docs.rs/crate/image/latest/source/CHANGES.md
- Symphonia:
  https://docs.rs/symphonia/latest/symphonia/
- `ffmpeg-next`:
  https://docs.rs/crate/ffmpeg-next/latest
- GStreamer Rust:
  https://gstreamer.freedesktop.org/documentation/rust/stable/latest/docs/gstreamer/
- `video-rs`:
  https://docs.rs/crate/video-rs/latest
- `tracing-gstreamer`:
  https://docs.rs/tracing-gstreamer/latest/tracing_gstreamer/
- `mp4parse`:
  https://docs.rs/mp4parse/latest/mp4parse/
- `rav1e`:
  https://github.com/xiph/rav1e
