# rev0047 audit/refactor notes

The audit surface was narrowed around the riskiest current claim: timing. `tools/attention_end_to_end_cpu_audit.py` verifies that the new artifact includes QK scoring, softmax, V accumulation, quality metrics, dense baseline comparison, and explicit non-GPU scope flags.

`tools/evidence_integrity_audit.py` and `tools/smoke_validate.py` were refactored away from rev0046-specific value-norm checks so the current revision validates the actual new evidence instead of requiring stale artifacts to be renamed.

The key overclaim guard is simple: rev0047 may claim native CPU row-attention timing pressure, but it may not claim GPU/fused-kernel performance or model throughput.
