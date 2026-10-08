# Cargo build-dir transition lanes — known failure modes, honest adapters, and neighbor crates (2026-03-16)

Purpose: keep **P-0489 Cargo Build-Dir Consumer Transition Kit** focused on the missing migration artifact instead of collapsing several different path problems into one vague “Cargo layout broke us” story.

## Why this note exists now

Cargo's March 2026 **Build Dir Layout v2** call for testing made the downstream failure modes much more explicit:

- many projects still rely on unspecified build-dir details,
- maintainers are asked to test anything touching build-dir or target-dir under `-Zbuild-dir-new-layout`,
- and the post lists concrete breakage families instead of only abstract warnings.

That is exactly the moment where the archive should get **more lane-honest**, not less.

## Keep these lanes separate

### 1. Bin-path inference from test paths
Typical smell: a test or helper infers a `[[bin]]` path from a `[[test]]` path.

Sharper likely adapter:
- `CARGO_BIN_EXE_*` when available,
- maybe a temporary older-Cargo fallback.

This is not the same as build-script output or general build-dir scraping.

### 2. Build-script / helper recovery of target-dir from `OUT_DIR` or executable paths
Typical smell: a helper walks upward from `OUT_DIR` or from its own binary path to guess workspace topology.

Sharper likely adapter:
- sometimes `OUT_DIR` if the real need is build-script-owned output,
- otherwise still `manual_review_required` or `blocked_on_upstream`.

Do not silently treat “`OUT_DIR` exists” as proof that target-dir recovery is solved.

### 3. User-requested artifact lookup
Typical smell: a consumer wants one requested artifact but scrapes compiler-oriented locations to find it.

Sharper likely adapter:
- final-artifact handoff or JSON-driven artifact reporting,
- possibly unstable `artifact-dir` in rehearsals,
- or an explicit upstream gap.

Do not silently collapse this into intermediate-layout migration.

### 4. Broad build-dir / target-dir topology migration
Typical smell: a tool genuinely depends on current build-dir organization, profile buckets, or target nesting.

Sharper crate:
- **P-0489** itself.

This is the lane for consumer inventory, path contracts, adapter plans, and transition receipts.

## Neighbor-crate boundaries that must stay visible

- **P-0471 Cargo Artifact Handoff Kit** — final artifact handoff.
- **P-0490 Cargo Lock Contention Witness Kit** — live waits and blocking topology.
- **P-0486 Debuggability Support Contract Kit** — symbol sidecars / support posture above artifact location.

Do not let future passes silently merge these into one fake “Cargo paths crate”.

## What a worthy P-0489 bundle should preserve now

At minimum, preserve:

1. which failure-mode lane the consumer belongs to,
2. what evidence supports that classification,
3. which adapter is actually documented versus merely inferred,
4. whether the consumer must support both old and rehearsed layouts temporarily,
5. and whether the case is truly blocked on upstream rather than locally fixable.

## Sources

- Build Dir Layout v2 call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo unstable docs (`artifact-dir`, `build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo build scripts docs: https://doc.rust-lang.org/cargo/reference/build-scripts.html
