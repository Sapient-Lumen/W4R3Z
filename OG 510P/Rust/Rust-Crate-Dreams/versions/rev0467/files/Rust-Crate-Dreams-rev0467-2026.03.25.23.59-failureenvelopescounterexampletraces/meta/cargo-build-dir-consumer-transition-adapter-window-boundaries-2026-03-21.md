# Cargo build-dir transition adapter-window boundaries — 2026-03-21

This note keeps **P-0489 Cargo Build-Dir Consumer Transition Kit** from collapsing “an adapter was suggested” into fake migration certainty.

## The sharper seam

Within **P-0489**, keep these truths separate:

1. **a consumer was classified into a known failure-mode lane**,
2. **a path contract or safer adapter was suggested**,
3. **that adapter is actually documented / supported in a specific Cargo window**,
4. **fallback or dual-layout support is still required**,
5. **and the overall transition verdict is still safe, risky, or blocked**.

Those are related, but they are not the same claim.

## What belongs in the adapter-window seam

The adapter-window seam is about questions like:

- Is the suggested adapter documented on stable, documented only for a newer Cargo floor, nightly-only, heuristic-only, or still an upstream gap?
- Does the migration still need older-Cargo fallback behavior?
- Does the migration need temporary support for both legacy layout and rehearsed new layout?
- Is the crate borrowing a point fix from a blog post or changelog without preserving its scope conditions?
- Is a named adapter actually outside the current consumer's documented scope?

## What it is not

### 1. Not consumer classification by itself

A consumer can be correctly classified as `bin_path_from_test_inference` or `target_dir_from_out_dir_inference` and still have an overclaimed migration path.
Classification asks **what kind of breakage this is**.
Adapter-window truth asks **how far the proposed fix really travels**.

### 2. Not path-contract truth by itself

A path contract can honestly say `build_script_out` or `final_artifact`.
That does not prove every adapter for reaching that contract is stable in the consumer's Cargo window.

### 3. Not transition verdict by itself

A `manual_review_required` or `adapter_available` verdict is downstream summary judgment.
The adapter-window seam is the evidence explaining **why** a named adapter is strong enough, conditional, or still weak.

### 4. Not a universal compatibility matrix for all of Cargo

This seam is narrowly about the adapters named by **P-0489**.
Do not let it expand into a giant version matrix for unrelated commands or crate ecosystems.

## Receiver-facing artifacts to prefer

- `adapter-plan.json` — which next move is being suggested
- `adapter-viability.report.json` — how strong that suggestion really is, in what Cargo window, with what fallback pressure
- `transition.receipt.json` — summary verdict after combining consumer evidence, adapter viability, and residual risk

## Anti-patterns

Do **not** let future revisions treat these as interchangeable:

- “the crate suggested `use_cargo_bin_exe`”,
- “that adapter is documented for this Cargo window”,
- “no fallback is needed”,
- “the migration is safe”.

They are adjacent truths, not one migration fact.
