---
id: P-0269
title: S3-Compatible Object Storage Interop & Evidence Kit (s3bundle)
status: idea
domains: [cloud, storage, interop, testing, security]
last_reviewed: 2026-03-05
evidence:
  - https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html
  - https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html
  - https://crates.io/crates/aws-sdk-s3
  - https://crates.io/crates/s3
  - https://crates.io/crates/s3s
  - https://github.com/minio/minio
---

## What it should provide others

A Rust-first toolkit to **test and debug S3 compatibility** across providers (AWS S3, MinIO, Ceph RGW, Wasabi, GCS S3 gateways, on-prem appliances) using shareable, redacted, replayable **evidence bundles**.

This should help:

- SDK authors (aws-sdk-s3, alternative clients)
- gateway/proxy authors
- storage vendors aiming for “S3-compatible”
- application teams needing confidence that their usage pattern is portable

## Core idea

Most “S3 bugs” are *edge-case semantics*:

- pagination / continuation tokens
- header normalization, encoding quirks, XML variations
- consistency expectations, overwrite semantics
- signature / auth subtleties (v4), region behavior

So the kit focuses on **scenario-driven** tests that emit a canonical request/response IR + provider fingerprints.

## Design sketch

### Workspace layout

- `s3bundle` — schema + IO + redaction policy
- `s3-ir` — canonical model:
  - method, canonicalized path/query
  - selected headers (normalized, allowlisted)
  - payload hash + size (optional body samples)
  - response status + selected headers + parsed XML/JSON bodies
- `s3scenario` — scenario DSL + runner
- `s3matrix` — provider capability matrix generator
- `s3diff` — semantic diffs (token drift, XML shape drift, header casing, error codes)

### Evidence bundle format: `*.s3bundle.zip`

- `manifest.json` (provider, region, auth mode, tool versions)
- `scenario.toml` + `inputs/`
- `trace.s3ir.jsonl`
- `reports/compat.md` + `reports/diff.json`
- `redaction.json` (what was removed/hashed)
- optional `pcap/` (if captured) for low-level debugging

## MVP (4–8 weeks)

1. Canonical IR + bundle writer/reader
2. 10 high-value scenarios:
   - PutObject + overwrite
   - ListObjectsV2 pagination (1000 limit, continuation token)
   - multipart upload (init/upload/complete/abort)
   - signed vs unsigned payload variants
3. Provider fingerprints (headers, error shapes, XML schema quirks)
4. `s3diff` explain output for the above scenarios

## De-risking plan

- Keep API surface narrow: focus on operations most used by apps (PUT/GET/LIST/MULTIPART).
- Make the runner pluggable:
  - native Rust client (reqwest/hyper)
  - adapter for aws-sdk-s3 request middleware (where possible)

## Non-goals (initially)

- Full IAM policy evaluation modeling
- Glacier, Outposts, or specialized storage classes

## Related work / overlap

There are multiple S3 clients and server implementations; this kit is **not** another client/server.
It’s the missing “compatibility lab + evidence format” that lets all of them converge.
