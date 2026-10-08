# rev0075 priority reconsideration

Highest-priority risk before this pass: rev0074 left four high-point fine strata that were correctly quarantined only because they were underpowered.  Those cells were at risk of becoming attractive folklore.

rev0075 reduced that risk by spending new games on the three unique size/life strata selected by the underpowered/high-mean rule.  After pooling, all three moved from `underpowered_min_games` to `quarantined_low_security_floor`.

Priority after rev0075:

1. **Do not promote `public_counter_guard`.** The strongest targeted strata still fail the conservative floor.
2. **Budget only one more targeted replication if needed:** `counter60_vs_threat40` at life 40, because its point floor is 0.6429 but its LCB is 0.3862.
3. **Prefer new adversarial columns over more volume.** More games can narrow confidence intervals, but a new threat policy may reveal a clearer strategic failure faster.
4. **Keep package discipline.** The rev0075 run generated 52,956 transition rows but shipped only a 360-row sample plus checksummed summaries; raw bulk stays out of the core.
