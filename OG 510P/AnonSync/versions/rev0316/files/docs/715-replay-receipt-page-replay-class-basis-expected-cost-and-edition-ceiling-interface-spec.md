# Replay receipt page: replay class, basis, expected cost, and edition ceiling interface spec

## Purpose

Preserve the replay truth that was actually in force when a policy was applied or a heavy mutation was reviewed.

The receipt answers:

> what replay class did the product claim, on what basis, with what full-resend ceiling, and what stronger class was unavailable at the time?

## Receipt fields

Every replay receipt must preserve at least:

1. subject or policy target
2. current replay class
3. strongest available class at commit time
4. strongest unavailable class and why unavailable
5. current fallback / full-resend ceiling
6. evidence strength
7. hash/piece-map availability snapshot
8. network-cost tendency
9. local-CPU/disk-cost tendency
10. review origin (`policy change`, `subject review`, `profile import`, `mutation review`)
11. strongest safe sentence used in UI
12. timestamp and actor

## Example safe sentences

- `At commit time this subject used piecewise replay, but piece-shifting edits could still force full resend.`
- `At commit time this profile intentionally preferred full resend over local differential recheck.`
- `At commit time stronger diff-delta replay was unavailable on this seat/tier.`

## Required comparisons

A receipt must let the operator compare later against:

- current replay class now
- replay class at receipt time
- what basis changed since then
- whether a stronger class later became available

## Data model

- `replay_receipt_id`
- `target_id`
- `target_kind`
- `recorded_replay_class`
- `best_available_class`
- `unavailable_stronger_class`
- `unavailable_reason[]`
- `fallback_ceiling`
- `evidence_strength`
- `hash_snapshot`
- `piece_map_snapshot`
- `network_cost_tendency`
- `local_cost_tendency`
- `safe_sentence`
- `origin`
- `actor_ref`
- `recorded_at`

## Failure this page prevents

Without this receipt, operators later only remember `we turned on delta` or `this was incremental`, and lose the more honest record that the system still had a shift-triggered full-resend ceiling or an edition gate.

AnonSync should keep replay-class truth durable enough to survive later folklore.
