# rev0024 learned mulligan results

The learned mulligan ranker was evaluated beside three deterministic policies:

```text
keep_always
land_band
land_band_business
mulligan_ranker_rev0024
```

Smoke results by same-shell policy summary:

```text
fjace_code:
  business  0.6146
  band      0.5833
  keep      0.5417
  learned   0.5208

overlord_threat:
  learned   0.4167
  business  0.3646
  band      0.3542
  keep      0.3542

wall_counter:
  learned   0.6458
  business  0.5833
  keep      0.5521
  band      0.4688
```

These are smoke-scale draw-half mean scores, not claim-ready metagame conclusions. The useful result is that mulligan policy has measurable shell-dependent effects and learned pregame policy can now be evaluated under the same gates as gameplay policies.
