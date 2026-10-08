# Mission/waste/semantic-drift audit — REV0151

Status: `pass_with_blockers`  
Promotion allowed: `false`  
Created: `2026-07-08T08:52:00-04:00`

## Heart of the mission

CloudtainerML is a claim compiler. The center is not “more notes,” “trust infrastructure,” or “security as a primary product.” The center is a small chain of executable, digest-bound falsifiers that can make or break architectural claims about sparse attention / routing / hard compilers.

The live mission is therefore narrow: produce one real TinyLlama public trace through `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`, then bind it through evaluation, selector-entry, replay, handoff archive, and named-hardware timing receipts. Until that chain exists, this cube remains non-promotional.

## What is missing

- A complete local, digest-authenticated TinyLlama snapshot in this cloudtainer.
- A runnable `torch`/`transformers` capture environment here.
- The real public trace NPZ/provenance pair for the current runner.
- Accepted evaluation, selector-entry, replay, handoff archive, and timing receipts.
- A semantic-currentness audit that catches stale “current” descriptions even when revision numbers and checksums pass.
- A stop rule that says: after static runner smoke, no more doctrine expansion until a capable host either produces the trace or returns a concrete blocker.

## What has gone wrong or become wasteful

1. **Semantic smoke gap.** Rev0150 passed smoke, but top-level fields still described older priorities: `current_primary_change=snapshot_download_plan_gate_refactor`, `highlight=downloadplangate`, and a runner-closure focus inside a runner-manifest-fallback revision.
2. **Baby datacube drift.** `BABY-DATACUBE-CANDIDATE.json` still pointed at rev0149/rev0138 style identities while the package had advanced to rev0150.
3. **Runner-work saturation.** The packet now has many good guards. More guard layers risk hiding the only important absence: no real trace.
4. **Retention regrowth.** Source rev0150 contains 4,384 files and 46,102,375 uncompressed bytes; duplicate-hash groups waste about 8,443,792 bytes.
5. **Copied tool/fixture families.** The largest duplicate group repeats `public_trace_gate_surrogate.py` 23 times. This should become object-addressed content plus pointers, not one physical copy per handoff fixture.
6. **Ledger sprawl.** Hundreds of experiments/questions are alive on paper while the live blocker is one digest-bound public-trace chain.

## What should change next

- Add a `semantic_currentness_audit.py` that rejects stale top-level `current_focus`, `highlight`, `current_primary_change`, `summary`, and baby-datacube identity fields.
- Promote a hard operating rule: either run the capable-machine trace, shrink/normalize repeated artifacts, or fix the first blocker reported by the runner. Do not add a new registry lane.
- Keep the capture split: snapshot/download/materialization may touch network; evidence capture must remain local-only and digest-bound.
- Move bulky duplicated fixture/tool families to an object store such as `objects/sha256/<digest>` with revision manifests pointing to them.
- Keep the external runner packet as the reviewer-facing unit; the full datacube should be provenance context, not the ordinary execution surface.

## Validation note

The source rev0150 cube passed its existing `tools/smoke_validate.py` before this audit revision. This rev adds a non-promotional audit and retargets the active aliases/files to rev0151; it does not claim a public trace.
