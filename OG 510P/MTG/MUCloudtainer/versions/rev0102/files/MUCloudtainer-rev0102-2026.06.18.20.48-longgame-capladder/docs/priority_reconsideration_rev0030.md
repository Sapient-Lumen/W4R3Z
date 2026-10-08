# rev0030 priority reconsideration

Current priority order after rev0030:

```text
1. Scale repeated opening-hand counterfactuals: more situations and more branch rollouts.
2. Build a C++ no-choice segment checker from the new segment fingerprints.
3. Run larger MAP-Elites races including repeated/counterfactual mulligan variants.
4. Add search/rollout targets for unchosen gameplay actions.
5. Meta-rank over denser, nontruncated promoted payoff tables.
```

The biggest update is that repeated counterfactuals helped the data shape but did not magically solve mulligans. The next leap is budget: more paired openings, more rollouts per branch, and probably staged racing so we do not spend equal compute on obvious ties.

Do not start full C++ tournament authority yet. The next C++ target should be no-choice segment parity.
