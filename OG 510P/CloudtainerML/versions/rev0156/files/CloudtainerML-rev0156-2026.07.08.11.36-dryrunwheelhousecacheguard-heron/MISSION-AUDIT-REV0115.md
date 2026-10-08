# Mission audit — REV0115 deep read / waste / verification-mutation fix

Status: `pass_with_blockers`  
Promotion allowed: `false`  
Package: `CloudtainerML-rev0115-2026.07.06.18.05-missionwasteverifyfix-kestrel`  
Generated: `2026-07-06T18:05:00-04:00`

## Heart of the mission

CloudtainerML is not primarily a sparse-attention manifesto, benchmark archive, or registry. It is a **claim compiler**: take an ML architecture claim, convert it into the cheapest hostile falsifier that could kill it, force exact semantic replay and provenance, then require named-hardware cost evidence before any promotion.

The sparse-attention lane is useful only if it keeps serving that mission. If sparse attention loses on exactness, memory traffic, metadata overhead, or hardware timing, the mission still survives as a reusable evidence discipline for architecture claims.

## What I read

This pass read the top-level entrypoints, rev0076-rev0114 mission audits, metadata/status files, storage-retention history, public-trace capture/gate scripts, handoff toolpack code, and current archive layout. The rev0114 archive contains about 2,780 files / 35,797,110 bytes; common file classes are .md=1092, .json=922, .py=305, .log=124, .cpp=110, .sh=106, .npz=91, <none>=8. The largest retained areas are:

- `artifacts/trace-bundles`: 10,532,598 bytes
- `artifacts/native-inputs`: 8,328,048 bytes
- `artifacts/probe-results`: 5,552,172 bytes
- `artifacts/audit`: 1,642,016 bytes
- `PRUNED-ARTIFACTS.jsonl`: 907,026 bytes
- `artifacts/research`: 708,887 bytes
- `artifacts/probe-result-summaries`: 674,887 bytes
- `FILE-MANIFEST.json`: 555,733 bytes
- `artifacts/bin`: 461,328 bytes
- `artifacts/run-manifests`: 384,594 bytes

## What is missing

1. **The decisive public trace.** The cube still lacks a real immutable public TinyLlama trace NPZ/provenance pair produced from the intended runtime and accepted by the current public-trace gate.
2. **The real endgame receipts.** The evaluation receipt, selector-entry receipt, selector replay, and portable handoff archive are currently fixture-proven rather than real-trace-proven.
3. **Named-hardware sparse-vs-dense timing.** Promotion still needs end-to-end timing on named hardware, not just CPU fixtures, native-input sidecars, or logical read reductions.
4. **A serious baseline bracket.** The performance claim must face modern dense/system baselines: FlashAttention-style IO-aware exact attention, vLLM/PagedAttention-style KV management, PyTorch/FlexAttention-style block-mask execution, and sparse/KV-cache methods such as H2O, StreamingLLM, MInference, and newer sparse-aware serving systems.
5. **A stop/pivot rule.** If the real trace environment remains unavailable, the cube should explicitly pivot to the reusable claim-compiler product rather than keep adding gate layers around absent evidence.
6. **Read-only reviewer verification.** Packaged evidence must be checkable without mutating the package being checked.

## What has gone severely wrong or wasteful

### Corrected severe wrongness already in the lineage

The cube has corrected several defects that could have produced impressive but false green checks: pre-transform projection capture being treated as scored Q/K, self-attested dense parity, missing score mask/scale, custom attention paths that could drop masks, prefill-only traces standing in for cached decode, local q_len decode positions, physical-cache width being confused with active key length, GQA duplicated-K/V accounting, weak prompt/generated-token replay, stale metadata, selector-receipt overwrite, and path-local handoff verification.

Those corrections are real. They are also a warning: the project is good at finding false positives, so every new green check should be treated as provisional until it is attached to real trace and hardware evidence.

### Newly found severe reviewer hazard

The rev0114 `START_HERE.md` tells a cold reviewer to run:

```bash
python tools/public_trace_cold_reviewer_verify_audit.py
python tools/public_trace_standalone_toolpack_audit.py
python tools/smoke_validate.py
```

On a fresh extraction, `smoke_validate.py` passed before those commands. After running the first two commands, `smoke_validate.py` failed because tracked audit/fixture artifacts changed and Python cache files were created under the package tree. The changed tracked files were:

- `artifacts/audit/REV0114_PUBLIC_TRACE_COLD_REVIEWER_VERIFY_AUDIT.json`
- `artifacts/trace-bundles/REV0114_STANDALONE_TOOLPACK_FIXTURES/REV0114_portable_handoff_toolpack_fixture.zip`

Several `__pycache__` files and nested gate-output files also appeared in fixture directories. That is exactly the kind of evidence-hygiene violation the cube is supposed to prevent: verification of an immutable archive should not rewrite the archive.

### Waste that can be corrected over time

The storage-retention policy already names the right cure: content-addressed objects, run manifests, revision pointers, and generated latest views. The current package is much slimmer than the historical baseline, but fixture trees and repeated archive/gate outputs still consume attention and bytes. The most expensive waste is not the remaining megabytes; it is the reader's effort separating current evidence from historical fixture archaeology.

## What changed in rev0115

- Added `--no-write` to the handoff archive gate and selector-receipt replay gate.
- Added `--no-write` / scratch execution to the standalone-toolpack and cold-reviewer audits.
- Changed the root `VERIFY_HANDOFF.py` launcher to delegate to the strict gate in no-write mode.
- Changed current entry docs so cold-reviewer verification starts with checksum validation and uses no-write commands.
- Added this deep-read audit plus online-research notes.

## What should change next

1. Run the real TinyLlama trace in a capable environment or record an explicit stop/pivot memo. Do not spend another turn on doctrine-only gates.
2. Treat packaged archives as immutable: reviewer commands must either be pure read-only checks or write only to an explicit scratch/run directory outside the package.
3. After a real trace passes, immediately run the receipt/handoff chain and then named-hardware dense-vs-sparse timing.
4. If sparse attention loses, preserve the evidence compiler as the durable product: reusable hostile falsifiers, trace contracts, provenance receipts, and promotion vetoes.
5. Collapse current operator surfaces toward one decision lane: `trace -> receipt -> handoff -> timing -> promote/stop/pivot`.

## Speculation

My strongest speculation is that the sparse-attention mechanism is less likely to win as an abstract "read fewer scores" claim than as a systems-co-designed claim with block/page-aligned KV layout, amortized metadata, and a narrow workload target. The external literature is pressuring the cube in that direction: the hard part is not discovering sparsity; it is making sparsity survive IO, cache layout, GPU kernels, scheduling, and end-to-end latency.

The best near-term bet is therefore not "prove sparse attention broadly." It is: capture one real trace, choose one concrete selector/cost lane, compare against strong dense and KV-management baselines on named hardware, then either kill the lane or turn the surviving verifier pattern into a claim-compiler product.
