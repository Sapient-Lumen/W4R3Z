# littlefs lane boundaries — 2026-03-19

This note exists to stop future passes from collapsing several related but distinct ideas into one fake “embedded filesystem crate”.

## Main judgment

The current sharp opportunity is **P-0527 LittleFS Native Adoption Kit**.
That does **not** mean the missing value is simply “write a filesystem in Rust.”
As of March 2026, there is already fresh pure-Rust littlefs work in the ecosystem.

The sharper remaining gap is the **adoption layer** above engines:

- storage-adapter receipts,
- compatibility witnesses,
- power-cut evidence,
- host-side image tooling,
- and compact support bundles.

## Keep these lanes separate

### 1. Raw engine implementation
Questions here:
- is the core implementation safe,
- format-compatible,
- performant enough,
- and maintainable?

This lane can import or extend `littlefs-rust-core`, `littlefs-rust`, or FFI-backed paths.
It is not the whole missing product anymore.

### 2. Storage adapter truth
Questions here:
- what flash/storage traits are supported,
- what granularities and geometry are assumed,
- whether async is native/cooperative/wrapped-blocking,
- and what backend caveats exist.

This lane should import `embedded-storage`, `embedded-storage-async`, and Embassy utilities.

### 3. Compatibility witness workflow
Questions here:
- what images and operation corpora were exercised,
- whether behavior matched expectations,
- and what exact compatibility claim is warranted.

This is not the same as engine implementation.

### 4. Power-cut evidence workflow
Questions here:
- what interruption model was exercised,
- whether remount succeeded,
- and whether the last known good state survived.

This is not the same as saying “littlefs is copy-on-write.”

### 5. Higher-level persistence product lanes
Examples:
- KV stores
- config stores
- OTA partition managers
- log-structured application data models

These should sit above LittleFS support, not be flattened into it.

## Future-pass checklist

When a future pass touches embedded flash/filesystem ideas, ask first whether the missing value is primarily:

1. engine correctness,
2. storage-adapter truth,
3. compatibility evidence,
4. power-cut evidence,
5. host-side image tooling,
6. or an application-layer persistence product.

If the answer is “more than one,” keep the boundary explicit rather than flattening them into one generic proposal.
