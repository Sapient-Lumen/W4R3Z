# Probe: Moment directional gap

Purpose: create synthetic attention cases where top-k cache retention keeps high attention mass but loses a value direction carried by evicted tokens.

Policies:

- top-attention kept-only
- top-attention plus evicted mean
- top-attention plus first-order value-key moment
- random kept-only / random plus moment
- value-norm kept-only

Smoke command:

```bash
python experiments/moment_directional_gap/moment_directional_probe.py --out artifacts/probe-results/REV0005_MOMENT_DIRECTIONAL_SMOKE.json
```

Interpretation: not a faithful implementation of MomentKV. It is a directional-gap falsifier and sandbox for moment-summary approximations.
