# Gap: media products, transcoding/streaming/playback, and support contracts

## Why this gap matters
Rust’s media ecosystem has passed the point where the main question is “can Rust touch images/audio/video at all?”
The real question is now **what exactly a Rust media product is promising**.

Today, serious Rust media work is spread across multiple legitimate families:
- pure-Rust image lanes like `image`;
- pure-Rust demux/decode lanes like Symphonia;
- FFmpeg/libav attachment lanes like `ffmpeg-next` and `video-rs`;
- GStreamer application/plugin lanes;
- inspect-only/container lanes like `mp4parse`;
- encode-heavy lanes like `rav1e`;
- observability bridges like `tracing-gstreamer`.

That is a healthy ecosystem pattern, but it leaves an underbuilt seam:
**source/format/processing/runtime/support truth still tends to live in feature flags, native-library setup notes, plugin paths, backend env vars, and README prose**.

## What is currently missing
The ecosystem still lacks one boring portable layer that can say, in reviewable form:
- which media operations are actually supported (inspect, decode, encode, transcode, mux, demux, analyze, stream, capture, play back);
- which media families and concrete formats/codecs are first-class versus inspect-only or passthrough-only;
- which metadata/color/timing/sample semantics are preserved, normalized, or dropped;
- which native libraries, plugins, hardware paths, and runtime settings materially affect behavior;
- which service/client/runtime surfaces are attached to the media contract;
- which examples and docs are actually checked;
- and what release/support teams can safely promise.

## Why existing pieces are not enough by themselves
- `image` is already a real image-processing lane, but its recent metadata/color/runtime-hook growth does not automatically become a stable support contract for a shipped media product.
- Symphonia already has explicit format/codec/metadata support tables and feature flags, but that does not automatically explain what a product supports by default, what is optional, and what requires non-default build posture.
- `ffmpeg-next` and `video-rs` are valuable native-runtime lanes, but choosing them does not by itself explain plugin/native dependency truth, hardware-path posture, or supported media semantics.
- GStreamer is already serious about application/plugin/runtime composition, but pipeline descriptions and plugin installation do not automatically become portable release/support evidence.
- `rav1e` and inspect-only crates like `mp4parse` prove encode-only and inspect-only lanes matter, which is exactly why one fake “supports media” label is not enough.

## Worthy contribution shape
A worthy contribution here is **not** another transcoder wrapper, another pipeline DSL, another codec matrix page, or another “Rust FFmpeg replacement” pitch.
It is a **Media Productization Stack**:
- **Media Surface** for operation / format / codec / metadata / processing truth;
- **Service Surface + Client App Surface** for ingest/stream/playback/capture attachment truth;
- **Runtime Settings + Offload Surface** for native/plugin/device/backend activation truth;
- **Observability + Support Envelope + Distribution Contract** for fidelity/runtime evidence and shipped/support truth.

## Strong first execution lanes
1. pure-Rust image/audio inspect-and-transform truth;
2. FFmpeg/GStreamer native/plugin/runtime truth;
3. service ingest/transcode/stream attachment truth;
4. client playback/capture/export attachment truth;
5. hardware-acceleration / fallback / observability truth;
6. downstream imports into interactive, web, model, dataset, release, and support lanes.

## What to avoid
- flattening images, audio, video, subtitles, metadata-only inspection, and mux/demux behavior into one fake canonical media capability;
- claiming codec/container recognition alone implies faithful processing, metadata preservation, or edit support;
- hiding plugin/native-library/backend requirements in install docs and environment variables;
- treating one benchmark, screenshot, or demo clip as support evidence;
- collapsing service/client/runtime/release/support truths into one vague “multimedia support” story.

## Suggested archive consequence
Promote an explicit **Media Productization Stack** so future revisions can stop re-solving real Rust media products as framework-local glue.
