# rev0046 audit/refactor notes

## Refactor

The shared attention compiler core now has explicit selector fields for:

- `selection_uses_value_norms`;
- `value_norm_reads`;
- `value_error_bound_from_scores_and_norms`;
- value-norm metadata bytes/read accounting.

This prevents score-only mass certificates and metadata-guarded certificates from being blended together.

## Audit change

`tools/value_norm_stress_and_timing_audit.py` checks four things:

1. mass-only rows that retain target mass but fail output quality are detected;
2. value-norm exception repair is measured against those rows;
3. no selector reports V-vector or dense-output oracle use;
4. native selector timing is labeled selector-only and not promoted as full attention-kernel evidence.

The current scientific run audit and evidence integrity audit were updated to require the new artifacts and preserve promotion block status.
