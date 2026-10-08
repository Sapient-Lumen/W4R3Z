# Zone-change replacement scaffold — rev0036

rev0036 turns the rev0035 one-shot zone-change replacement hook into a small replacement-event resolver. The supported domain is still intentionally narrow, but the important semantic jump is now present: after one replacement modifies a zone-change event, the engine rechecks the modified event for newly applicable replacements before the destination is finalized.

The executable target remains the high-risk battlefield movement family. A battlefield permanent may define `ZoneChangeReplacementDefinition` entries that watch one source zone, one requested destination zone, and one replacement destination zone for objects matching a static scope and type mask. `move_object(...)` asks the resolver for the final destination before it computes whether a creature died, so replacement chains can suppress or preserve dies triggers according to the final event.

## Data model

`ZoneChangeReplacementDefinition` lives on `CardDefinition` beside other local card-text scaffolds:

- `name`: audit-friendly replacement label;
- `scope`: source/self, controller/opponent, or all-creature/all-permanent style static scope;
- `from_zone`: the zone the object is moving from;
- `to_zone`: the requested destination this definition can replace;
- `replacement_zone`: the destination used instead;
- `affected_type_mask`: an optional type filter, defaulting to creatures;
- `choice_rank`: deterministic affected-controller choice hint used when more than one currently applicable replacement is available.

Scenario syntax exposes the same shape:

```text
replacement=NAME:SCOPE:FROM_ZONE:TO_ZONE:REPLACEMENT_ZONE[:TYPES][:choice=N]
```

For example:

```text
card exile_gate enchantment 0 0 replacement=to_exile_first:all_creatures:battlefield:graveyard:exile:creature:choice=2
card command_gate enchantment 0 0 replacement=exile_to_command:all_creatures:battlefield:exile:command:creature
```

The first definition can rewrite `battlefield -> graveyard` into `battlefield -> exile`. The second then becomes applicable to the modified event and can rewrite the final destination to command.

## Resolver seam

The engine now uses a repeated pre-finalization pipeline:

```text
requested move
  -> collect active battlefield replacement candidates for current destination
  -> choose one candidate using affected-controller deterministic choice rank
  -> record zone_change_replacement_choice when there was a real choice
  -> record zone_change_replaced
  -> mark that exact source/definition/zone-change-index as already applied
  -> recheck candidates against the modified destination
  -> finalize destination
  -> compute dies/enters trigger hooks from the finalized destination
  -> move object and run cleanup
```

Each individual replacement definition gets only one opportunity to apply to a given event or any modified version of that event. The resolver tracks source object id, replacement index, and source zone-change index to prevent accidental self-loops while still allowing a different replacement to become applicable after the destination changes.


## rev0046 structured zone-change record

`move_object(...)` now emits a `ZoneChangeRecord` beside the human-readable `move_object` event. The record is intentionally small and movement-focused: it stores the moved object, owner, previous and new controllers, source zone, `requested_zone`, finalized replacement destination, pre-move and post-move zone-change indexes, whether a replacement was applied, and whether the object was a battlefield creature before the event finalized. This gives future LKI, trigger, replacement, and replay code a typed seam without parsing audit strings.

The important distinction is requested versus finalized movement. A lethal creature event may be requested as `battlefield -> graveyard`, then replaced into exile or command before `move_object(...)` queues dies triggers. The structured record therefore preserves both the original request and the finalized replacement destination, while `creature_died` follows the finalized destination rather than the initial request.

Validation now checks that zone-change records have monotonic event sequences, valid object/player/zone references, and advancing zone-change indexes. The focused regression is `test_zone_change_record_preserves_requested_and_final_destination`, which corrupts a copied record to prove the validator catches stale/non-advancing movement metadata.

## Deterministic choice model

This is not a complete rule-616 choice engine. It does not yet pause for player input, batch simultaneous events, or implement the self-replacement/control/copy/back-face hierarchy. Instead, when multiple candidates apply to the current event, the affected object’s controller is recorded as the chooser and candidates are ordered by:

1. higher `choice_rank`;
2. source object id;
3. definition discovery order.

That gives scenario and C++ tests a reproducible way to model the affected controller choosing between replacements without introducing an interactive choice stack prematurely.

## Validation and audit

The invariant validator rejects replacement definitions with invalid scopes, invalid zones, invalid affected type masks, or inactive rewrites. The structural audit now probes the type definition, choice-rank field, repeated resolver helpers, scenario DSL, C++ tests, CMake scenario labels, this document, `prevention_and_replacement.md`, and the metadata-only rules ledger.

The harness audit/refactor in rev0036 also caps `auto` parallelism for build, C++ case, scenario, and fuzz runners through `MTGSIM_BUILD_AUTO_JOBS`/`MTGSIM_AUTO_JOBS` defaults of 8. This avoids cloudtainer fan-out spikes on hosts that report very large CPU counts.

## Tests

C++ coverage now includes:

- `test_zone_change_replacement_exiles_creature_instead_of_dying`;
- `test_zone_change_replacement_source_scope_only_replaces_itself`;
- `test_zone_change_replacement_rechecks_modified_event_and_choice_rank`;
- `test_zone_change_record_preserves_requested_and_final_destination`;
- `test_validation_catches_invalid_zone_change_replacement_definition`.

Scenario coverage now includes:

- `tests/scenarios/zone_replacement_dies_exile_no_trigger.mtgscn`;
- `tests/scenarios/zone_replacement_source_scope.mtgscn`;
- `tests/scenarios/zone_replacement_recheck_choice.mtgscn`.

The core new behavioral regression is that a creature whose `battlefield -> graveyard` move is first replaced by exile can then have that modified `battlefield -> exile` event replaced again before finalization. The resulting final zone drives dies-trigger detection.

## Known missing pieces

Missing: replacement effects from non-battlefield zones, self-replacement effects on spells, full affected-player/affected-object interactive choices, APNAP batching for simultaneous events, the rule-616 self/control/copy/back-face hierarchy, prevention/redirection of non-damage events, replacement effects that modify how permanents enter, simultaneous zone-change event batches, complete last-known-information records for all moved objects, delayed/relinked zone-change effects, and Oracle-text-derived replacement generation.

The immediate value is not breadth; it is that replacement is now represented as a repeated typed event resolver instead of a one-shot destination rewrite.


Audit keyword: rechecked replacement events are represented by repeated candidate collection before final movement finalization.

## rev0051 structured replacement applications

rev0051 promotes each applied zone-change replacement from a string-only `zone_change_replaced` event into a `ZoneChangeReplacementRecord`. The record captures the affected object, affected-player fallback chooser, replacement source/controller, source zone-change identity, the current event destination being rewritten as `event_to_zone`, the chosen `replacement_zone`, definition index, deterministic `choice_rank`, candidate_count, pass index, and the final `ZoneChangeRecord` it fed.

`ZoneChangeRecord` now carries `first_replacement_record_index` plus `replacement_record_count`, so a replay/audit consumer can start from the final movement and recover the exact replacement chain without parsing logs. This keeps the current deterministic `choice_rank` scaffold honest while preserving the missing rule-616 surface area: interactive affected-player choice, APNAP batching across simultaneous events, self-replacement priority, and richer prevention/replacement ordering are still roadmap rather than claimed complete.

Validation now rejects detached replacement records, impossible replacement ranges, mismatched first/final destinations, zero candidate_counts, stale source identity, and typed event records whose `EventRecordKind::ZoneReplacement` link does not reciprocate.

## rev0183 replacement-chain validation seal

rev0183 tightens the structured replacement application path around the rule-616 repeat loop. The generated rows already represented a repeated resolver, but validation previously checked mostly the first requested destination and final destination. Now each linked `ZoneChangeReplacementRecord` must form a contiguous chain: pass 1 consumes the movement's `requested_zone`, every later pass consumes the previous pass's `replacement_zone`, `pass_index` matches range order, the affected player matches the moved object's pre-move controller/owner, and the same source/definition/source-zone LKI cannot apply twice to the same event chain.

The standalone replacement-row validator also verifies ownership: a `ZoneChangeReplacementRecord` may not merely point at a `ZoneChangeRecord`; the movement must include that row inside its `first_replacement_record_index` / `replacement_record_count` range. This closes a row-splicing audit hole without widening the replacement-effect model.

## rev0184 priority-tier seal

rev0184 implements the first executable slice of the rule-616 priority hierarchy for the supported zone-change replacement scaffold. `ZoneChangeReplacementDefinition` now has a `ReplacementPriorityTier` (`SelfReplacement`, `ControlEntering`, `CopyEntering`, `BackFaceEntering`, or `General`). Candidate selection first filters to the earliest applicable tier, then applies the existing deterministic `choice_rank` fallback only within that eligible tier.

`ZoneChangeReplacementRecord` now stores `priority_tier`, `candidate_min_priority_tier`, and `eligible_candidate_count`. Validation rejects a row whose chosen tier is later than the minimum available tier, rejects zero eligible candidates, and rejects eligible counts greater than total candidates. `chosen_among_multiple` now means multiple eligible same-tier candidates, not merely multiple candidates across lower-priority tiers.

The regression `test_zone_change_replacement_priority_tier_forces_eligible_choice` proves a low-rank self-tier replacement beats a high-rank general replacement and that copied-state corruption is caught by `zone_replacement_record.priority_tier_skip`.
