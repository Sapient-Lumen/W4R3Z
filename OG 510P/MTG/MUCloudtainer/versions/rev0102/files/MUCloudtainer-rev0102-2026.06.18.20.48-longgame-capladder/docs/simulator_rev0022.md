# rev0022 simulator note

No core rule semantics were intentionally changed in rev0022. The simulator-facing additions are evaluation and policy-interface work:

```text
ranker blend public agents
ranker/code/public sequential race
MAP-Elites same-deck pilot variants
public payoff agent cache
C++ trace checks attached to new race outputs
```

The authoritative gameplay loop remains:

```text
GameState true state
  -> DecisionFrame public/private-correct observation + legal actions
  -> public agent chooses action index
  -> engine applies exact legal action
  -> replay/fingerprint/C++ gates can audit sampled games
```

rev0022 should therefore be read as a learning/evaluation revision, not a rules expansion revision.
