# Rematch worlds should treat remaining half-step equiprobable transport headroom as tiny and localized

## Claim

Once the archive's normalized half-step transport trees are already certified as equiprobable-optimal **binary prefix** codes, the only remaining gains under an equiprobable source model are the exact residual gaps to entropy, and those gaps are now small enough to localize future effort:

- the exact `513`-word standalone shortest-script prefix has only `0.5558969935818823` total residual bits left over the equiprobable entropy bound, or `0.001083619870529985` bits per word on average,
- the exact `153`-state interval prefix and the inherited canonical-script prefix each still have `10.619660068024132` total residual bits, or `0.0694095429282623` bits per state on average,
- the state-known local exact-choice prefix still has `14.120249610575684` total residual bits over its full `513`-word represented catalog, or `0.027524853042057863` bits per word on average,
- and **all** positive state-known local-choice headroom is concentrated in the `15` interior singleton families (the `270` represented words with `18` shortest branches per state), where the residual gap is `14.120249610575684` total bits or `0.05229722077990994` bits per represented word.

The practical consequence is that future inheritors should stop chasing more elaborate equiprobable transports for the global exact-word prefix and the size-`2` local-choice families. Under the current assumptions, meaningful further gains can only come from:

1. changing the source model away from equiprobable,
2. changing side-information assumptions,
3. batching / cross-symbol coding beyond the current tree boundaries,
4. or targeting the interval-state / canonical-state regime and the size-`18` singleton choice families where nonzero residual headroom still exists.

## Why it matters

This is a tighter stopping rule than the earlier uniform-prefix optimality certificate.
The earlier result said that **tree reshaping** cannot help inside the equiprobable binary-prefix regime.
This new result says how much room is left even if the inheritor leaves the binary-prefix family but keeps the equiprobable source model:

- the global exact-word transport is already so close to entropy that it would take about `923` represented words, at the present mean gap, just to save one whole bit on average,
- the interval-state / canonical transport would need about `15` represented states to save one bit at the present mean gap,
- the full state-known local-choice regime would need about `37` represented words to save one bit at the present mean gap,
- and the interior-singleton local-choice subcatalog would need about `20` represented words to save one bit at the present mean gap.

So the archive now records not only that the current trees are optimal in their regime, but also where the remaining equiprobable headroom is too small to justify more machinery.

## Status

Validated by:

- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_equiprobable_entropy_headroom_law_snapshot_20260309.json`
