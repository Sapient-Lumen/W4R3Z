# Frontier salience snapshot — 2026-03-20 (125)

This pass did **not** promote another generic config framework, another docs.rs helper, or another release-support variant.
It deepened **P-0474 cargo-config-layer-receipt-kit** by making a more boring and more reusable boundary explicit:

- **an effective Cargo config can still overclaim if another team cannot tell whether it came from one real invocation or a later reconstruction, and whether the exported bundle is actually replayable after redaction.**

## Main judgment

The sharper missing layer is no longer merely “show me effective Cargo config”.
The sharper missing layer is an **invocation-basis / replayability contract** above effective-config, origin-trace, and redaction artifacts.

Current Cargo substrate makes that specific:

1. Cargo’s config reference already documents hierarchy, env overrides, `--config` overrides, include graphs, and path-root differences.
2. Cargo 1.94 stabilized the top-level `include` key, which makes shared config graphs and optional per-user includes a stable operational surface.
3. Cargo’s docs are explicit that `--config` values take precedence over env, and env takes precedence over config files.
4. Cargo’s docs are also explicit that env and `--config KEY=VALUE` paths are cwd-relative, while config-file paths are config-root-relative.
5. Cargo treats tokens and credential-provider configuration as sensitive, with credentials living in `$CARGO_HOME/credentials.toml` and providers/aliases adding more redaction-sensitive context.
6. Nightly `cargo config get` exists as inspection substrate, but still is not itself a durable replayable artifact.

That means the next worthy move is not another parser.
It is one conservative crate family that can publish:

- **invocation-basis truth**,
- **replayability truth**,
- plus the already-needed effective-config / origin / path / redaction surfaces.

## Why this beat nearby work

The archive already had adjacent lanes for:

- crate-authored configuration scenarios,
- post-publish Cargo receipts,
- feature/cfg/docs support surfaces,
- and broader docs/build support lanes.

What it still lacked was one compact way to say:

- “this winning config came from `--config`, not the project default files,”
- “this path was cwd-relative, not config-root-relative,”
- “this bundle is safe to attach but not safe to treat as replayable,”
- and “this was reconstructed from files only, not captured from the failing invocation.”

That is a real receiver-facing product boundary, not just another Cargo inspector.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and timeout aftermath truth remain broad pain points.
4. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because downstream test-support truth remains under-served.
5. **P-0474 cargo-config-layer-receipt-kit** — materially stronger after this pass because Cargo config is now a stable enough operational surface that per-invocation truth and replayability truth look like a real shared substrate.
6. **P-0124 schema-compatibility-workbench-kit** — still unusually strong because schema engines exist but one shared review contract above them still does not.
7. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
8. **P-0121 ffi-boundary-conformance-kit** — still important and sharper, but should remain boundary-contract-first.

## What changed in the archive

Added:
- `entries/2026-03-20-305.md`
- `meta/frontier-salience-2026-03-20-125.md`
- `meta/cargo-config-layer-product-plan-2026-03-20.md`
- `meta/cargo-config-layer-lane-boundaries-2026-03-20.md`
- `fixtures/cargo-config-layer-receipt-kit/invocation-basis.receipt.schema.json`
- `fixtures/cargo-config-layer-receipt-kit/replayability.report.schema.json`
- scenario families for invocation-scoped overrides, redaction-sensitive credential providers, and mixed path-root replay traps

Updated:
- `README.md`
- `INDEX.md`
- `proposals/cargo-config-layer-receipt-kit.md`
- `fixtures/cargo-config-layer-receipt-kit/README.md`
- `fixtures/cargo-config-layer-receipt-kit/configbundle.schema.json`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy Cargo config support contribution for Rust should now provide more than a merged config dump and a redaction pass.
It should also provide:

- one explicit **invocation-basis receipt**,
- one explicit **replayability report**,
- and one honest separation between **inspectable** and **replayable** bundles.

## Freshness anchors

- Cargo configuration reference — https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features (`cargo config`) — https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog (1.94 include stabilization; 1.93 precedence/path fixes around `--config`) — https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo 1.93 development-cycle notes on config include design — https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
