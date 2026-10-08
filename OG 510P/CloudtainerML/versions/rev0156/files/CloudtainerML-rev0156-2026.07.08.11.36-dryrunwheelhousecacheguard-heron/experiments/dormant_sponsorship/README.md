# Dormant-token sponsorship probe

Symbolic proxy for semantic sponsorship: anchors such as `key:`/`id:`/`config:` protect adjacent value tokens that would otherwise have near-zero direct attention.

Run:

```bash
python experiments/dormant_sponsorship/dormant_sponsorship_probe.py --quick --out artifacts/probe-results/REV0004_DORMANT_SPONSORSHIP_SMOKE.json --csv artifacts/probe-results/REV0004_DORMANT_SPONSORSHIP_SMOKE.csv
```

Useful for asking whether attention-score cache retention has an inherent blind spot for dormant values.
