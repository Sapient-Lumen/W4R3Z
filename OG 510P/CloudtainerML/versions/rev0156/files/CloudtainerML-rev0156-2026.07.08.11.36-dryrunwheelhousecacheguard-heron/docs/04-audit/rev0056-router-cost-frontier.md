# rev0056 router cost frontier

rev0056 asks whether adaptive routing beats the dense-score histogram under a range of explicit QK/value proxy weights.

## Findings

- Equal-unit adaptive router all-row cost: `543.25`.
- Equal-unit histogram all-row cost: `492.4166666666667`.
- First grid point where router beats histogram on all rows: `qk_weight=12.0`.
- First grid point where router beats histogram on high-support rows: `None`.

## Interpretation

The router is not promotable. The result is useful because it turns a hidden proxy-cost assumption into an explicit veto. Future systems work must measure whether QK score work is actually expensive enough, on the target kernel path, to justify routing overhead.
