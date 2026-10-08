# rev0050 refactor / audit notes

Added:

```text
src/muc5/terminal_meta.py
scripts/run_rev0050_terminal_meta_claimgate.py
tests/test_rev0050_terminal_meta.py
```

The new module separates population-analysis logic from the payoff runner:

```text
terminal_meta_rank_rows(...)
life_split_stability_rows(...)
rank_disagreement_rows(...)
claim_ledger_rows(...)
terminal_meta_gate(...)
```

That separation matters because later terminal-clean panels should be able to reuse the same analysis code without copying a large script body.

The cube audit now checks that the rev0050 panel is terminal-clean, promotion/statistical/meta gates pass, meta-rank mass sums to 1.0, claim-ledger rows exist, and C++ shadow/trace checks remain clean.
