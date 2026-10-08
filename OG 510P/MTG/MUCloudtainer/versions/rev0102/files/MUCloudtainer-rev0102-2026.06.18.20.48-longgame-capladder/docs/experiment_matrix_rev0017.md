# rev0017 experiment matrix additions

## C++ transition differential experiment

```text
Question: Can C++ match Python on selected deterministic state transitions?
Input: directed edge states + sampled public gameplay states
Output: post-state signature diff
Gate: zero mismatches
Current result: 5,017 cases, 0 mismatches
```

Next extensions:

```text
stack resolution microcases
Overlord trigger discard microcases
Jace +2 private-choice microcases
Jace Brainstorm putback microcases
cleanup discard / end-turn microcases
```

## Meta-rank payoff experiment

```text
Question: Does population ranking differ from lower-confidence-bound standings?
Input: promotion-gated 8-strategy public payoff table
Output: all-life / 20-life / 40-life meta-rank CSVs
Gate: promotion gate + statistical gate + replay samples
Current result: 512 games, 8 replay samples, promotion/stat gates passed
```

Do not treat this as a metagame claim yet. Pair/life cells are still smoke-scale.
