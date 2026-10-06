# Priority-0 role-blind replay and external-replay handoff — 2026-06-15

## Decision

`rev0364` spends the `OQ-0255` frontier on a role-blind-by-file replay slice rather than another argument for self-sufficiency testing. The revision adds a separated responder packet, scorer key, manifest scorecard, and checker:

- `assays/priority-zero-role-blind-responder-packet-2026-06-15.json`
- `assays/priority-zero-role-blind-scorer-key-2026-06-15.json`
- `assays/priority-zero-role-blind-replay-2026-06-15.json`
- `tools/check_priority_zero_role_blind_replay_contract.py`

This closes `OQ-0255` only in the narrow sense that the archive now has a checked role-blind replay object and scorecard. It does **not** close the stronger independence problem. `OQ-0256` is opened for an external or operator-independent replay using the responder packet without the scorer key.

## Result

| Labeled packet | True variant revealed only in scorer key | Score | Operator cost | Interpretation |
| --- | --- | ---: | ---: | --- |
| `packet-charlie` | no archive | 2 / 18 | 1 min | Correct behavior is abstention from archive-specific claims. |
| `packet-alpha` | sham/decoy core | 4 / 18 | 5 min | Fluent false continuity must be rejected or abstained from. |
| `packet-delta` | full archive | 16 / 18 | 23 min | Recovers exact trace, but the cost penalty prevents it from becoming default reentry burden. |
| `packet-bravo` | compact hot cue | 17 / 18 | 9 min | Recovers mission/routing, rejects decoys, preserves escalation triggers, and wins on cost. |

The compact cue therefore passes this file-separated role-blind slice. The scorecard is stronger than the earlier same-session unblinded statement because the responder packet excludes the answer key, expected scores, and variant map. It is still weaker than independent evidence because the same session created the packet/key pair and the archive publicly contains both.

## How to run the next replay

A future operator should hand **only** `assays/priority-zero-role-blind-responder-packet-2026-06-15.json` to the responder. The responder should answer each labeled packet before seeing the scorer key. Only then should the scorer open `assays/priority-zero-role-blind-scorer-key-2026-06-15.json` and apply the metric table.

Failure conditions are concrete:

- the responder sees the scorer key before answering;
- no-archive receives a confident DelayBasin-specific answer;
- the sham packet is accepted as canon;
- compact loses mission heart or `OQ` routing;
- full archive gains more than two net points after operator cost;
- the result is cited as deletion, minimality, benchmark, or independent-certification authority.

## Substance over doctrine

The important move is not a new registry class. The important move is that the next replay now has a small separable packet that can be handed to another model or human without including the answer key. This should reduce the chance that the archive scores its own expectations while pretending it has tested continuation.

## Relationship to the earlier smoke slices

The rev0361 smoke slice proved that a minimal support core could recover the live mission/routing better than no-archive or sham controls. The rev0363 rotated slice moved decisive cues away from privileged positions and kept the compact cue competitive with the full archive. This rev0364 role-blind slice adds file separation: the answer key and scorecard are not part of the responder packet.

## Non-claims

This is not deletion authority, not a review court, not a minimality proof, not a standing benchmark, not full self-sufficiency certification, and not independent operator evidence. It is a checked handoff object plus a same-session role-blind-by-file scorecard.

## Next live risk

`OQ-0256` should run an external or operator-independent replay of the responder packet. If compact fails there, the hot-cue burden gate must narrow or reverse. If compact passes, the archive may cautiously strengthen the compact default while keeping full-archive escalation triggers public.
