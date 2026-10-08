# rev0042 repair notes

rev0042 intentionally spends the turn on risky scientific repairs rather than doctrine expansion.

## 1. Bridge annealing forward path repaired

Previous defect: `tiny_bridge_annealed_hard_train.py` used temperature only in an auxiliary regularizer while the actual attention forward path still called ordinary `sigmoid(edge_logits)`. The experiment label therefore overclaimed.

Repair: `AnnealedForwardBoundaryReader` now overrides `gate_probs()` so inherited `soft_gate` attention logits use `sigmoid(edge_logits / T)` and, when enabled, a straight-through hard gate with a small probability floor. The current artifact records `annealing_in_forward_path: true` and includes source hashes.

Finding: hard Top-K deployment remains weak, but threshold deployment reaches perfect accuracy in the tiny bridge-copy world. This is not a promotion; it is a useful compiler lesson that threshold hardening can succeed where Top-K hardening fails.

## 2. Canonical compiler timing added

The canonical sparse compiler benchmark now records `elapsed_ns_python` and `bytes_touched_est` per compiler row, plus platform metadata. This creates pressure against cost-only storytelling.

Caveat: this is Python timing, not C++/CUDA/Triton kernel evidence.

## 3. Block-index selector refactored

Previous defect: the synthetic score directly rewarded the target block, so selector success was partially label leakage.

Repair: the block-index toy now separates hidden target labels from observable selector features: query-phase score, local prior, boundary prior, group offset, and noise. Target labels are evaluation-only except the named `token_oracle_upper` method.

Finding: after removing the direct target-score bonus, block selectors look much weaker. That is a successful falsifier repair, not a failure of the revision.

## 4. GVR and gate repairs rerun

rev0042 reruns the rev0041 GVR and gate-compiler repairs under current revision names with run provenance. No promotion claim changed.

## Remaining promotion blockers

- Real attention-score rows are still missing.
- Kernel-level named-hardware timing is still missing.
- Bridge threshold hardening needs transfer stress.
- Block-index needs an output metric and measured cost beyond proxy rows.
