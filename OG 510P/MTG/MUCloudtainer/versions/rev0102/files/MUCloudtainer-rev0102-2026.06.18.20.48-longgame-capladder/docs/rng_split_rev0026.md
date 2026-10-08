# rev0026 — split RNG contract

rev0026 fixes a fairness seam in public payoff games.

Before this revision, `play_public_agent_game` used one RNG stream for both:

```text
agent tie-break randomness
state-transition randomness
```

That is dangerous.  A public agent that consumes extra random numbers while ranking actions could accidentally change a future Jace ultimate shuffle, even if it chose the same legal actions.  That is not strategic skill; it is RNG coupling.

The new public-game default is:

```text
transition_seed = seed
agent_seed      = seed + 1000003
```

This matches the replay-trace convention introduced earlier.  Agents may use RNG for tie breaks, but that stream no longer affects state transitions.

## Affected path

```python
play_public_agent_game(..., transition_seed=None, agent_seed=None)
```

With defaults:

```python
transition_rng = Random(seed)
agent_rng = Random(seed + 1000003)
```

`public_payoff.py` now records both seeds in payoff rows:

```text
transition_seed
agent_seed
```

## Test added

`tests/test_rev0026_cpprollout_rng.py` includes a burn-agent test.  Two deterministic agents choose the same actions, but one consumes 1,000 extra random values at every decision.  The final game fingerprint remains identical, including Jace ultimate shuffle traffic.

This is a small but important anti-hack boundary: policies should not control transition randomness by varying internal scoring work.
