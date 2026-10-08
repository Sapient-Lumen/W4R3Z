# Hot substrate watchcard: Machine-readable tooling surfaces (2026-03)

## Lane
- machine-readable tooling surfaces watch
- drift horizon: **warm-to-hot**

## Authoritative sources
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/beta/rustc/json.html
- https://docs.rs/about/rustdoc-json
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html

## Imported truths
- Cargo still frames structured outputs plus custom subcommands as the stable extension path.
- `cargo metadata`, rustc JSON, and docs.rs rustdoc JSON are important imports but they carry compatibility caveats.
- libtest JSON is strengthening the testing substrate but is still a moving target.

## Non-claims
- there is no single universal stable schema for everything;
- adapter and provenance layers are still required;
- Tooling Contract remains a multiplier seam, not the first whole product to build.

## Current implication
Future assistants should preserve format-version and opacity warnings and prefer importer/adapter/receipt families over universal-schema fantasies.

## Downstream assets most likely to care
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`

## Reissue triggers
- libtest JSON lands or shifts materially;
- docs.rs rustdoc JSON access or retention changes;
- Cargo/rustc compatibility notes change materially.

## What did not change
- the broad top-band ladder;
- the archive still refuses a one-framework-fixes-everything story.
