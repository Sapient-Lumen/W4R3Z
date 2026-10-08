# rev0011 Experiment Matrix Additions

## New axis: replay requirement

```text
none       quick smoke only
sampled    trace a small random subset
promoted   trace all games that affect champion/paper/theory claims
full       trace every game, expensive but best for audits
```

Current default:

```text
smoke/probes: full replay
bulk payoff: sampled or promoted later
```

## New axis: reward convention

```text
terminal_only
win_loss_draw_half_reported
win_loss_draw_half_training_optin
custom_shaped_diagnostic_only
```

Default recommendation:

```text
training: terminal_only
reporting: win_loss_draw_half_reported
```

## New axis: RNG isolation

```text
single_rng_legacy
agent_rng_plus_transition_rng
```

Default for replayable experiments:

```text
agent_rng_plus_transition_rng
```

## New strategy-bundle axis still pending

```text
constructor_method = enumerative | evolutionary | neural | hybrid | manual_seed
constructor_context = known_life_20 | known_life_40 | unknown_life | open_decklist | closed_decklist
mulligan_policy = fixed_rule | learned | evolved
pilot = random | heuristic | sparring_style | public_neural | search | cfr_like
```
