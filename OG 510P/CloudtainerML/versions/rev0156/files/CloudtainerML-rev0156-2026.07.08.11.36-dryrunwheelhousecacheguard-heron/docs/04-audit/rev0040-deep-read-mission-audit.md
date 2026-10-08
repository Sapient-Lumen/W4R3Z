# Deep-read mission audit — rev0040

## Executive judgment

The cube has found a real and unusually useful mission: **compile architecture ideas down to hard mechanisms and discover where exactness, routing, memory traffic, or selector cost destroys the apparent win**.

The problem is that its evidence system has begun to reward the appearance of rigor—many reports, guard-field names, revision-stamped outputs—more than the substance of reproducible validity. The scientific instinct is good; the evidence plumbing is not yet trustworthy enough to support promotion.

## What is working

- The project prefers small falsifiers over expensive model training.
- It records negative results and reversal regimes.
- It recognizes that soft sparsity is not deployment evidence.
- It has converged on a timely mechanism family: block indexing, shared routing, hybrid masks, thresholding, and exact temporal Top-K.
- The recent bridge-copy probes expose a useful distinction between probability calibration and ranking quality.

## What is missing

### 1. Immutable run lineage

A result needs command, code hash, input/data hash, environment, seed, raw output hash, timing method, and any derived transformations. Current artifacts mostly have none of these. A revision number is not provenance.

### 2. Evidence tiers and hard vetoes

Symbolic toys, trained tiny models, and measured kernels currently coexist in similar dashboards. Field-presence scores can make them look equally ready. `MISSION-KERNEL.md` now defines E0–E4 tiers and vetoes.

### 3. Real cost

Many `wall_proxy`, `selector_cost`, or `block_cost` values are hand-chosen coefficients. They are useful hypotheses, not performance evidence. Every proxy should expose raw operation/byte/pass counts and be replaced by named-hardware timing before promotion.

### 4. Portfolio stopping

There are hundreds of sources, ideas, cells, and mostly-open questions, with roughly two-fifths of ideas/cells labeled P0. That is not prioritization. P0 is now capped at five repair items.

### 5. A canonical compiler benchmark

The best next asset is not another probe. It is one shared benchmark where identical scores and tasks pass through threshold, Top-K, Top-p, hybrid, block, and temporal compilers. This would let the cube study the deployment gap instead of comparing unrelated toys.

## Severe validity failures

### GVR temporal Top-K — quarantined

`gvr_topk_temporal.cpp` computes true Top-K before evaluating methods and passes the truth set into the proposed GVR method. The method checks whether every true Top-K index is in its candidate set to decide whether to fall back. Its cost excludes this oracle computation. Therefore the exactness and savings claim is invalid. The output remains useful only as a diagnostic of candidate-set behavior.

### Gate compiler “validation” — quarantined

`validation_topk_budget` is implemented in the same branch as `topk_budget3`. It performs no validation-time selection. Naming it as a distinct compiler creates a false comparison.

### Annealed hard bridge gate — negative/mislabeled

The temperature schedule changes an auxiliary sigmoid regularizer but not the forward gate, which still uses raw sigmoid logits. `hard_mix_step` is unused. The result itself is negative: dense/oracle accuracy is perfect while hard compiled accuracy is around 0.37. This is evidence that the current training recipe did not harden—not evidence for annealed hard gating.

### Blockwise index branch — symbolic only

The target block receives a direct synthetic score bonus; the probe evaluates target-block recall, not an attention output; and cost coefficients are assigned rather than measured. It is a useful selector-policy phase toy but cannot substantiate MiniMax/MSA speed or quality.

## Evidence-system failures

- Native audit syntax-compiled only fresh sources and accepted current-named carry-forward JSON for the rest.
- Sparse/compiler reports treated key presence as readiness and always emitted `status: pass`.
- Packaged rev0039 results were modified by a tail-contract patcher after execution, but no derivation lineage was recorded.
- Root revision surfaces disagreed about rev0033, rev0037, rev0038, and rev0039.
- Source IDs contain duplicate papers; one blockwise probe cites the wrong/redundant shared-routing source ID.

## Waste

The rev0039 package is about 246.5 MB unpacked. About 204.1 MB belongs to revision-named logical families, and normalized-JSON analysis estimates about 68.8 MB of repeated content after timestamps/revision labels are removed. Most current probe outputs are carry-forward copies. This is correctable without deleting history: store unique immutable objects once and make revisions thin manifests.

## Speculative north star

The project can become a local **compiler and verification suite for sparse mechanisms**:

```text
observable scores/features
    → selector/index compiler
    → hard layout/program
    → exactness verifier/fallback
    → kernel/memory implementation
    → adversarial and distribution-shift evaluation
```

That is more distinctive than another architecture survey and more defensible than a pile of synthetic winners. The flagship result should be a deployment-gap map: where each compiler wins, reverses, or becomes impossible once exactness and realized cost are enforced.

## Immediate decision

Freeze broad expansion. Repair GVR first, because it tests whether the cube can transform a quarantined result into a provenance-complete, non-oracular, measured experiment without erasing the negative history.
