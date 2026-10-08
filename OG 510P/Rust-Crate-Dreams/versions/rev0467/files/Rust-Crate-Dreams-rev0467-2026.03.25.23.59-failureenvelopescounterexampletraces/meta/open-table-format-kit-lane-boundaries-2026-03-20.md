# open-table-format-kit lane boundaries — 2026-03-20

This note keeps **P-0028 open-table-format-kit** from collapsing into fake “supports multiple lakehouse formats” language.

An open-table-format support crate must keep at least these eight truths separate:

1. **what identifies the table**,
2. **whether the table surface is live or pinned**,
3. **which read modes are supported**,
4. **which write / maintenance modes are supported**,
5. **which engine registration paths are supported**,
6. **which storage/catalog schemes are wired**,
7. **how tightly the integration is coupled to DataFusion / bindings**, and
8. **which gaps are native limitations versus binding/adapter omissions**.

## What belongs in this lane

The lane is about questions like:

- Is this subject catalog-backed with live refresh, or a static metadata/snapshot registration?
- Does the subject support snapshot reads only, or also time travel / incremental windows?
- Are write and maintenance operations genuinely wired for this path, or only documented elsewhere?
- Is a storage backend supported in the underlying Rust crate but missing in one binding/export path?
- Does the integration require exact DataFusion version matching, or can it cross an FFI boundary more safely?
- Which capability differences are format-native and which are adapter-local?

## What does **not** belong here

Do **not** collapse this seam into:

- a new universal table format,
- a full metadata replay / catalog bug workbench (that belongs closer to **P-0359**),
- generic query-engine execution planning,
- a storage SDK,
- or a lakehouse marketing matrix.

Those may contribute evidence, but this lane is specifically the receiver-facing contract for **table surface**, **capabilities**, and **integration coupling**.

## Preferred artifacts

If this lane keeps sharpening, prefer tiny artifacts such as:

- `table-surface.receipt.json`
- `capability-profile.report.json`
- `integration-coupling.receipt.json`

The point is not to produce another engine.
The point is to make it reviewable whether a consumer is looking at:

- `catalog_live_refresh`,
- `static_snapshot_pin`,
- `time_travel_pin`,
- `incremental_window`,
- `row_level_dml_supported`,
- `binding_gap`,
- `datafusion_exact_version_match_required`,
- or `ffi_table_provider_decoupled`.

## LLM/archive reminder

Do **not** let future passes rephrase this seam as:

- “Rust has Iceberg, Delta, and Hudi now,”
- “the query engine can register a provider,”
- “the storage backend is supported somewhere,”
- or “there is a common trait, so the problem is solved.”

The sharper missing value is a receiver-facing contract that says **what table surface is actually exposed, what operations are really wired, and how much integration coupling debt comes with it**.
