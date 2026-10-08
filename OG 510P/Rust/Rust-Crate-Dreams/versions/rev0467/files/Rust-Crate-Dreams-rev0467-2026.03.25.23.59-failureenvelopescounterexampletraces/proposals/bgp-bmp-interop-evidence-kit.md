---
id: P-0254
title: BGP + BMP Interop & Evidence Kit — canonical control-plane captures, policy explainers, and repro bundles
status: idea
domains: [networking, routing, security, interop, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://www.rfc-editor.org/rfc/rfc4271.html
  - https://datatracker.ietf.org/doc/html/rfc7854
  - https://www.iana.org/assignments/bgp-parameters
---

## Why this is missing
Rust networking teams increasingly need offline, shareable artifacts for:
- reproducing routing incidents,
- comparing routing policy outcomes,
- validating parsing/decoding correctness for BGP and BMP streams.

BMP exists specifically to monitor BGP sessions and obtain route views without screen scraping (RFC 7854), but Rust lacks a **standard evidence bundle** and conformance harness to make BMP/BGP captures reproducible and comparable across tooling.

## What the crate provides
A workspace that produces **`*.bgpbundle.zip`** artifacts:

- Canonicalized BGP message streams (OPEN/UPDATE/KEEPALIVE/NOTIFICATION) per RFC 4271.
- BMP message captures and decoded views per RFC 7854 (peer up/down, route monitoring).
- Parameter registries snapshots (code points, error codes) to make traces stable across time (IANA BGP parameters).

### Core crates/modules
- `bgp-wire`: strict BGP message parser/renderer (zero “helpful” normalization by default).
- `bmp-wire`: strict BMP parser/renderer.
- `canon`: canonical JSON views + deterministic ordering + stable hashing.
- `policy-explain`: optional layer for “why is this route present/absent” when coupled with policy engines.
- `bgpbundle`: evidence schema + redaction profiles (IP/ASN masks, community redaction).
- `matrix`: compare captures across decoders and policy engines.

## Bundle format sketch
`bgpbundle/`
- `meta.json`
- `registries/iana-bgp-parameters.csv` (or pinned JSON snapshot)
- `streams/peer-<id>/bgp.bin` + `bgp.jsonl`
- `streams/bmp.bin` + `bmp.jsonl`
- `timeline.json` (normalized timestamps)
- `verdict.json` + `diff.md`

## MVP plan (6–8 weeks)
1. `bmp-wire` + `bgpbundle` pack/unpack; ingest pcap → bmp stream.
2. Canonical JSON view for the top message types (BMP route monitoring + BGP UPDATE).
3. Redaction presets + stable hashing for sharing artifacts.
4. Interop runner that compares two decoders on the same bundle and produces diffs.

## De-risking
- Treat policy as optional: get the **evidence layer** right first.
- Start with **monitoring** flows (BMP) before attempting full BGP speaker behavior.

## What users get
- A single portable artifact to reproduce a control-plane event and compare decoders/policy outputs.
