# rev0047 Experiment Matrix Additions

| Axis | rev0047 setting |
|---|---|
| Frame queue | rev0046 yield screen |
| Label method | online adaptive branch racing |
| Branch action subset | hybrid legal-action subset selector |
| Branch C++ gate | transition shadow checker |
| Model | JSON-backed linear action ranker |
| Training rows | accumulated audited action-counterfactual rows + rev0047 yield rows |
| Payoff gate | promotion + statistical + replay + C++ shadow |
| Main caveat | payoff truncations remain high |

Recommended next matrix row:

```text
yield-screen queue + lower-truncation payoff settings + stricter nonterminal draw guard
```

