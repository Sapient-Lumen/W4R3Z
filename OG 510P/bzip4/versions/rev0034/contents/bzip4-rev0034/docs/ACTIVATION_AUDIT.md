# Activation planner audit

The activation planner is a pure, allocation-free contract used before any
future persistent scheduler dispatch.

## Floor semantics

A configured minimum is a true minimum, not a ceiling-derived target. Five
blocks with `minimum_blocks_per_active_lane = 4` permit one lane, not two.
Logical-byte grain follows the same rule.

## Executor availability

A background-only profile with zero retained background workers has no
executor. rev0021 returns an inactive plan instead of advertising an
unserviceable lane. A participating caller remains one available lane even when
no background worker exists.

## Overflow

Adding the caller lane to a retained-worker count can overflow `size_t` at the
synthetic maximum. rev0021 uses saturating availability semantics and tests the
maximum value with a two-lane policy cap.

## Wake accounting

`active_only` reports only productive background workers. `all_retained` is an
explicit experimental control and reports every retained background worker.
No scheduler or wake implementation is claimed in this revision; the planner
is the tested policy boundary on which that implementation can be rebuilt.
