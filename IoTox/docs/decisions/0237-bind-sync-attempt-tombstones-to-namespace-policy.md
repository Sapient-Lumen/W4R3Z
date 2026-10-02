# ADR 0237: Bind sync attempt tombstones to namespace policy

Status: accepted through the ADR 0235 direct-UDP and forced-TCP gates, 2026-08-29.

## Context

The sync subscriber retains terminal scheduler attempts for the lifetime of a pull. That bounded
history is what rejects late file events from a dead route incarnation instead of applying them to a
replacement. The subscriber originally fixed this bound at four records: enough for one committed
manifest, one initial range, and two replacement ranges.

Direct-UDP three-loss diagnostic `pair.fdskk7te` reached attempt six after two exact prefix
handoffs, then failed closed with `sync scheduler attempt tombstone bound is exhausted`. It retained
542,916 bytes exactly and reported zero discard and fallback. The fifth scheduler record needed for
the post-third-loss carrier could not be allocated even though the host-local namespace already
declared a larger bounded-request policy.

## Decision

- Set each pull's scheduler-attempt limit from its already validated host-local
  `maximum-outstanding-requests` namespace quota. The same quota already bounds the durable active
  attempt journal; no remote input may widen it.
- Keep every terminal attempt until the pull retires. Do not evict a fence merely to admit another
  carrier, because a delayed transport completion could then alias successor work.
- Expose `scheduler-attempts` and `scheduler-attempt-bound` in content-free `sync-status` output.
- Raise only `sync-file-range-triple-route-loss` from four to five outstanding requests. Five is the
  exact fixture requirement: one manifest attempt, one initial range attempt, and three replacement
  range attempts. Every other Sandwurm namespace retains four.
- Extend the owned subscriber boundary through three sequential carrier losses. The same exact
  prefix grows from 50% to 75% to 87.5%, reaches a fourth carrier under the fifth scheduler record,
  and completes with cumulative retained/resumed equality and every prior attempt still fenced.

## Consequences

The scheduler's fence-history budget is explicit, operator-bounded, and consistent with the
namespace's durable request budget instead of being a hidden lower constant. Exhaustion still fails
closed and never discards a tombstone or reuses an attempt identifier.

This change does not prove the three-loss gate by itself. ADR 0235's later direct-UDP
`pair.3iufekzy` and forced-TCP `pair.zleebk2k` proofs consume exactly five records and retain every
fence through completion. This decision does not permit unbounded retries, alter range framing,
increase concurrent route work, or make terminal attempt records durable across daemon restart.
