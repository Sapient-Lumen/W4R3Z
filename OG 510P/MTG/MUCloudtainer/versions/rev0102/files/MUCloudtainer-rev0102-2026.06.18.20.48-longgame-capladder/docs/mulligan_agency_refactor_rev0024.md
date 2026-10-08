# rev0024 mulligan agency refactor

The important refactor in rev0024 is that `MulliganObservation` now carries allowed pregame context:

```text
starting_life
deck_counts
```

This matters because the agent is supposed to know its own registered deck and the actual starting life total at gameplay time. Earlier observations exposed the hand and mulligan count but not the construction context, which made learned mulligan policy unnecessarily blind.

The core contract remains:

```text
referee emits legal pregame actions
mulligan agent chooses one legal action
engine applies the choice
```

The engine now accepts learned mulligan agent names through the same lazy factory seam as rule policies. Existing deterministic policy names remain supported:

```text
keep_always
land_band
land_band_business
```

New learned policy name:

```text
mulligan_ranker_rev0024
```

`public_payoff.py`, `payoff.py`, `replay.py`, and `cpp_trace.py` were updated so strategy bundles can carry either deterministic policy names or learned mulligan-agent names.

The replay and C++ trace paths now preserve learned mulligan identity in trace config:

```text
mulligan_agents: [name0, name1]
```

That prevents a subtle replay bug where gameplay traces recorded after a learned mulligan could later be replayed under a deterministic fallback policy and fail fingerprint checks.
