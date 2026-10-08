# Design: Media Surface Kit (`cargo mediacheck`, `media-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust application or library’s supported **media surface**: input/output media families, container/codec/image-format support, metadata and side-data lanes, color/timing/sample-format posture, runtime/native/plugin assumptions, and evidence that the declared media behavior still matches reality.

This should **not** replace `image`, Symphonia, FFmpeg/GStreamer bindings, codec crates like `rav1e`, or future media frameworks.
It should make them compose better and make support claims reviewable.

## References (signals)
- `image` is explicitly a native Rust image encoding/decoding and basic image-processing crate, and its recent changes add media-surface-relevant support like XMP/IPTC/ICC extraction and initial 16-bit CMYK TIFF handling.
  https://docs.rs/image/
  https://docs.rs/crate/image/latest/source/CHANGES.md
- Symphonia is explicitly a 100% pure Rust audio decoding and multimedia format demuxing framework, with feature-flag-sensitive support for formats/codecs and dedicated metadata and probing layers.
  https://docs.rs/symphonia
  https://docs.rs/symphonia-core
- `ffmpeg-next` explicitly says it is a fork of the abandoned `ffmpeg` crate, is in maintenance mode, and aims for compatibility across FFmpeg 3.4 through 8.0.
  https://docs.rs/crate/ffmpeg-next/latest
- GStreamer Rust bindings explicitly target writing GStreamer applications and plugins, and `gst-plugins-rs` shows Rust-based plugin inventories are already a real lane.
  https://gstreamer.freedesktop.org/documentation/rust/stable/latest/docs/gstreamer/
  https://github.com/GStreamer/gstreamer-rs
  https://github.com/GStreamer/gst-plugins-rs
- `mp4parse` explicitly parses ISO Base Media Format / MP4 streams, proving that file/container introspection support matters as a first-class surface.
  https://docs.rs/mp4parse
- `rav1e` is a serious AV1 encoder project in Rust, confirming that Rust’s media story now includes real encode paths, not just orchestration wrappers.
  https://github.com/xiph/rav1e

## Core idea
The kit should give Rust projects a way to publish and validate answers to questions like:
- Which media operations are supported: decode, encode, transcode, inspect, thumbnail, waveform, stream, edit, mux, demux, capture?
- Which media families are in scope: image, audio, video, timed text/subtitles, metadata-only, packet/track introspection?
- Which container/codec/image formats are supported, under which feature flags or runtime assumptions?
- Which color-space, bit-depth, pixel-format, sample-format, channel-layout, resampling, and timing assumptions are part of the support promise?
- Which metadata is preserved, normalized, or dropped?
- Which plugin/native/hardware/runtime requirements must be present?
- Which golden assets and transformations were actually checked?

The output should be attachable to CI, app releases, SDK releases, bug reports, docs/reference generation, and platform handoff.

## Proposed artifact set

### 1) `media-surface/v0`
Top-level declaration of a project’s supported media boundary.

Should capture:
- project/app/library identity
- supported operation classes (decode, encode, transcode, inspect, stream, edit, analyze, render)
- supported media families (image, audio, video, mixed/multitrack, metadata-only)
- top-level support levels (stable / preview / experimental / illustrative-only)
- links to format, processing, runtime, and check artifacts

Design rule: this is not the place to flatten every codec/container detail into one list. Keep the top-level declaration concise and link the detailed catalogs.

### 2) `media-format-catalog/v0`
Stable identities for the concrete format families a project claims to support.

Should capture:
- entry ids for image formats, containers, codecs, subtitle/timed-text lanes, metadata/tag families, and track kinds
- directionality (input only, output only, roundtrip, passthrough, inspect-only)
- feature-flag or build-profile gates
- required runtime/plugin/native capability refs
- support level and notes
- optional links to spec/profile refs

Design rule: preserve the difference between container support, codec support, and “we can inspect this asset but not fully decode/transcode it.”

### 3) `media-processing-profile/v0`
Declared processing semantics that matter for compatibility.

Should capture:
- pixel formats / color spaces / color profiles / alpha handling
- sample formats / channel layouts / sample rates / resampling posture
- timebase / timestamp / seeking / gapless / trimming / edit posture
- metadata preservation / stripping / rewriting rules
- scaling, conversion, rotation/orientation, and normalization assumptions
- track-selection and mux/demux posture where relevant

Design rule: processing semantics are a separate compatibility surface from raw format recognition.

### 4) `media-runtime-profile/v0` (optional)
Runtime/environment truth attached to the media surface.

Should capture:
- native libraries required
- plugin inventories or plugin families required
- hardware-acceleration lanes and fallbacks
- CPU/SIMD requirements or noteworthy optional accelerators
- platform-specific support qualifiers
- licensing / royalty / redistribution notes when they materially affect shipped support

Design rule: keep runtime truth explicit instead of burying it in install docs.

### 5) `media-check-plan/v0`
Plan for validating that the declared media surface still behaves as claimed.

A plan should capture:
- selected operations/media-format ids to exercise
- representative golden assets and asset classes
- expected outputs/fidelity/metadata rules
- file versus stream/live scenarios
- platform/runtime combinations to exercise
- unsupported or illustrative-only scenarios

Design rule: distinguish illustrative demo media from actual checked coverage.

### 6) `media-check-report/v0`
Portable results from running media checks.

A report should capture:
- artifact versions and environment
- runtime/plugin/native capability state
- formats/codecs/assets exercised
- pass/fail/unsupported outcomes
- fidelity or roundtrip findings when relevant
- metadata preservation/loss findings when relevant
- timing/seek/gapless findings when relevant
- raw attachment refs (fixtures, logs, hashes, thumbnails, spectrograms, output files)

Design rule: the report should be honest about scope. “One MP4 file decoded on Linux” is not proof of broad video support.

### 7) `media-diff-report/v0` (optional)
A compatibility-oriented comparison between two declared media surfaces.

Should support:
- added/removed formats or operations
- changed feature/runtime gates
- changed metadata or processing posture
- changed fidelity guarantees
- possible compatibility hazards

### 8) `media-pack/v0`
Bundle format for declarations, reports, raw fixture inventories, hashes, generated docs, and supporting artifacts.

## How it should compose
- **Client App Surface Kit:** link capture, camera/mic/file-picker, deeplink/share-target, and package permissions without making the app kit own codec/container truth.
- **Service Surface Kit / Event Surface Kit:** link upload, streaming, or live-packet APIs without confusing them with the media contract itself.
- **Model Surface Kit:** attach multimodal model expectations to declared media inputs/outputs rather than flattening media files into model artifacts.
- **Dataset Surface Kit:** link bounded media corpora or benchmark sets without pretending a dataset contract is the same thing as a media-support contract.
- **Runtime Settings Kit:** link configurable transcoding profiles, plugin paths, bitrate presets, and hardware toggles as runtime inputs.
- **Support Envelope Kit:** link platform/runtime baselines without replacing the media-specific format/processing declarations.

## Non-goals
- standardizing one universal codec abstraction
- replacing FFmpeg or GStreamer
- replacing pure-Rust image/audio/video libraries
- forcing image/audio/video/subtitle/media-metadata workflows into one fake canonical track model
- claiming codec/container recognition alone implies faithful transcode, metadata preservation, or edit support
- pretending all media support can be tested with a couple of tiny sample files

## First implementation shape
A credible first implementation could be mostly adapters and validators:
- generate `media-surface` + `media-format-catalog` from lightweight project config and crate/runtime annotations
- ingest `image`/Symphonia/FFmpeg/GStreamer/codec-specific support declarations as attachments without flattening away source truth
- record small golden-asset suites with hashes and expected outcomes
- emit generated support/reference docs for supported operations and formats
- attach raw output files, thumbnails, waveform summaries, hashes, and logs as evidence
- provide a diff mode for media-support changes across releases

The winning version is intentionally boring: it turns “supports media” from folklore into reviewed artifacts.
