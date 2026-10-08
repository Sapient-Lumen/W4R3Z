# Lab Handbook

## AFK Mission Control

`afk_concord.sh` runs long-lived search missions using idle compute.

Typical usage:

```bash
./afk_concord.sh &
tail -f runs/afk_discovery/mission_control.log
```

Mission families currently include:
- candidate discovery under reciprocity constraints,
- adversarial search against current candidates,
- self-play and robustness checks.

## Candidate Gate (`grlab gauntlet`)

`grlab gauntlet` evaluates whether a candidate should be promoted to the discovered pool.

Core checks include:
1. resistance against known adversarial baselines,
2. non-exploitative behavior against pure cooperators,
3. bounded downside against defectors,
4. self-play efficiency,
5. compatibility with reciprocal baselines.

## Artifacts

- `examples/strategies/candidates/` (or legacy `examples/strategies/discovered/`): promoted candidate strategies.
- `examples/strategies/adversaries/` (or legacy `examples/strategies/vampires/`): adversarial counterexamples found by search.

## Observability

Use:

```bash
python3 -m grlab status
```

to summarize trial counts and most recent promoted/counterexample artifacts.
