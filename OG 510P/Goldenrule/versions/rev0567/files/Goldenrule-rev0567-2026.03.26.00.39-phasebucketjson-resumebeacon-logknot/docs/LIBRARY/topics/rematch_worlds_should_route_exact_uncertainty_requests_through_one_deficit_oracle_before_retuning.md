# Rematch worlds should route exact uncertainty requests through one deficit oracle before retuning

## Claim
Future inheritors should route compact repeat-sidecar exact uncertainty requests through **one executable deficit oracle** before they start retuning.
The oracle should do three things in one pass:
- prune the live dwell support from the required worst-case preserved-gain floor,
- reject target dwell values that fall outside that live support,
- and then expose the remaining cap, checkpoint, slack, and width deficits for each floor-eligible exact tier.

## Why this matters
The archive already had all of the ingredients needed to answer an exact request bundle, but they were spread across separate cards:
- the guarantee threshold selector,
- the dwell coverage topology,
- the repair guide,
- the post-amortization selector,
- and the new floor-conditioned dwell-support ladder.

That is enough for a careful human, but it is still too easy for a future session to merge them in the wrong order.
The most common waste pattern is to argue about cap or slack first when the real blocker is earlier:
- the required floor already prunes the dwell suffix,
- the requested dwell already sits in a dead zone,
- or the request is already above the current exact frontier.

The new oracle makes the correct order explicit:
1. check the required floor,
2. derive the live dwell support,
3. screen the target dwell against that support,
4. then inspect tier-specific budget and tolerance deficits.

That means the archive can now answer one request bundle deterministically instead of forcing future inheritors to manually cross-reference several reports.

## Implementor rule
- Run the request through the executable uncertainty oracle before manual retuning.
- Treat required floor as the first pruning step, not as one budget among several.
- If the target dwell is outside the floor-conditioned live support, repair dwell or weaken the floor before discussing cap or slack.
- When no exact tier is feasible, inspect the tier deficit rows rather than improvising a new failure theory.
- Use the strongest feasible exact tier returned by the oracle unless a separate program-level reason prefers a weaker lane.

## Pointers
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle.py`
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle.py`
