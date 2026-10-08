# P-0515 — Crate Off-Ramp Pack Kit: successor authority, stopgap horizons, and recipe witnesses (2026-03-23)

This note sharpens **P-0515** into a more reviewable product.

## Main judgment

A good off-ramp pack should now publish four receiver-facing truths separately:
1. **successor class** — what kind of replacement is being claimed;
2. **successor authority** — who is actually making that claim;
3. **stopgap horizon** — whether the current answer is temporary, and until when;
4. **recipe witness scope** — which exit recipe actually ran, under what matrix.

That is the difference between a persuasive migration note and a durable support artifact.

## Product stance

The crate should stay small and support-first.
It should not try to become:
- a universal code-rewrite engine,
- a security scanner,
- a registry policy service,
- or an ecosystem-wide maintainer reputation system.

It should instead emit a compact bundle another maintainer or downstream team can answer with:
- who said this is the successor,
- whether that answer is long-term or temporary,
- what exact migration path was exercised,
- and where manual review still begins.

## New first-class artifacts

### `successor-authority.receipt.json`
Suggested fields:
- `crate`
- `subject`
- `claim`
- `authority_class`
- `source`
- `observed_at`
- `long_term_successor` (bool)
- `notes`

### `stopgap-horizon.report.json`
Suggested fields:
- `crate`
- `entries[]`
  - `subject`
  - `stopgap_class`
  - `recommended_until`
  - `review_due`
  - `successor_target`
  - `horizon_verdict`
  - `notes`

### `recipe-witness.report.json`
Suggested fields:
- `crate`
- `recipes[]`
  - `recipe_id`
  - `witness_verdict`
  - `checked_axes[]`
  - `uncovered_axes[]`
  - `observations[]`
  - `notes`

### `offramp-support-bundle.manifest.json`
Suggested fields:
- `crate`
- `bundle_version`
- `includes[]`
  - `kind`
  - `path`
  - `purpose`

## CLI sketch

- `cargo off-ramp capture` — successor class + successor authority + stopgap horizon
- `cargo off-ramp check` — declared recipe + witnessed recipe scope + successor-compat verdicts
- `cargo off-ramp summary` — compact receiver-facing sunset notes
- `cargo off-ramp bundle` — portable manifest joining all artifacts

## Good proving grounds

1. a renamed crate where rustdoc deprecation notes exist, but only the pack declares the long-term successor;
2. a security stopgap where the last-safe pin is real but intentionally temporary;
3. a recipe that updates `Cargo.toml` cleanly but still leaves feature/remap or behavior gaps;
4. an off-ramp bundle that keeps authority, horizon, and witness scope separate.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-yank.html
