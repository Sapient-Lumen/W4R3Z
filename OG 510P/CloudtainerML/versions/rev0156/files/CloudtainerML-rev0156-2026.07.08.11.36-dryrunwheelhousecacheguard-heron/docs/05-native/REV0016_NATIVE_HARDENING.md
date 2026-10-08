# REV0019 native hardening notes

C++ is now the default for stable high-volume symbolic/tensor probes. Python remains the report/dashboard/training layer.

## New probes

### VeriCache guard wind tunnel

Simulates lossy KV decode drift across long generations with critical tool-call sites. Compares full KV, lossy/no guard, periodic refresh, margin guard, drift guard, a toy verifier guard, and oracle risk guard.

### Periodic cache rewrite

Simulates reasoning traces with step boundaries, needed facts, distractors, and recurrent definitions. Compares continuous eviction, fixed periodic rewrite, step-boundary rewrite, attention-style reconsolidation, and oracle step rewrite.

### Memory provenance phase

Sweeps user-misbelief rate, correction loss, and high-stakes rate. Compares no persistent memory, belief snippets, recency memory, provenance-balanced memory, skeptical high-stakes memory, correction-linked memory, and oracle provenance.

## Next native hardening candidates

- Add catastrophic-tail metrics to older lossy cache probes.
- Run HPO-style threshold sweeps for verifier guard risk signals.
- Replace hard step boundaries with learned/event-driven rewrite triggers.
- Add a richer cost model for provenance memory: correction source, confidence, timestamp, stakes, and opt-out behavior.
