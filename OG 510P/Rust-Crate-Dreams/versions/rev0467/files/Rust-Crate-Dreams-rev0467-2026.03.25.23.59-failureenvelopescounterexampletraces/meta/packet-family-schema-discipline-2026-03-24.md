# Packet-family schema discipline — 2026-03-24

This note gives the archive a smaller and more reusable answer to:

> if the leading crates all emit receipts, reports, manifests, packs, locks, notes, matrices, and imports, what should those artifact families mean in theory and practice?

## Main judgment

The next missing value is **not** another generic “export JSON” story.
It is a shared discipline for packet families so future crates can hand other people files that are:
- predictable,
- replayable,
- composable,
- and harder to over-read.

The archive should now assume that a worthy crate usually exports a **small schema family** rather than one giant blob.

## Why this matters now

Current official Rust substrate keeps pushing in the same direction:

- Cargo’s plumbing work is explicitly about programmatic stages and says schema evolution must be planned rather than improvised.
- Cargo build-analysis work is about recorded metadata across invocations, not just pretty terminal output.
- `Cargo.lock` already carries a strong cultural expectation of replayable, stable semantics across versions.
- docs.rs rustdoc JSON is explicitly format-versioned and recipe-bound.
- the libtest JSON work exists because once machine-readable output becomes operationally useful, downstream tools start depending on it.

That means the archive should stop treating packet naming and schema discipline as cosmetic.
It is part of the product.

## Packet-family meanings

### `*.receipt.json`
Meaning:
- a narrow statement of **observed or imported fact**;
- usually tied to one authority surface, one capture route, or one exact basis.

Good use:
- `citation-locator.receipt.json`
- `build-surface.receipt.json`
- `selection-anchor.receipt.json`

Should refuse to do:
- multi-step judgment,
- scoring,
- policy verdicts,
- or hidden inference.

### `*.report.json`
Meaning:
- a **derived judgment** or analysis above one or more receipts/imports.

Good use:
- `claim-trace.report.json`
- `parity-gap.report.json`
- `source-coverage.report.json`

Should declare:
- which lower artifacts it depends on,
- what exactness level it uses,
- and where manual review still applies.

### `*.manifest.json`
Meaning:
- a **composition or inventory file**;
- names the members of a bundle, their roles, and their intended use together.

Good use:
- `knowledge-pack.manifest.json`
- `debug-support-bundle.manifest.json`
- `review-packet.manifest.json`

Should refuse to do:
- hide evidence semantics inside one opaque super-document.

### `*.matrix.json`
Meaning:
- support or answerability **across explicit dimensions**.

Good use:
- `query-support.matrix.json`
- `format-window.matrix.json`

Should make axes explicit:
- query class,
- target,
- feature set,
- schema version,
- or audience class.

### `*.lock`
Meaning:
- a **frozen replay basis** that should be stable enough to compare or reopen later.

Good use:
- `source-parity.lock`

Should refuse to become:
- a generic scratch file,
- latest-view cache,
- or human prose explanation.

### `*.import.json`
Meaning:
- imported evidence from another authority surface that remains **semantically distinct** from local observation.

Good use:
- `docsrs-presence.import.json`
- `mirror-verification.import.json`

Should always preserve:
- provenance,
- capture route,
- time or version context,
- and the fact that this evidence was imported rather than locally derived.

### `*.pack.json`
Meaning:
- a compact **machine-facing slice** optimized for downstream use, with explicit exclusions and support ceilings.

Good use:
- `assistant-context.pack.json`

Should never be the only artifact.
A pack should point back to receipts, reports, manifests, and notes.

### `*.note.md`
Meaning:
- the short human-facing explanation, caveat list, or manual-review guidance.

Good use:
- `manual-review.note.md`
- `answer-boundary.note.md`

Should not pretend to be machine-authoritative.

## Required cross-cutting fields

Every structured packet family should prefer a compact shared spine such as:

- `schema_name`
- `schema_version`
- `crate` or `subject`
- `capture_basis` or `derived_from`
- `exactness`
- `generated_at`
- `notes`

Not every file needs every field.
But future passes should assume some versioned identity and some lineage pointer are mandatory.

## Schema evolution rules

### Rule 1 — version structured output deliberately
If a downstream consumer could parse it, give it a schema version.

### Rule 2 — prefer more small files over one blurry blob
Multiple packet types are a feature, not a failure, when they keep fact, judgment, and composition separate.

### Rule 3 — keep imported evidence distinct from local evidence
Do not silently flatten docs.rs, crates.io, mirror, or registry data into “what the workspace knows”.

### Rule 4 — freeze replayable bases separately from latest-view browsing routes
A pinned citation or decision packet is not the same thing as a `latest` link.

### Rule 5 — make manual-review zones first-class
If a question class or scenario cannot be answered honestly, the schema family should carry that fact explicitly.

## What this implies for the leading crates

### P-0509 Pathfinder
Should emit small decision packets with locks/manifests/notes and defer evidence basis to P-0536.

### P-0536 Crate Knowledge Pack
Should provide the pinned receipt/report/pack stack that other lanes can import.

### P-0486 Debuggability Support
Should use the same family semantics so capability witnesses, claim ceilings, and bundle manifests compose with pathfinder packets.

### P-0496 Source Parity
Should keep source receipts, coverage reports, imported mirror verification, and parity locks distinct.

## Product rule

A worthy crate here should make one downstream question boring:

> what kind of packet is this, how stable is it, what exactly supports it, and what must I still review manually?

If the crate cannot answer that cleanly, it is not yet exporting a real contract.

## Sources

- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
