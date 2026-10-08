# Cargo Rebuild Explanation Kit — product plan (2026-03-22)

## Product thesis

`cargo rebuild-why` should give maintainers, CI reviewers, and performance triagers one **portable support bundle** for a rebuild mystery.
Its job is not to replace Cargo’s session recorder.
Its job is to make one rebuild incident explainable, comparable, and reviewable.

## Who it is for

- workspace maintainers debugging “why did this rebuild?” incidents,
- CI reviewers comparing two specific runs,
- performance engineers triaging one surprising fanout event,
- tool authors importing Cargo build-analysis sessions into stable artifacts,
- downstream teams filing actionable bug reports.

## Core user promises

1. **I can see why this baseline was chosen.**
2. **I can see whether the comparison is compatible enough to trust.**
3. **I can see which units rebuilt and which were reused.**
4. **I can see whether reverse-dependency fanout is merely observed or something stronger is proven.**
5. **I can share one redactable bundle with another reviewer.**

## 0.1 deliverables

### Library

- import/freeze adapters for Cargo build-analysis sessions,
- typed receipts for baseline authority and reverse-impact,
- exactness and evidence-source reporting,
- diff/pack assembly for support bundles.

### Cargo subcommand

- `capture`
- `doctor`
- `diff`
- `pack`

### Bundle contents

- rebuild context,
- rebuild receipt,
- unit-rebuilds,
- evidence-source receipt,
- exactness report,
- baseline-authority receipt,
- reverse-impact report,
- optional timings pointer and cache-conflict overlay,
- human summary.

## First implementation order

1. **Session import + freeze** so nightly Cargo sessions become small stable inputs.
2. **Baseline authority** so the comparison window is explicit and reviewable.
3. **Unit rebuild classification** with exactness labels.
4. **Reverse-impact reporting** so fanout does not get mistaken for proven interface change.
5. **Diff + pack** once the vocabulary stops moving.

## Success criteria

A user should be able to answer all of these from one bundle without re-running the build:

- why was this baseline picked instead of the nearest prior session?
- is this an apples-to-apples comparison or only a caveated one?
- which dependents actually rebuilt?
- do we merely observe fanout, or do we have stronger proof of interface-affecting change?
- what should a human review next before escalating a Cargo bug or performance ticket?

## Anti-goals

- becoming a historical warehouse,
- replacing Cargo timing or report UIs,
- claiming semantic interface proofs Cargo does not provide,
- or swallowing lock-contention / resolver / tool-parity diagnosis.

## Why this is likely shippable

The crate can deliver value immediately because the artifact layer sits above Cargo’s current nightly substrate and can remain useful even while upstream report formats evolve.
That keeps the MVP narrow, stable-first, and adoptable.

## 2026-03-22 later refinement — comparison scope, route drift, and bundle imports

The product surface should now treat three more review objects as first-class:

1. **comparison scope** — whether command family, profile, targets, workspace selection, wrappers, and artifact routes make the sessions comparable enough to explain together;
2. **artifact-route drift** — whether `build-dir`, `target-dir`, rust-analyzer private target-dir, or wrapper hash lanes changed the meaning of reuse expectations;
3. **bundle import visibility** — whether adjacent context from P-0494 / P-0490 / P-0035 stays explicitly imported instead of being flattened into proof.

### Additional 0.1 bundle contents

- `comparison-scope.receipt.json`
- `artifact-route-drift.report.json`
- `rebuild-support-bundle.manifest.json`

### Implementation order adjustment

Insert **comparison scope** between baseline authority and unit rebuild classification.
Insert **artifact-route drift** before final pack assembly.

### Success criterion added

A user should be able to answer all of these from one bundle without re-running the build:

- are these sessions comparable enough to explain together,
- did build-dir / target-dir / tool-owned route drift change the reuse context,
- and which adjacent-lane imports are only context instead of direct rebuild proof?
