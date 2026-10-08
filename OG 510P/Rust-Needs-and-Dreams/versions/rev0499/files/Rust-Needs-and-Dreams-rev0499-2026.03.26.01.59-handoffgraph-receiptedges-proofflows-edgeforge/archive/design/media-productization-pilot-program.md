# Pilot program: Media Productization Stack

## Goal
Exercise the smallest set of media-facing lanes that prove the archive’s proposed **Media Productization Stack** is real and useful: media/processing truth, runtime/plugin/native/backend activation, service/client attachment truth, observability/fidelity evidence, and shipped/support truth.

This pilot program should produce reusable artifacts and comparison notes.
It should not try to standardize every media framework or every codec family.

## Pilot artifact families
- `media-surface/v0`
- `media-format-catalog/v0`
- `media-processing-profile/v0`
- `media-runtime-profile/v0`
- `media-check-plan/v0`
- `media-check-report/v0`
- `media-pack/v0`
- imported support/docs attachments from Distribution Contract / Support Envelope / DocProof

## Ranked pilot lanes

### Pilot 1: pure-Rust image/audio inspect-and-transform lane
**Why first:**
It proves the narrowest serious lane with the least native/plugin variance.
It is enough to show that format support, metadata posture, and processing semantics belong in durable review artifacts.

**Candidate substrates:**
- `image`
- Symphonia
- `mp4parse` for inspect-only/container examples

**What to export:**
- operation classes in scope;
- format/codec/image identities;
- metadata/color/sample/timing processing posture;
- pure-Rust runtime profile;
- checked fixture reports.

**Success condition:**
A reviewer can tell exactly which media operations, formats, and processing semantics are part of the supported contract without reading example code.

### Pilot 2: FFmpeg / GStreamer runtime lane
**Why second:**
Rust media products frequently rely on native libraries or plugins.
That means version/plugin/library discovery is not incidental setup; it is real product truth.

**Candidate substrates:**
- `ffmpeg-next`
- `video-rs`
- GStreamer Rust

**What to export:**
- native/plugin/library requirements;
- runtime/plugin discovery posture;
- version/backend notes;
- unsupported-combination notes;
- checked reports that include runtime state.

**Success condition:**
A reviewer can distinguish “supports this media flow” from “might work if the right local native state happens to exist.”

### Pilot 3: service ingest / transcode / stream lane
**Why third:**
Media products are often backend APIs as much as they are local libraries.
This proves service/API truth can import media truth instead of replacing it.

**Candidate substrates:**
- Axum/Actix service importing Media Surface artifacts
- upload/transcode/export flow
- live ingest or packet-inspection flow

**What to export:**
- API attachment points;
- accepted/rejected media classes;
- transcode/export profiles;
- runtime-setting activation that materially changes outcomes;
- checked service-side media reports.

**Success condition:**
A reviewer can see which truths belong to the media layer and which belong to the service API.

### Pilot 4: client playback / capture / export lane
**Why fourth:**
Many Rust media products are local tools, players, editors, or capture/export apps.
This proves client/package/device behavior can attach cleanly without swallowing media semantics.

**Candidate substrates:**
- desktop playback/export tool
- camera/mic capture tool
- mixed client-app/media lane using Tauri, Slint, or another client surface importer

**What to export:**
- playback/capture/export roles;
- package/device/window/runtime assumptions;
- local asset vs downloaded asset posture;
- checked client-side reports.

**Success condition:**
A reviewer can tell which behaviors are media semantics and which are app/device/package realities.

### Pilot 5: observability + downstream-consumer lane
**Why fifth:**
The stack matters only if other archive surfaces can import it and if failures become easier to diagnose.

**Candidate substrates:**
- `tracing-gstreamer`
- release/support imports
- interactive/web/model/dataset consumers

**What to export:**
- fidelity/runtime/trace attachments;
- one release/support import;
- one interactive/web/client import;
- one model/dataset import where media is only an attachment lane.

**Success condition:**
Consumers can reuse media-productization facts without re-describing format/runtime/support posture.

## Comparison questions the pilots should answer
- Which facts are stable media-product facts versus runtime-activation facts?
- Which formats are inspect-only, decode-only, encode-only, or round-trip capable?
- Which metadata and processing semantics are public contract versus best-effort implementation details?
- Which failures are media-surface failures versus missing-plugin/native/backend failures?
- Which docs/examples are checked support evidence versus illustrative tutorials?

## Early artifacts worth standardizing
- `media-surface/v0`
- `media-format-catalog/v0`
- `media-processing-profile/v0`
- `media-runtime-profile/v0`
- `media-check-report/v0`
- `media-pack/v0`

These are enough to prove the seam without freezing a giant schema too early.

## What this pilot program should resist
- becoming a new transcoder framework;
- becoming a codec marketplace or giant media matrix website;
- assuming FFmpeg, GStreamer, and pure-Rust lanes can be flattened into one runtime story;
- treating screenshots or one successful clip as support evidence;
- letting service/client packaging swallow media semantics.

## Recommended first implementation order
1. pure-Rust image/audio lane
2. FFmpeg/GStreamer runtime lane
3. service ingest/transcode lane
4. client playback/capture/export lane
5. observability + downstream consumer lane

## Expected archive follow-ons
- Promote Media Productization Stack in frontier and priority docs.
- Add media-productization-specific amnesia resistance language.
- Make future interactive, web, client, service, model, dataset, release, and support revisions import media-productization facts instead of re-deriving them.
