# rev0023 result notes

This file is generated as a narrative companion to the machine-readable summaries.

Read these outputs first:

```text
data/rev0023_mlp_ranker_summary.json
data/rev0023_mulligan_policy_gate_summary.json
```

Interpretation rules:

1. Strong supervised MLP metrics mean the model imitated baseline policies; they do not mean the policy is strategically strong.
2. A mulligan policy result is not a deck result unless the deck and pilot shell are held fixed.
3. Any row with truncation must be handled by reward/promotion gates before it can influence training or selection.
4. C++ trace success is a parity check on sampled traffic, not a complete proof of full C++ simulator correctness.
