# rev0077 refactor audit

The refactor is small and executable: sampling-frame classification is centralized in `src/muc5/population_sampling.py` instead of being inferred ad hoc from filenames or revision numbers inside analysis scripts.

New shared functions:

```text
sampling_frame_for_row(row)
annotate_sampling_frame_rows(rows)
global_pool_source_rows(rows)
sampling_frame_summary_rows(rows)
adaptive_pooling_guard(rows)
```

Why this matters:

- Broad pooled promotion gates must only consume complete, preregistered population panels.
- Adaptive follow-up evidence must remain available for selected-stratum challenges.
- Unknown future rows fail closed rather than being accidentally included.

The revision also ships compact CSV outputs rather than raw games or transition logs. Artifact limits enforce that rev0077 adds no new bulk evidence.
