# rev0026 refactor/audit notes

## Refactor 1: public RNG split

`src/muc5/agents.py::play_public_agent_game` now accepts:

```python
transition_seed: int | None = None
agent_seed: int | None = None
```

Default behavior is deterministic and replay-aligned:

```text
transition_seed = seed
agent_seed      = seed + 1000003
```

`src/muc5/public_payoff.py` records those seed values in payoff rows.

## Refactor 2: mulligan replay aliases

Replay traces store explicit mulligan agent names such as:

```text
mulligan_rule_land_band_business
```

`src/muc5/mulligan_ranker.py::make_mulligan_agent` now accepts these rule-agent names as aliases for their underlying policies.  This makes mixed learned/rule mulligan traces easier to replay through one factory.

## New audit surface

`src/muc5/cpp_rollout.py` adds live rollout preparation and batch finalization.  `scripts/run_rev0026_cpp_shadow_rollout.py` exercises it and writes:

```text
data/rev0026_cpp_shadow_rollout_games.csv
data/rev0026_cpp_shadow_rollout_transitions.csv
data/rev0026_cpp_shadow_rollout_summary.json
```

The cube audit checks the generated shadow rollout has:

```text
144 games
42,458 C++-checked transition events
0 C++ mismatches
0 skipped C++ events
0 Python errors
promotion/statistical gates passed
```
