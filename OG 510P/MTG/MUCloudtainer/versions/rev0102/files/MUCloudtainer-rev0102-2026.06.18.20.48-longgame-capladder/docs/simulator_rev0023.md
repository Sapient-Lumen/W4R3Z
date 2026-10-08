# rev0023 simulator note

No new card rules were added in rev0023.

The simulator-facing changes are evaluation changes:

```text
new MLP public agent names
new strategy-bundle panels
new mulligan-policy gate
new payoff/replay/C++ trace artifacts
```

The referee contract remains:

```text
GameState true state stays inside engine
DecisionFrame exposes public/private-correct observation
legal actions are enumerated by referee
agent returns action index
engine applies legal action
```

This preserves the original narrow MUC plan: do not teach agents legality through illegal-action penalties; give them a legal menu and make them learn which legal move matters.
