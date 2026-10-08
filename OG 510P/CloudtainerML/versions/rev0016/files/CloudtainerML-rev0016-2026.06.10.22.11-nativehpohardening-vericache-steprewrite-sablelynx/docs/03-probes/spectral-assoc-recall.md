# Spectral associative recall probe

Script: `experiments/spectral_assoc_recall/spectral_assoc_probe.py`

Purpose: compare exact attention-like retrieval against constant/low-rank associative memories under generated key-value recall tasks.

## What it does

- Generates continuous keys and value prototypes.
- Queries are noisy copies of stored keys.
- Key correlation can be increased to create crosstalk/collision stress.
- Compares nearest-neighbor attention, additive linear memory, ridge memory, low-rank ridge memory, and online delta-rule memory.

## What to look for

- Does linear memory fail from crosstalk before exact attention does?
- How much rank is needed before compressed memory stops being fake full-cache storage?
- Does online delta memory remember early facts or drift toward later ones?
- Do context gates or spectral summaries deserve a next implementation?

## Run

```bash
python experiments/spectral_assoc_recall/spectral_assoc_probe.py --quick --out artifacts/probe-results/manual-assoc.json
```
