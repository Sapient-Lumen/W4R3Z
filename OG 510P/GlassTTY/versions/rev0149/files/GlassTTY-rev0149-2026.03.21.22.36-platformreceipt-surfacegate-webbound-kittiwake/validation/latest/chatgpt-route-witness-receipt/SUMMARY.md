# ChatGPT route witness receipt

- generated_at: `2026-03-21T22:05:01Z`
- minimum_required_fields: `host`
- recommended_field_count: `9`

## Quality tiers

- `strong` — 11-15 weighted points; suitable for durable handoff and proof continuation
- `usable` — 8-10 weighted points; acceptable for continuation when the branch decision stays in the baseline lane
- `sparse` — 4-7 weighted points; classification may be possible, but proof should pause for recapture
- `insufficient` — 0-3 weighted points; do not continue baseline proof

## Proof readiness

- `ready` — branch guard stays on continue and the witness quality is usable or strong
- `ready-with-caution` — branch guard stays on continue-with-caution and the witness quality is usable or strong
- `hold-for-recapture` — branch guard classified the shell, but the witness is too sparse for durable proof handoff
- `insufficient` — the witness is too thin to justify proof actions even if one cue looked promising
- `stop` — branch guard says the shell is a richer branch or otherwise outside the baseline lane
