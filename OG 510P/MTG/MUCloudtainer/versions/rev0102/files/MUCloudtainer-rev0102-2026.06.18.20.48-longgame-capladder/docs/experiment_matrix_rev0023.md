# rev0023 experiment matrix additions

## MLP action-ranker smoke

Question:

```text
Does a tiny non-linear public action-ranker improve over the linear imitation ranker enough to justify more learned policy work?
```

Dimensions:

```text
policy family: MLP / linear / blended linear / public profile / code policy
life total: 20 / 40
starting player: 0 / 1
mulligan policy: strategy-bundle component
```

Required gates:

```text
promotion gate
statistical gate
public replay samples
batched C++ trace checks
```

## Mulligan policy gate

Question:

```text
How much does the mulligan policy move results when deck and pilot shell are held fixed?
```

Dimensions:

```text
shell: fjace_code / overlord_threat / wall_counter
mulligan policy: keep_always / land_band / land_band_business
life total: 20 / 40
starting player: 0 / 1
```

This is a precursor to learned mulligan agents.
