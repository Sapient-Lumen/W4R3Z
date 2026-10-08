# Moment directional-gap probe

A pure NumPy approximation of the MomentKV intuition: top-k cache retention can preserve most attention mass while losing a value direction carried by evicted tokens. The probe stores compact evicted-set moments and compares output reconstruction.

Run:

```bash
python experiments/moment_directional_gap/moment_directional_probe.py --out artifacts/probe-results/REV0005_MOMENT_DIRECTIONAL_SMOKE.json
```
