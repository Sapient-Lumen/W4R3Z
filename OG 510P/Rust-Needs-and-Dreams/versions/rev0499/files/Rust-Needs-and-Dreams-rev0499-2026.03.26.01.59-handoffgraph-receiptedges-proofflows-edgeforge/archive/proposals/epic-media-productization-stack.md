# Epic proposal: Media Productization Stack

## Thesis
Rust needs a **portable, boring media-product boundary** above codecs, native runtimes, plugins, players, pipelines, and demo assets.
The problem is no longer “can Rust touch media?”
The problem is that media operations, format support, metadata/processing semantics, runtime/plugin/native/backend activation, service/client attachment points, and support/docs truth are still too often implicit.

## Why this would count as worthy
This contribution would help multiple major Rust lanes at once:
- media-heavy backend services;
- desktop/mobile playback, capture, and export tools;
- interactive apps, games, and visualization products;
- ML/data products that ingest or emit media;
- browser/full-stack products that attach playback/export flows;
- release/support teams that need honest runtime/plugin/package claims.

It would be boring in the right way:
- reviewable;
- importable by other tools;
- runtime-aware instead of setup-doc theater;
- format-aware instead of fake universal media support;
- useful to support and release teams, not only media-library authors.

## Deliverables
- `design/media-productization-stack.md`
- `design/media-productization-pilot-program.md`
- `gaps/media-products-transcoding-streaming-playback-and-support-contracts.md`
- `media-surface/v0` family refinements
- comparison pilots across pure-Rust, FFmpeg/libav, and GStreamer lanes
- release/support/import examples

## First proof bar
A first serious proof should show that one Rust project can publish a `media-pack/v0`-style bundle that keeps:
- media operation and format truth,
- metadata/processing posture,
- runtime/plugin/native/backend activation,
- service/client attachment points,
- and checked support/docs evidence

all distinct while still being reusable by interactive, web, client, service, model, dataset, release, and support consumers.

## Non-goals
- universal Rust media framework;
- universal codec/container abstraction;
- replacing FFmpeg or GStreamer;
- flattening service/client/runtime/release/support truth into one giant schema.
