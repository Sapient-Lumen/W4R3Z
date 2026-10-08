# rev0022 priority reconsideration

Previous priority:

```text
1. Sequential racing with ranker/code/public populations.
2. MAP-Elites cells evaluated with ranker policy variants.
3. Tiny MLP/listwise ranker.
4. Batched C++ rollout only after replay/fingerprint gates.
```

rev0022 completes the first two at smoke scale.

## What we learned structurally

- Ranker policies can now enter staged races, not just full round-robin tables.
- MAP-Elites construction cells can be compared under multiple pilots on the same deck shell.
- C++ recorded-trace checks are now part of new evaluation scripts, not an isolated benchmark.
- The public payoff cache avoids repeatedly loading the same frozen ranker model.

## New priority order

1. **Tiny listwise/MLP ranker only if it uses the same public feature/action interface.**
   The linear ranker is useful as a baseline but weak. A tiny MLP or gradient-boosted action scorer is now justified if it is frozen to JSON-like artifacts and enters the same gates.

2. **C++ batch rollout sketch from traces, not full tournament core.**
   The next C++ step should consume prepared trace/transition batches and report cost/coverage. Full authoritative rollout remains later.

3. **Race larger MAP-Elites panels with sequential budget allocation.**
   The next construction question is not one top deck. It is which descriptor cells remain alive under staged evaluation.

4. **Mulligan learning.**
   We have kept mulligans agent-facing. The next learning target may be pregame keep/take/bottom decisions, because bad mulligans poison all later policy comparisons.

5. **Alpha/meta-rank over promoted, nontruncated tables.**
   Useful after payoff density improves. Smoke rankings are not enough.
