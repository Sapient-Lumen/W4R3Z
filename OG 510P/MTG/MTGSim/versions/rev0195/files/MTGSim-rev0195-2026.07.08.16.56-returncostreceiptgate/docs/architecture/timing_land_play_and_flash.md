# Timing, land play, and flash through rev0022

rev0022 adds the first explicit spell-timing and land-play scaffold. The point of this slice is not to model every casting permission or every special action. The point is to remove a dangerous early shortcut: “a card can be paid for, therefore it can be cast.” Timing is now a separate legality seam that action enumeration, direct cast helpers, scenario fixtures, and validation can all exercise.

## Engine seams

- `can_cast_spell_now(game, player, object)` checks that the player has priority, the object is in that player’s hand, the object is not a land, and the card type/keyword allows the current timing window.
- Instants and cards with `AbilityFlash` use priority-based timing.
- Other nonland cards use `player_has_sorcery_speed_window`: active player, precombat or postcombat main phase, priority, and empty stack.
- `can_play_land(game, player, object)` is deliberately separate from casting. It checks priority, active player, main phase, empty stack, hand membership, land type, and remaining land plays.
- `play_land_from_hand(...)` moves the land directly to the battlefield, increments `lands_played_this_turn`, does not use the stack, and preserves priority.

## State and validation

`PlayerState` now stores `max_land_plays_per_turn` and `lands_played_this_turn`. The default maximum is one. `advance_step(...)` resets a player’s land-play count when that player becomes active for a new turn. Validation rejects impossible land-play counters where `lands_played_this_turn > max_land_plays_per_turn`.

The current model intentionally treats land-play counters as direct state fields rather than as continuous-effect-derived values. That makes the scaffold cheap to test now while leaving a future seam for effects that modify the number of lands a player can play.

## Action-space and ML impact

`ActionKind::PlayLand` means policies/search/ML code can distinguish a stack-free land special action from a spell cast. Legal-action enumeration now emits land-play actions only in legal land windows, and it never emits a cast action for land cards. Flash cards appear as cast actions in instant-speed windows; ordinary sorceries and creatures do not.

This matters for future simulations because “play land,” “cast instant,” and “cast sorcery-speed object” have different priority, stack, and search-branching consequences. Keeping them explicit also makes timing bugs easier to isolate with rule filters and scenario shards.

## Scenario fixtures

The scenario runner now supports:

- `main_phase PLAYER [main1|main2]` for compact sorcery-speed fixtures;
- `priority PLAYER STEP [ACTIVE_PLAYER]` for testing unusual priority windows;
- `action play_land PLAYER OBJECT`;
- `expect_land_plays PLAYER COUNT`.

The new fixtures are `timing_flash_in_combat.mtgscn`, `land_play_special_action.mtgscn`, and `land_play_resets_next_turn.mtgscn`.

## Audit/refactor slice

This revision audits and refactors the old single legality path for paid casts. The direct cast helpers, mode-aware cast helper, action enumerator, scenario runner, card catalog, rule-module registry, and rules ledger all now know about timing and land play. `tools/audit_datacube.py` has a dedicated `timing_land_wiring` probe to stop these seams from drifting apart.

## Known gaps

This is still a timing scaffold. It does not implement full special actions, permission/restriction layers, alternate timing permissions from continuous effects, flash granted by temporary effects, timing changes from real Oracle text, cast/play permissions from unusual zones, lands with spell-like alternate play rules, costs paid during land play, effects that change how many lands can be played beyond direct test-field mutation, or full rule-601 casting-order rollback.
## rev0056 priority-transition records

rev0056 turns the priority-pass response window into typed data. `PriorityTransitionRecord` entries in `GameState::priority_transition_records` now preserve the actor, active player, priority holder before and after the pass, step before and after, stack size and top object before and after, pending-trigger counts, and consecutive-pass snapshots.

The record outcome distinguishes `PriorityAdvanced`, `StackResolved`, `StepAdvanced`, `PendingTriggersPutOnStack`, and `NoAlivePlayers`. A pass that causes stack resolution records `StackResolved` and links to the produced `StackResolutionRecord`; empty-stack all-player passes record the step transition; pending triggered abilities gate ordinary priority passing and record that triggers were put on the stack instead. This gives response-window and agent-action consumers durable priority facts without scraping `pass_priority` strings.

