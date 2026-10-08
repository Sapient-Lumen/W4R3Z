# Entropy-guided budget probe

Tiny synthetic test for head/segment budget allocation. The question is whether
attention entropy is a useful online signal for allocating sparse attention or KV
retention budgets, and whether a decode-conditioned signal is needed for late
importance shifts.

Run:

```bash
python experiments/entropy_guided_budget/entropy_head_probe.py
```
