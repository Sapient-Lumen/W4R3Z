# rev0014 refactor and audit notes

## Public-agent action parameter refactor

rev0014 fixed two public profile scoring seams.

### Force pitch card

The engine emits Force pitch actions as:

```text
CAST(card=ForceOfWill, payment=pitch, pitch_card=...)
```

The public profile scorer was checking `pitch`, so pitch-card penalties were sometimes falling through to the default. The scorer now checks:

```python
action.params.get("pitch_card", action.params.get("pitch", ""))
```

### Blocking

The engine emits block actions as:

```text
BLOCK(block_player_attackers=..., block_jace_attackers=...)
```

The public profile scorer was checking `block_player` / `block_jace`. It now supports the engine names and keeps the legacy fallback.

These were not legality bugs. They were evaluation-policy bugs. The engine would still apply legal actions correctly, but public baseline policies could make distorted choices.

## Strategy-set refactor

rev0013 had the code-policy payoff population defined inside a script. rev0014 adds:

```text
src/muc5/strategy_sets.py
```

so payoff scripts, statistical gates, and future population tools share the same bundle definitions.

## New audit checks

`scripts/audit_cube.py` now checks:

```text
rev0014 statgate outputs exist and pass live audit
LCB standings are sorted by lower confidence bound
static MAP-Elites archive exists and has nontrivial cells
public-agent Force/block parameter fix is live
required rev0014 files exist
```
