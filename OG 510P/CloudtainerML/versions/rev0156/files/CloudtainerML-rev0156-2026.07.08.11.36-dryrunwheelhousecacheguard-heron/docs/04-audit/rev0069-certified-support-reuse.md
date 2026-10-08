# rev0069 — certified support reuse

Raw support reuse was the risky loophole left by rev0066: it saved QK work but failed quality. rev0069 adds an observable Q/K/key-drift mass certificate and pays fallback work inside the timed loop.

## Result

- Raw anchor quality rate: `0.71875`
- Raw anchor speedup vs dense: `1.27000422603`
- Certified quality rate: `1`
- Certified speedup vs dense: `0.481626916939`
- Certified reuse rows: `70` / `112`
- False certified quality failures: `0`
- Certified QK dot fraction: `1`
- Bound metadata scan fraction: `0.279418945312`

## Interpretation

['actual_public_pretrained_trace_bundle_missing', 'gpu_fused_attention_kernel_timing_missing', 'certificate_fallback_or_metadata_scan_erases_support_reuse_speedup', 'full_or_near_full_qk_work_required_for_certified_quality', 'no_deployable_score_path_sparse_win_measured']

The certificate repairs the invalid fast path, but it does not create a promotion-ready sparse systems win on the local trace.
