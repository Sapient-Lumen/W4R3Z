# rev0070 — two-stage certified support reuse

rev0069's certified reuse was safe but slow because every candidate needed a token-scale outside-bound scan. rev0070 adds a scalar precheck and block-summary sidecar before fallback.

## Result

- Raw anchor quality rate: `0.71875`
- Raw anchor speedup vs dense: `1.12940880106`
- Full token certificate speedup: `0.431117735714`
- Two-stage certificate quality rate: `1`
- Two-stage certificate speedup: `0.538477671054`
- Scalar-certified rows: `70`
- Block-certified rows: `0`
- Fallback rows: `42`
- False certified quality failures: `0`
- Full-token outside-bound scan fraction: `0.279418945312`
- Two-stage sidecar read fraction: `0.09228515625`
- Bound-read reduction: `0.669724770642`

## Interpretation

The two-stage sidecar reduces certificate metadata scans, but it remains non-promotional because speed is still negative on this native CPU trace and the sidecar has not been integrated into a real KV-cache/kernel path.
