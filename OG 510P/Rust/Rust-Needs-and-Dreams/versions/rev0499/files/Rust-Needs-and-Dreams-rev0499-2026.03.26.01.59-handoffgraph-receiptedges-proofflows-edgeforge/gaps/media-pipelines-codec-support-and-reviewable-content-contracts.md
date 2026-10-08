# Gap: media pipelines, codec support, and reviewable content contracts

## What is missing
Rust now has credible libraries and bindings for image, audio, video, and streaming work, but it still lacks a **shared media-surface contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which media operations are officially supported (decode, encode, transcode, analyze, stream, edit, thumbnail, waveform, metadata extraction, etc.),
- which image/container/codec families and track types are actually part of the support promise,
- which feature flags, native-library requirements, plugin sets, or royalty/licensing-sensitive lanes matter,
- which color/pixel/sample/channel/timing assumptions are part of the supported behavior,
- which metadata, tags, captions, and side-data lanes are in scope,
- which file, live-stream, packetized, or camera/network input assumptions matter,
- which hardware-acceleration or platform-runtime assumptions exist,
- which golden assets and cross-format regression checks were actually run,
- and what evidence exists that a declared media surface still matches the shipped binary.

That missing layer matters because Rust no longer just has toy image decoders. The `image` crate is a serious pure-Rust image surface with encoders/decoders and recent metadata work including XMP/IPTC/ICC support; Symphonia is a pure-Rust multimedia demuxing/audio-decoding framework whose default support posture is feature-flag-sensitive; `ffmpeg-next` gives a broad FFmpeg wrapper but explicitly says it is in maintenance mode; GStreamer’s Rust bindings are explicitly meant for building GStreamer applications and plugins, with a separate Rust plugin ecosystem; `mp4parse` handles ISO BMFF/MP4 parsing; and `rav1e` gives Rust a real AV1 encoder lane. The remaining pain is increasingly the **portable support boundary above those pieces**, not the bare existence of multimedia crates.

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

## The current seam is awkward
The ecosystem clearly has ingredients:
- `image` already gives Rust a broad image decode/encode surface and now explicitly carries metadata/color-related support work such as XMP, IPTC, ICC extraction and initial 16-bit CMYK TIFF support;
- Symphonia already exposes format probing, metadata handling, codec registries, and per-codec/per-format feature flags, which is exactly the kind of support truth applications need to surface honestly;
- `ffmpeg-next` gives broad access to FFmpeg’s format/codec/filter/device/software-scaling/software-resampling lanes, but its own crate page says it is in maintenance mode rather than being a single strategic center of gravity;
- GStreamer Rust is explicitly for writing GStreamer applications and plugins, and there is an active `gst-plugins-rs` repository, which means real media support often depends on external runtime/plugin inventories rather than just one Cargo dependency;
- `mp4parse` shows that container- and asset-introspection lanes matter independently of full decode/playback support;
- `rav1e` shows Rust has serious codec/encoding ambitions, not just thin orchestration wrappers.

But actual support truth still gets split across:
- Cargo feature flags,
- runtime/plugin installation notes,
- native dependency setup,
- sample asset folders,
- README prose about what formats “should” work,
- ad hoc transcoding/playback tests,
- codec/container/profile caveats,
- and folklore about color conversion, metadata preservation, gapless playback, seeking, or packet/timestamp behavior.

The result is not that Rust lacks media code.
The result is that there is still no portable way to say:
- “these are the input/output media families we officially support,”
- “these codecs/containers/profiles/metadata lanes are checked versus illustrative,”
- “these platform/native/plugin requirements are part of the contract,”
- “this is the color/timing/sample-format posture we claim,”
- or “these golden assets and transcoding/roundtrip checks were actually run.”

That is exactly the archive pattern worth elevating: strong point libraries, weak shared review layer.

Sources:
- https://docs.rs/image/
- https://docs.rs/crate/image/latest/source/CHANGES.md
- https://docs.rs/symphonia
- https://docs.rs/symphonia-core
- https://docs.rs/crate/ffmpeg-next/latest
- https://gstreamer.freedesktop.org/documentation/rust/stable/latest/docs/gstreamer/
- https://github.com/GStreamer/gstreamer-rs
- https://github.com/GStreamer/gst-plugins-rs
- https://docs.rs/mp4parse
- https://github.com/xiph/rav1e

## Why this matters
This gap is bigger than “better media docs.”
It affects:
1. **product honesty** — “supports video upload” or “exports thumbnails” can hide very different realities around codecs, color profiles, metadata preservation, and platform runtime requirements;
2. **compatibility review** — changing a codec list, pixel-format path, metadata-preservation rule, or plugin/runtime dependency can be a real breaking change;
3. **ops and packaging clarity** — GStreamer plugin availability, FFmpeg/native library availability, and CPU/SIMD/hardware assumptions are support claims, not invisible implementation details;
4. **testing realism** — many projects test one happy-path sample file but do not ship one artifact saying which containers/codecs/profiles/bit-depths/timing cases were actually checked;
5. **cross-domain composition** — Client App Surface Kit, Model Surface Kit, Dataset Surface Kit, Service Surface Kit, Event Surface Kit, and Retrieval Surface Kit all need a media/content boundary without owning it;
6. **future maintenance** — a field with wrappers, plugins, native deps, and codec churn badly needs support artifacts that survive maintainer turnover.

There is also an honesty constraint: a media-surface kit should not pretend every Rust media stack is or should become a universal FFmpeg replacement. Some applications only need thumbnail extraction or metadata scanning; others only need audio demux/decode; others depend on external plugin inventories or platform decoders. A good contribution should therefore make supported scope and non-goals explicit instead of selling “media support” as a magical universal capability.

Sources:
- https://docs.rs/image/
- https://docs.rs/symphonia
- https://docs.rs/symphonia-core
- https://docs.rs/crate/ffmpeg-next/latest
- https://gstreamer.freedesktop.org/documentation/rust/stable/latest/docs/gstreamer/
- https://github.com/GStreamer/gst-plugins-rs

## What “good” looks like
A worthy contribution here is **not** another transcoder, another image/audio/video mega-framework, or a fake universal codec abstraction.

It is a shared media-surface boundary:
- one `media-surface/v0` describing app/library identity, supported operation classes, and top-level media families,
- one `media-format-catalog/v0` giving stable identities for supported container/codecs/image formats, track types, metadata lanes, support levels, and required feature/runtime gates,
- one `media-processing-profile/v0` describing color-space/pixel-format/sample-format/channel-layout/timing/seek/edit/metadata-preservation posture,
- one optional `media-runtime-profile/v0` describing native-library, plugin, hardware-acceleration, CPU/SIMD, and platform-runtime assumptions,
- one `media-check-plan/v0` describing which golden assets, transcode/roundtrip/playback/analyze scenarios were exercised,
- one `media-check-report/v0` recording checked formats/codecs/assets/platforms, fidelity/metadata findings, failures, and raw attachment pointers,
- one optional `media-diff-report/v0` for additive/breaking media-support changes,
- and one `media-pack/v0` bundle for CI, release review, SDK/app handoff, and later archaeology.

That would let Rust teams treat media support as a reviewable product surface instead of a pile of Cargo features, plugin notes, sample files, and intuition about what happens when a customer uploads a CMYK TIFF with metadata or an audio file with a different container/codec mix than the one in the README.
