# KV Wind Tunnel probe

Script: `experiments/kv_wind_tunnel/kv_wind_tunnel.py`

Purpose: stress-test cache quantization variants in a pseudo-decode loop where small cache errors can feed back into future queries.

This is inspired by current KV-cache quantization work, especially the claim that decode-time evaluation exposes accumulating errors that prefill-style static reconstruction can miss.

## What it does

- Creates synthetic K/V tensors with optional token-scale outliers.
- Quantizes K/V using several crude variants: global, row/token-wise, column/channel-wise, variance-normalized, Hadamard-rotated, and combinations.
- Runs a recurrent pseudo-decode loop where attention outputs update the next query state.
- Compares every quantized run against an fp32 reference trajectory.

## What to look for

- Does attention-output error accumulate across steps?
- Do row/token-scale outliers hurt more than average MSE predicts?
- Do Hadamard rotation or variance normalization reduce the top-tail failures?
- Does argmax agreement remain high while hidden-state trajectory still diverges?

## Run

```bash
python experiments/kv_wind_tunnel/kv_wind_tunnel.py --quick --out artifacts/probe-results/manual-kv.json
```
