# rev0032 priority reconsideration

The next priorities are now:

1. **No-choice segment execution benchmark.** We have batched segment checking; the next question is how much wall-clock benefit we get if C++ actually executes forced segments in live rollouts while Python checks pre/post signatures.
2. **Larger MAP-Elites races.** rev0032 uses only a 96-game smoke panel. The same machinery should run denser nontruncated tables before any metagame claim.
3. **Search labels for unchosen gameplay actions.** Outcome-weighted behavior cloning cannot value unchosen legal actions; rollout/search labels are the next learning upgrade.
4. **Repeated mulligan counterfactual scale-up.** More openings and more branch rollouts matter more than model cleverness.
5. **Meta-rank on promoted tables.** Meta-rank becomes meaningful only after payoff tables are denser and nontruncated.

Do not jump straight to a full C++ engine. rev0032 found a segment-state actor bug precisely because the C++ path was still shadowed and differential-tested.
