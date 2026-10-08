# Cargo Build-Dir Consumer Transition Kit — product plan (2026-03-21)

This note sharpens **P-0489 Cargo Build-Dir Consumer Transition Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0489** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

`0.1` should stay migration-first.
It should not promise a universal stable filesystem API for Cargo internals.
It should publish one boring bundle that answers five questions conservatively:

1. **which consumers still rely on Cargo internals**,
2. **what safer adapter is being suggested**,
3. **how strong the authority for that adapter actually is**,
4. **which Cargo/toolchain window that adapter really works in**,
5. **and whether a migration period still requires dual support or fallback behavior**.

The new sharp edge is that adapter advice is no longer timeless.
Cargo's March 2026 build-dir testing post names concrete consumer families and even gives **version-windowed** advice, while Cargo 1.94's changelog shows Cargo itself moving tests toward `CARGO_BIN_EXE_*`.
That means `0.1` needs a first-class **adapter-viability report**, not just a generic adapter plan.

## What `0.1` should provide other people

- one compact `consumer-inventory.manifest.json`
- one compact `layout.snapshot.json`
- one compact `consumer-audit.report.json`
- one compact `path-contract.json`
- one compact `adapter-plan.json`
- one compact `adapter-viability.report.json`
- one compact `transition.receipt.json`
- one compact `transition.diff.json`
- one rendered `transition.summary.md`
- one redacted issue / CI attachment bundle

## What belongs in `adapter-viability.report.json`

At minimum, each consumer-level viability record should say:

- which adapter is being recommended
- whether that adapter is `documented_stable`, `documented_stable_with_version_window`, `documented_nightly`, `heuristic_only`, or an `upstream_gap`
- whether it is usable now, only above a minimum Cargo version, nightly-only, or still manual-review-only
- whether legacy-layout or older-Cargo fallback is still required
- whether migration requires temporary dual support
- and which source class justified the claim

## Commands worth shipping first

- `cargo build-dir-transition scan`
- `cargo build-dir-transition doctor`
- `cargo build-dir-transition diff <old> <new>`
- `cargo build-dir-transition bundle`

`doctor` should be able to render warnings like:

- `adapter_claim_missing_version_window`
- `nightly_only_adapter_marketed_as_stable`
- `older_cargo_fallback_not_recorded`
- `dual_layout_support_required_during_migration`
- `out_dir_contract_claim_exceeds_documented_scope`
- `blocked_on_upstream_but_presented_as_local_fix`

## First proving-ground scenarios

1. **A test helper infers a `[[bin]]` path from a `[[test]]` path**
   - prefer `CARGO_BIN_EXE_*`
   - preserve the Cargo 1.94+ floor and older-Cargo fallback pressure
2. **A build helper recovers target-dir from `OUT_DIR`**
   - keep `OUT_DIR`-for-build-script-owned-output distinct from target-dir recovery
   - downgrade to `heuristic_only` or `manual_review_required` when the consumer need is still ambiguous
3. **A migration rehearsal needs both legacy and new layout handling**
   - `support_both_layouts` is a real temporary plan step, not an implementation embarrassment
4. **A user-requested artifact lookup points toward unstable artifact handoff routes**
   - do not silently promote nightly-only routes into stable adapter claims

## What to leave for later

- automatic source rewriting of downstream helpers
- deep Cargo-as-a-library coupling
- a generalized Cargo path abstraction layer
- organization-wide policy registries for all consumer types
- pretending every currently fragile consumer already has a perfect stable replacement
