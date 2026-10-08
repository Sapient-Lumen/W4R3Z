# Epic proposal: Media Surface Kit

## Thesis
Rust’s image/audio/video ecosystem is now strong enough that the missing contribution is no longer “yet another decoder wrapper” or “yet another transcoder CLI.”
The higher-leverage missing piece is a **portable media-surface contract** that lets teams declare, diff, validate, and ship what their software actually promises: supported operations, container/codec/image-format lanes, metadata/color/timing behavior, runtime/plugin assumptions, and checked evidence.

In other words: Rust needs a boring, attachable `media-pack/v0` more than it needs one more pile of README bullets about “common formats supported.”

## Why now
The ecosystem signals line up:
- `image` is a durable pure-Rust image library and is still expanding support in compatibility-relevant areas like XMP/IPTC/ICC metadata extraction and CMYK TIFF handling.
- Symphonia is already a real pure-Rust demux/decode framework with explicit format/codec/metadata support and feature-gated support posture.
- `ffmpeg-next` remains useful but explicitly describes itself as maintenance-mode compatibility glue rather than a strategic place to centralize every media contract.
- GStreamer Rust plus `gst-plugins-rs` prove that Rust media support increasingly lives in plugin-rich runtimes and mixed dependency stacks rather than in one pure-Cargo lane.
- `mp4parse` confirms that asset/container introspection is a first-class support surface.
- `rav1e` confirms that serious encode pipelines belong in the Rust conversation too.

That means the missing substrate is not raw media capability.
It is the **reviewable boundary above today’s pieces**.

Sources:
- https://docs.rs/image/
- https://docs.rs/crate/image/latest/source/CHANGES.md
- https://docs.rs/symphonia
- https://docs.rs/symphonia-core
- https://docs.rs/crate/ffmpeg-next/latest
- https://gstreamer.freedesktop.org/documentation/rust/stable/latest/docs/gstreamer/
- https://github.com/GStreamer/gst-plugins-rs
- https://docs.rs/mp4parse
- https://github.com/xiph/rav1e

## What should be built
A first credible version should ship:
1. `media-surface/v0`, `media-format-catalog/v0`, `media-processing-profile/v0`, optional `media-runtime-profile/v0`, `media-check-plan/v0`, `media-check-report/v0`, optional `media-diff-report/v0`, and `media-pack/v0`
2. adapters for common Rust media lanes (`image`, Symphonia, `ffmpeg-next`, GStreamer Rust, codec/container-specific helpers like `mp4parse`, encoder lanes like `rav1e`)
3. generated support/reference docs for operations, supported inputs/outputs, runtime requirements, metadata posture, and processing qualifiers
4. validation/reporting support for unsupported assets, runtime/plugin mismatch, metadata loss, format-recognized-but-not-fully-supported cases, and regression drift across releases
5. release/CI examples showing media packs attached to libraries, CLIs, desktop/mobile apps, services handling uploads/transcodes, and ML/media preprocessing workflows

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one pure-Rust image-processing app/library using `image` plus metadata-aware fixtures and explicit format/bit-depth/color claims
- one audio decode/analyze tool using Symphonia with format/codec/metadata support declared and checked
- one FFmpeg-backed transcode/thumbnail service with explicit runtime/native dependency and feature support documentation
- one GStreamer-based streaming or plugin-rich pipeline with plugin inventories and checked operation subsets attached as artifacts
- one media-ingestion library that proves inspect-only/container-parse support can be declared separately from full decode/transcode support

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve operation identity, format truth, processing posture, and runtime truth
2. **v0.2 adapters**
   - support `image`, Symphonia, `ffmpeg-next`, GStreamer Rust attachments, and basic golden-asset suites
   - support raw fixture/output attachments without flattening all media evidence into one fake canonical sample format
3. **v0.3 cross-kit integration**
   - integrate with Client App Surface, Service/Event Surface, Runtime Settings, Support Envelope, Model Surface, and Dataset Surface kits
   - support diff/baseline workflows across platforms/releases
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one runtime, one OS target, or one media lane

## Success metrics
- Teams can review media-support changes as explicit artifacts instead of reverse-engineering Cargo features, plugin notes, and fixture folders.
- Supported inputs/outputs and processing qualifiers remain documented from one declared source.
- Runtime/plugin/native requirements become easier to trust because checked and illustrative lanes stay distinct.
- Metadata/color/timing behavior becomes less folkloric and more reviewable.
- Rust media stacks become easier to hand off across client apps, services, ML pipelines, docs, and operations workflows without bespoke glue.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Client App Surface Kit covers app/package/lifecycle/permission truth,
- Service Surface Kit and Event Surface Kit cover HTTP and streaming/message boundaries,
- Runtime Settings Kit covers configurable runtime knobs,
- Support Envelope Kit covers platform/runtime baselines,
- Model Surface Kit covers model/tokenizer/runtime truth,
- Dataset Surface Kit covers dataset/table/layout truth,
- and Plugin Surface Kit covers extension ecosystems.

But none of those is the portable contract for the **media/content boundary itself**.
Media Surface Kit is the missing substrate that keeps formats, codecs, processing posture, runtime/plugin assumptions, and checked evidence attached to one reviewable interface without absorbing the rest of the stack into one mega-format.
