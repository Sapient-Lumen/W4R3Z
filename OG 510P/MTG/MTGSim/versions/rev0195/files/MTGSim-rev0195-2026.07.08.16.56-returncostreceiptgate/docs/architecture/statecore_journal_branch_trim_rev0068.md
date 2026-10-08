# rev0068 StateCore / Journal branch-trim seam

## Purpose

The riskiest waste in the cube was not another missing rule subcase. It was architectural: every copied `GameState` carried the whole forensic event and typed-record history. That made branch search, fuzz shrinking, agent rollouts, and speculative choices pay for old evidence that does not affect future legal transitions.

rev0068 adds the first executable split between:

- **StateCore**: facts needed to continue play.
- **Journal**: forensic evidence about how the current state was reached.

This is deliberately smaller than full replay. It gives the code something measurable and testable now, without inventing a registry or declaring serialization complete.

## New API seam

```cpp
std::uint64_t canonical_state_hash(const GameState& game) noexcept;
std::uint64_t journal_hash(const GameState& game) noexcept;
std::size_t journal_entry_count(const GameState& game) noexcept;
std::size_t journal_reserved_capacity_bytes(const GameState& game) noexcept;
void clear_journal(GameState& game) noexcept;
GameState make_branch_state(const GameState& source, JournalRetention retention = JournalRetention::ClearAll);
```

`canonical_state_hash` includes the current continuation: card definitions, objects, players and zones, stack, RNG state, turn/priority markers, pending triggers, prevention shields, and continuous effects.

It intentionally excludes the old event log and typed evidence vectors. It also excludes the raw `next_event_sequence` allocator; pending triggers keep the ordering data that matters for play.

`journal_hash` covers the forensic stream: human events, typed event records, trigger records, stack placement/resolution records, priority transitions, state-based action records, zone-change records, combat records, damage/prevention/life/mana/counter/discard/draw/mulligan records, and the `journal_trimmed` marker.

## The trim-safety bug that had to be fixed

A naive journal trim would clear `trigger_records` while leaving `pending_triggers` with stale `trigger_record_index` values. Setting those indexes to zero solved stale references but exposed a deeper issue: the pending trigger itself did not carry the event subject. The old `TriggerRecord` was the only structured place that knew what object caused the trigger.

rev0068 therefore adds these continuation fields to `PendingTrigger`:

```cpp
ObjectId subject{};
u64 subject_zone_change_index = 0;
```

This makes a pending trigger independently meaningful after its old journal anchor is dropped.

## Reconstruction behavior

When a trimmed branch later calls `put_pending_triggers_on_stack`, the engine sees a pending trigger with no valid record anchor, reconstructs a fresh branch-local `TriggerRecord`, records a new `TriggerQueued` event row, then records the normal `TriggerPutOnStack` row.

That preserves validation and typed event-spine consumers for the branch, while avoiding the memory cost of copying all prior evidence into every branch.

## Validation behavior

The validator still treats missing pending-trigger record links as errors in ordinary states. A missing link is allowed only when `GameState::journal_trimmed` is true. Pending trigger subject and subject zone-change snapshots are now validated directly.

## Regression coverage

- `test_canonical_state_hash_and_branch_journal_trim`
  - proves hash separation between StateCore and Journal,
  - proves journal vector capacity is released,
  - proves pure journal rows do not change the StateCore hash.

- `test_branch_trim_preserves_pending_trigger_reconstruction`
  - queues a trigger,
  - trims the branch journal to zero entries,
  - validates the trimmed branch,
  - puts the detached pending trigger on stack,
  - validates the reconstructed TriggerRecord linkage.

## Remaining work

This is not yet replay. The next step is a canonical checkpoint serializer and a reconstruction test:

```text
checkpoint(StateCore) + action/choice stream -> same canonical_state_hash
```

After that, the project should land `TransitionResult` and typed `ChoiceRequest`/APNAP scheduling, then move replacement/prevention into a generic propose/modify/commit event transaction.
