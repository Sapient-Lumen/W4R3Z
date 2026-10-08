
## rev0192 — Tap Cost Payment Receipt Spine

Refactored the nonmana receipt audit probe from discard-only rev0191 coverage to a tap/discard paid-action spine. The probe now requires `TapCostPaymentRecord`, `tap_payment_*` journal fields, validator diagnostics for typed tap-cost payment receipt drift, focused C++ tamper coverage, and this doc/ledger surface. This keeps the pass executable: tap-as-cost can be challenged through declaration, placement, transaction, journal export, and validation instead of being inferred from a plain `tap` log row.

## rev0190 — nonmana receipt transaction spine

Audited the paid-action body for the user's requested failure mode: useful work getting lost in doctrine/registry bureaucracy while the risky execution spine remains incomplete. The concrete waste was semantic indirection: sacrifice-cost payment receipt proof existed on stack-placement/cost witness surfaces, but the paid-action declaration and terminal transaction did not carry the exact typed sacrifice-cost payment receipt.

This revision promotes the receipt into `PaidActionDeclarationRecord.v2`, `PaidActionTransactionRecord.v6`, and `PaidActionTransactionJournal.v4`. Validation now rejects placement/declaration/transaction/payment-row drift and rejects rollback rows that pretend to contain committed sacrifice-payment evidence.

The next correction over time is a reusable nonmana cost-plan transaction, not more prose: choices, alternative/additional costs, tap/sacrifice/discard/life/counter payments, replacement/prevention interposition, rollback, and final commit should share one ordered proof surface.

---

## rev0170 — paid journal bundle artifact trust

Audited the replay bundle / paid-action transaction boundary after rev0169. The wasteful failure mode was not another missing registry row; it was an omission risk: replay artifacts could prove the final StateCore while paid-action cost/payment receipts remained a separate optional journal.

rev0170 promotes that seam to `ReplayArtifactManifest.v3` with an explicit paid-action journal attachment contract. Attached manifests require `PaidActionTransactionJournal.v3` text, bind the journal's text hash, record count, final-state hash, journal hash, and payload hash into the manifest, and fail old three-file verification with `PaidActionJournalMissing` rather than silently ignoring the attachment requirement.

The refactor is carried through source, tests, CLI, CMake, rules ledger, README, changelog, and this datacube audit. The new executable anchors are `test_replay_artifact_manifest_binds_paid_action_transaction_journal` and `mtgsim_cli_paid_replay_bundle_roundtrip`. This is artifact trust work: it makes paid-action evidence harder to omit from a replayed claim.

---

# rev0157 roadmap delta — mission trust triage

The active mission is **trusted transitions**: one authoritative state plus one explicit legal choice should produce one deterministic next state and enough typed evidence to validate, replay, branch, fuzz, search, and explain the transition.

The next code-bearing change should introduce a typed declaration / cost-plan seam rather than another field-only witness. Start with a vertical paid-cast transaction: declaration (`ChoiceDeclarationRecord`), total-cost lock, mana production, mana payment, nonmana costs, stack placement, rollback proof, and one causal receipt only after success.

Correct over time: regenerate generic `latest` reports from the staged root, refresh the rules ledger/manifest against the current official rules source, split monoliths only at proven seams, and make coverage-guided fuzzing / semantic counterexample shrinking a separate evidence class from randomized legal walks.

See `docs/architecture/mission_trust_triage_rev0157.md` for the deep-read triage.

## rev0156 — mode contract hash witness

Audited the last asymmetric edge in the rev0153–rev0155 choice-anchor spine. Target choice anchors proved exact ordered target vectors, but mode choice anchors still proved only `choice_mode_index`.

The refactor adds `EventRecord::choice_mode_contract_hash` and public `mode_choice_contract_hash(...)`, populates the hash when paid modal casts emit `choose_mode`, and seals the payload through `hash_into(EventRecord)`. Validation now rejects missing or mismatched selected-mode contract hashes, and `test_mode_choice_anchor_hashes_selected_mode_contract` guards the seam.

## rev0155 — target set hash witness

Audited the multi-target branch of the choice-lock receipt. rev0154 sealed the choice payload fields into `journal_hash(...)`, but a multi-target `choose_target` row still only carried `choice_target_count`; the exact ordered target vector lived on `StackPlacementRecord::chosen_targets` without a matching EventRecord payload.

This slice adds `EventRecord::choice_target_set_hash`, computes it from stamped targets through `target_choice_set_hash(...)`, validates it against `StackPlacementRecord::chosen_targets`, and adds `test_multi_target_choice_anchor_hashes_ordered_target_set`. The deeper next seam is a typed `ChoiceDeclarationRecord` rather than continuing to grow EventRecord one field at a time.

---

## rev0154 — choice anchor hash seal

Audited the newly split rev0153 choice payload anchors against the Journal hash boundary. Validation already rejected drift in `EventRecord::choice_mode_index`, `EventRecord::choice_target_count`, `StackPlacementRecord::mode_choice_event_sequence`, and `StackPlacementRecord::target_choice_event_sequence`, but those fields were absent from `hash_into(...)`, so journal tampering could remain hash-identical while still being semantically invalid.

This slice adds the missing hash inputs, a focused `journal_hash(...)` mutation regression, and a datacube probe that keeps the hash contract wired across source, tests, docs, rules ledger, README, changelog, and artifact report. The next deeper seam is a typed `ChoiceDeclarationRecord` that hashes the entire pre-payment declaration surface instead of extending `EventRecord` field-by-field.

---

## rev0153 — choice payload anchors

Audited the remaining ambiguity inside the rev0152 choice-lock receipts: a placement record named the generic choice span, but consumers still had to infer which choice row carried the mode payload and which carried the target payload.

The refactor adds `EventRecord::choice_mode_index`, `EventRecord::choice_target_count`, `StackPlacementRecord::mode_choice_event_sequence`, and `StackPlacementRecord::target_choice_event_sequence`. `seal_choice_lock_witness(...)` now seals split anchors, and validation rejects missing anchors, wrong-kind anchors, stale anchors outside the lock window, mode-index drift, target-count drift, and single-target payload drift. The focused regression extends `test_paid_action_choice_lock_receipts_record_mode_and_target_events`, and the datacube audit probes the new field surface across source, tests, docs, ledger, README, and changelog.

## rev0152 — choice lock receipts

Audited the paid-action spine after rev0151. Stack-entry and cost-payment witnesses were strong, but mode/target choice rows were still found by implication: the final stack-placement record knew choices were locked before payment, yet did not name the exact `choose_mode` / `choose_target` events that formed the lock.

This slice adds `first_choice_event_sequence`, `last_choice_event_sequence`, and `choice_event_count` to `StackPlacementRecord`, seals them through `seal_choice_lock_witness`, and validates object/controller/count consistency across the named span. The refactor also routes choice logs through linked event rows so mode and target choices are durable, queryable evidence instead of prose between stack entry and payment.

The next deeper seam is a typed choice declaration record that unifies modes, targets, X, alternative/additional costs, divisions, and optional decisions before any cost mutation occurs.

---

## rev0151 — sacrifice cost witness receipts

Audited the paid-action cost spine after rev0150. Mana plans, mana changes, tap costs, and loyalty counters now had named witnesses, but sacrifice costs still relied on the broader paid-action zone-change span. This slice adds exact `first_sacrifice_cost_zone_change_record_index` / `sacrifice_cost_zone_change_record_count` fields plus `sacrifice_cost_event_sequence`, sealed through `seal_sacrifice_cost_witness`.

The refactor keeps the generic span for broad ordering, while giving agents and validators a local receipt for the actual sacrifice payment. The package audit also compacted oversized validation histories and SQLite metrics payloads into trend rows, preserving full details in named reports while removing cache/history payload warnings. The next deeper seam is a unified nonmana cost plan record covering tap, sacrifice, discard, life, counters, and rollback reasons under one cost kernel.

---

## rev0149 — paid action phase receipts

Audited the seam named by rev0148: paid casts and activations had strong adjacent evidence, but the paid phase itself was still implicit. The refactor adds paid action phase receipts to `StackPlacementRecord`, centralizes the engine path through `seal_paid_action_phase`, and gives validation direct diagnostics for missing or inconsistent phase evidence.

The strongest practical change is that “stack object exists before costs” and “mode/target choices are locked before payment” are now explicit record booleans backed by event sequences and typed ranges. The next audit target is a broader cost-plan kernel that includes all nonmana costs, rollback reason, and a single receipt boundary.

---

## rev0147 — tap event zone snapshot

Audited the bridge between automatic payment-plan tap witnesses and plain tap EventRecord rows. rev0144 anchored tap rows by object/player, but the witness still did not prove the same object zone-change incarnation as the planned mana step. This slice adds `EventRecord::object_zone_change_index`, fills it from `tap_object(...)`, hashes it, validates missing tap-row snapshots with `event_record.tap_log_missing_object_zone_index`, and validates automatic payment witnesses with `mana_payment_plan_record.tap_event_witness_zone_index_mismatch`.

The full typed tap/untap record family remains the deeper future refactor; rev0147 keeps the current bridge honest by making tap event identity match the zone-change precision already carried by `ManaPaymentPlanStepRecord`.


## rev0146 — Mana Payment Locked Step Guard

Audited the payer-scoped payment plan after rev0145 for contradictions inside the readable plan row. The live planner already excludes locked tap sources, but the validator did not reject a durable `ManaPaymentPlanRecord` that listed a source in `locked_tap_sources` and then reused the same object/zone snapshot as a tap-cost `ManaPaymentPlanStepRecord`.

rev0146 adds `mana_payment_plan_record.locked_source_used_as_tap_step` and a focused corruption regression that repairs the plan hash after mutating the lock entry, proving the new failure is about lock/step consistency rather than hash drift. The new audit probe checks the validator code, regression, architecture note, ledger, README, and changelog wiring.

## rev0145 — Mana Payment Payer Hash Scope

Audited the automatic mana-payment hash domain after rev0144. The plan record identified the payer, but `plan_hash` sealed only cost, pool, locked sources, and planned steps. That let two different players with identical empty auto-payment plans share a seal.

The refactor advances the identity namespace to `MTGSim.ManaAutoPaymentPlan.v4`, hashes `PlayerId` into the plan identity, routes `mana_payment_plan_record_identity_hash(...)` through the payer-scoped helper, and adds `test_auto_payment_plan_hash_is_payer_scoped_for_empty_plans` to prove identical empty plans by different players produce distinct hashes. The validator now catches payer drift as an identity-hash mismatch, and the datacube audit probes this seam through source, tests, docs, rules ledger, README, and changelog.


## rev0144 — Tap Event Identity Anchor
This rev0144 tap event identity anchor keeps the slice narrow while preparing a future typed tap/untap record family.


Audited the tap-event witness left by rev0142/rev0143. Payment-plan steps could name a `tap_event_sequence`, but the underlying plain tap log row did not structurally identify the tapped object or tapping player.

The refactor routes `tap_object(...)` through `record_event_with_links(...)` so plain `tap` rows carry object/player anchors without introducing a full typed tap-record family. Validation now rejects unanchored tap log rows and requires automatic payment-plan tap witnesses to identify the planned mana source and payment player. The regression `test_tap_log_event_records_object_and_player_context` covers the generic tap row, while the payment-plan regression corrupts source/player anchors to prove `tap_event_witness_source_mismatch` and `tap_event_witness_player_mismatch` fire.

## rev0143 — Mana Payment Pool Span

This rev0143 pool-span witness slice audits automatic payment before/after mana-pool evidence.

Audited the readable automatic payment plan after rev0142. The plan named selected steps, tap witnesses, and produced mana rows, but it still did not preserve the floating mana context that made the plan sufficient. The refactor adds `pool_before_plan` and `pool_before_payment` to `ManaPaymentPlanRecord`, advances the plan identity namespace to `ManaAutoPaymentPlan.v3` by hashing the starting pool, and validates that `pool_before_plan + planned production == pool_before_payment == linked Paid ManaChangeRecord::pool_before`.


## rev0142 — Mana Payment Tap Witness

- Added `ManaPaymentPlanStepRecord::tap_event_sequence` so tap-cost automatic payment steps witness the ordered `tap` Event row; this tap-event witness pays the source tap before the produced mana row.
- Strengthened validation for missing, wrong-kind, out-of-order, post-production, post-payment, duplicate, and non-tap-step tap witnesses.
- Kept this as a bridge refactor rather than a full typed tap/untap record family; the next evidence expansion should promote tap status changes into their own structured journal record.

## rev0141 — mana payment producer backlink

Audited the rev0140 execution witness for directionality. Plan steps could point to the produced mana row, but the produced row itself did not identify its owning payment plan step.

The refactor adds `auto_payment_producer_plan_record_index` and `auto_payment_producer_plan_step_index` to `ManaChangeRecord`, fills them on automatic mana-production rows, includes them in stable hashing, and validates the two-way link against `ManaPaymentPlanStepRecord::produced_mana_change_record_index`. The new regression corrupts incomplete backlinks, invalid step links, and non-production backlink payloads, while the datacube audit now probes the bidirectional witness surface across code, docs, tests, ledger, and release notes.

## rev0140 — mana payment plan step witness

- Promoted readable automatic mana-payment steps from intent-only payloads into execution witnesses via `produced_mana_change_record_index`.
- Refactored `ManaAutoPaymentPlan.v2` hashing so the pre-execution identity seal excludes witness indexes while the full step record still participates in StateCore hashing.
- Strengthened validation around identity-hash drift and plan-step production witness links.

## rev0139 — mana payment plan record

Audited the evidence seam left by rev0138: `auto_payment_plan_hash` sealed the automatic mana-payment plan, but the selected plan body was still implicit. The refactor adds typed `ManaPaymentPlanRecord`, `ManaPaymentPlanStepRecord`, and `ManaPaymentPlanLockedSourceRecord` rows, links them through `EventRecordKind::ManaPaymentPlan`, and connects the final paid `ManaChangeRecord` back through `auto_payment_plan_record_index`.

The focused regression `test_auto_payment_plan_record_links_locked_sources_steps_and_paid_record` proves the readable plan exposes the selected Forest mana ability, source zone-change identity, produced mana, tap-cost flag, plan hash, and two-way paid-record link; validator probes reject broken plan hashes, stripped paid-record plan links, and broken typed event links.

## rev0138 — mana payment plan hash

Audited the count-only evidence left by rev0137. Automatic paid `ManaChangeRecord` rows could expose how many mana-ability steps were reserved and how many tap sources were locked, but not the identity of the locked-source set or the selected mana-ability steps.

The refactor adds `auto_payment_plan_hash` to `ManaChangeRecord`, includes it in stable StateCore hashing, computes it with `mana_payment_plan_hash(...)` before reserved mana abilities are activated, and validates that every automatic paid record carries a nonzero hash while manual/payment/production rows do not. The new regression `test_auto_payment_plan_hash_records_empty_plan_evidence` proves even an empty automatic plan records a stable hash, and the activation/attack lock regressions now assert nonempty plan hashes too. The datacube audit has a dedicated rev0138 probe across source, validation, tests, docs, ledger, README, and changelog.

## rev0137 — mana payment plan evidence

Audited the typed evidence gap left after the activation and attack tap-source lock slices. The helper-level lock behavior was correct, but the paid `ManaChangeRecord` did not itself say how many mana-ability plan steps were reserved or how many tap sources were locked out before planning.

The refactor adds `auto_payment_mana_ability_count` and `auto_payment_locked_tap_source_count` to `ManaChangeRecord`, includes them in stable hashing, records them from the locked-source auto-payment path, and validates that plan metadata appears only on automatic paid records. The existing activation and attack-cost regressions now assert that their successful external-source payments carry one plan step and one locked source. The datacube audit has a dedicated rev0137 probe across source, validation, tests, docs, ledger, README, and changelog.

## rev0136 — attack tap-cost lock

- Audited the combat attack-cost seam against the paid-action transaction spine. Nonvigilance attackers chosen for declaration are now locked out of the tap-mana planner for their own attack cost.
- Added `attack_declaration_locked_tap_sources(...)` and routed attack-cost preflight/payment through the existing locked-source mana planning path.
- Added `test_attack_cost_locks_nonvigilance_attackers_out_of_auto_mana_payment`, proving the self-funded nonvigilance attack-cost path is omitted/rejected without combat, tap, pool, stack, or declaration-window leakage, and succeeds with an external mana source.
- Added `audit_attack_tap_cost_lock_wiring(...)` and `docs/architecture/attack_tap_cost_lock_rev0136.md` so the seam remains connected across code, tests, docs, ledger, and release surfaces.

## rev0135 — attachment-safe sacrifice order

Audited the first semantic failure exposed by the rev0134 paid-action transaction spine: a deterministic sacrifice selector could find a payable set, then pay it in battlefield order and make a later selected attached Aura illegal by sacrificing the enchanted permanent first. The transaction prevented leakage, but the reducer still rejected a legal payment order.

The refactor adds `selected_attachment_depth(...)` and `order_sacrifice_cost_objects_for_payment(...)`, then routes `pay_selected_sacrifice_cost(...)` through the ordered selection after validating the chosen set. The focused regression `test_sacrifice_cost_orders_attached_permanents_before_enchanted_sources` proves an attached Aura is sacrificed explicitly before its enchanted creature, the spell reaches the stack, and the payment detail exposes the attachment-safe sacrifice order. The datacube audit now probes this seam through source, tests, docs, audit notes, ledger, README, and changelog.

## rev0134 — paid action transaction spine

Audited the inner paid-action body named by the rev0133 compass. The refactor adds `commit_paid_action_body_transaction(...)`, stages paid spell casts and activated-ability activation bodies on a copied `GameState`, and adopts only after all modeled phases succeed. It also locks activation tap-cost sources out of their own auto-mana payment plan, closing the concrete double-tap leak where one object could both fund and pay a tap-cost activation.

The focused regression `test_activated_ability_tap_cost_locks_source_before_auto_mana_payment` proves the failed self-funding activation leaves no synthetic stack object, stack placement, tapped source, or produced mana behind, and then proves success with an external mana source. The datacube audit now probes this seam through code, tests, docs, and the rules ledger.

## rev0125 — Transition checkpoint seal

Audited the transition-result boundary after the selected-action seal. `TransitionResult` now carries `StateCheckpointSeal checkpoint_before` and `StateCheckpointSeal checkpoint_after`, `capture_transition_before(...)` / `capture_transition_after(...)` derive their scalar fields from those seals, and `committed_with_atomic_adoption_guard()` requires `committed_with_checkpoint_seals()` before a staged state can be adopted. The refactor also removed the duplicate private action-receipt count helper and makes `transition_result_matches_receipt(...)` reject checkpoint-seal drift.

## rev0121 — Transition action journal seal

- Exposed the staged action-body journal sample on `TransitionResult` through `journal_hash_after_action` and `journal_entries_after_action`.
- Strengthened `transition_receipt_matches_result(...)` so the causal receipt's post-action journal hash/count must match the immediate transition result before adoption.
- Added `has_post_action_journal_seal()` and `committed_with_action_journal_seal()`; the atomic adoption guard now includes the post-action journal seal.
- Added `test_commit_action_transition_carries_post_action_journal_seal` and datacube audit probes for the new seal.
- Remaining refactor target: push this transaction boundary inside paid casting and activated ability cost/payment phases, not only around the top-level LegalAction mutation.

## rev0119 — transition staged commit audit/refactor

Audited the new `TransitionResult` seam for the next failure mode after proof carrying: successful preflight followed by partial mutation before a failed commit. The refactor introduces shared `ActionTransitionPreflight` / `preflight_action_transition(...)`, makes `commit_action_transition(...)` mutate a staged `GameState` copy, appends the causal receipt to that staged state, and adopts with `game = std::move(staged_game)` only after success. `TransitionResult` now exposes staged commit sentinels and `committed_with_staged_adoption()`.

## rev0118 — transition choice-proof spine audit/refactor

Audited the public `TransitionResult` seam after rev0117. The result could name a causal receipt, but the selected-choice page proof and APNAP queue proof still mostly lived on the receipt. The refactor carries `LegalActionPageLocation`, `ChoiceQueueLocation`, checked/found sentinels, and `committed_with_choice_proofs()` directly on committed transition results, while preflight rejections keep those proof sentinels false and nonmutating. The datacube audit now has a transition-result wiring probe across types, engine code, tests, docs, and ledger.

## rev0117 — transition result spine audit/refactor

Audited the action boundary against the rev0116 mission-spine finding that MTGSim needed an explicit reducer result rather than only side-effecting boolean helpers. The refactor adds `TransitionStatus` / `TransitionResult`, `pending_transition_for_player(...)`, and `commit_action_transition(...)`; factors the LegalAction mutation switch into `apply_legal_action_mutation(...)`; and proves pure NeedChoice inspection, nonmutating rejection, and single-receipt commit with focused C++ regressions. Legacy `apply_action(...)` intentionally keeps illegal-attempt receipts for full-trace audit compatibility.


## rev0030 audit/refactor slice — copied-definition projection

The audit now probes copy wiring across C++ types/APIs, engine projection helpers, validation, scenario DSL, CMake smoke tests, card DB sample rows, rule modules, and metadata-only ledger rows. The refactor target was the stale assumption that an object's `definition_index` is always its current characteristic source.

## rev0031 — timestamp ordering audit

Audited/refactored the continuous-effect projection path so narrow static-source and generated continuous effects no longer rely on category order. New timestamp metadata and validation make the projection path more refactorable for future dependency and simultaneous-timestamp work.

## rev0034 — trigger LKI and target-choice audit

Audited the trigger scaffold for the riskiest false confidence: pending triggers previously carried only payload metadata and targeted triggers had no target-choice path. The refactor added source snapshots, self-dies pre-move capture, deterministic target choice, and audit probes that watch those seams directly.


## rev0035 — zone-change replacement audit

Audited the prevention/replacement scaffold for the riskiest false boundary: replacement effects previously existed only around damage and destroy/regeneration, so battlefield-to-graveyard movement still became a dies event before any replacement hook could intervene. The refactor added `ZoneChangeReplacementDefinition`, a `move_object(...)` pre-finalization hook, scenario syntax, validation, focused C++/scenario tests, and audit probes across docs, ledger, CMake, and parser wiring.

## rev0062 — mana-pool mutation audit/refactor

rev0062 promotes mana production, payment, auto-payment, and pool clearing into `ManaChangeRecord` data stored in `GameState::mana_change_records` and linked by `EventRecordKind::ManaChange`. The validator now checks before/after pool deltas, colored/colorless payment satisfaction, source identity for mana abilities, and one-to-one event linkage.


## rev0074 risk-seam fuzz audit/refactor

The fuzz runner previously exposed `trigger_stack_actions` and `loyalty_actions` counters without ensuring the fixture could reliably generate either action. rev0074 adds a `risk-seams` profile, a binary-level `--require-risk-seams` failure mode, and runner-level aggregate reporting so zero-coverage regressions fail early instead of appearing as harmless low counters.

## rev0079 — Replay resume probe

Focused on the riskiest remaining replay-artifact gap: prefix localization was helpful but still left debugging rooted at the original snapshot. The new resume probe writes a fresh snapshot at the longest known-good prefix and a suffix bundle so the suspect action is first. This is intentionally practical infrastructure, not a new registry layer.

## rev0124 — transition selected-action seal

Audited the transition-result handoff for the last caller-owned selected-action dependency after rev0123. `TransitionResult` now carries the canonical selected `LegalAction`, `commit_action_transition(...)` strips labels and normalizes targets before hashing/staging/receipt append, and `transition_result_matches_receipt(...)` lets external audit/replay consumers verify the returned result against its causal `ActionReceiptRecord` without retaining the caller's original action object.

## rev0132 — transition trace-entry seal

rev0132 audits the small handoff between a committed `TransitionResult` and the replay-facing `ActionTraceEntry` row it projects. rev0131 removed duplicate trace-entry hashing, but the result still required callers to recompute `transition_result_trace_entry_hash(...)` to know which replay row was being certified.

This cut adds `kActionTraceEntrySchemaVersion`, `action_trace_entry_schema_version`, `action_trace_entry_hash`, and `has_action_trace_entry_seal()` to `TransitionResult`. `commit_action_transition(...)` computes the carried seal before trace handoff and boundary sealing; `check_transition_result_boundary(...)` now reports `TraceEntrySealMissing` and `TraceEntrySealMismatch` with expected/observed trace-entry schema/hash echoes. The result is a first-class replay projection seal that fails before broader handoff or receipt/result diagnostics.

## rev0150 — paid action cost witness receipts

Audited the first seam left by rev0149's paid-action phase receipts: the phase named the cost window, but not every nonmana payment witness was first-class on the stack-placement receipt. Tap-cost activation payment still required an event scan, and loyalty counter payment was only implied by the event span.

The refactor adds `tap_cost_event_sequence` plus a paid-action counter-change range to `StackPlacementRecord`. Validation now rejects missing/wrong tap witnesses by source zone-change snapshot and missing/non-loyalty counter ranges for paid loyalty costs. The new audit probe keeps the field-level wiring connected across source, tests, docs, ledger, README, and changelog.

## rev0167 — journalpayloadseal

Audited the paid-action journal parser/verifier boundary. rev0167 emits `MTGSim.PaidActionTransactionJournal.v2`, adds a header-level `record_payload_hash`, and makes parsing fail closed for unknown fields and blank lines. The verifier now rejects a valid row spliced from another journal when the header payload seal is stale.

## rev0168 — journal sequence guard

Audited the external paid-action journal boundary after rev0167. The concrete gap was release-surface, not doctrine: CTest wrote a paid-action journal artifact but did not run the CLI roundtrip/verifier as part of the release suite, and the v2 payload seal did not yet express first/last causal row sequence bounds.

The refactor bumps new exports to `MTGSim.PaidActionTransactionJournal.v3`, adds first/last transaction sequence header fields, makes verification fail closed on older schemas, rejects zero/non-increasing rows, and wires `mtgsim_cli_paid_action_journal_roundtrip` into CTest. The targeted regression rejects sequence tampering, stale header bounds, schema downgrades, unknown fields, blank lines, stale state bindings, and row splicing.

## rev0172 — pending trigger order choice

Audited and refactored the pending-trigger placement path so the selected APNAP-respecting `TriggerRecord` order is first-class action, receipt, and trace evidence instead of an implicit engine sort. Validation now detects duplicate/invalid trigger-order receipts and stack-order mismatches.

## rev0175 simultaneous SBA look-back batch

rev0175 fixes a simultaneous SBA/LKI hazard in the existing dies-trigger seam. `apply_state_based_actions(...)` now captures one pre-batch battlefield trigger-source snapshot before moving/destroying creatures for nonpositive-toughness or lethal-damage SBAs, then passes that snapshot through `move_object_with_precomputed_ltb_snapshots(...)` for every creature in the batch.

The important behavioral guarantee is narrow but substantive: when two creatures with creature-dies triggers die in the same SBA pass, each source can still see the other death even if one source has already been moved by the internal sequential movement loop. The public movement API remains stable; the new helper is internal evidence plumbing for simultaneous-batch callers, with the `pre_creature_sba_ltb_snapshots` variable naming the one shared pre-SBA snapshot.

This does not yet create a full event-batch record, nor does it cover every possible zone-change trigger form. It removes the highest-risk local bug: cross-dies trigger discovery no longer depends on the order in which the engine records simultaneous creature movements.

## rev0176 damageability gate

rev0176 fixes a concrete damage receipt bug: a plain artifact or other non-battle/non-creature/non-planeswalker battlefield object could previously receive a `DamageRecord` with positive `dealt` even though the engine had no legal damage result for that object type.

The refactor adds `DamageRecord::not_dealt`, `DamageRecord::target_was_damageable`, and `DamageRecord::damage_disallowed_by_target_type`. `deal_damage_to_target(...)` now gates object targets before applying protection/prevention; impossible target-type damage records all requested damage as `not_dealt`, leaves prevention shields unchanged, and produces no lifelink or deathtouch result. Validation rejects both accounting drift and old-style impossible object damage receipts.

## rev0177 damage counter-result links

rev0177 binds `DamageRecord::counters_removed` to the exact `CounterChangeRecord` range produced by planeswalker loyalty or battle defense damage. The validation path now rejects missing ranges, wrong source/object/kind, non-damage-result counter rows, and amount drift, so damage-to-counter results are challengeable without parsing event strings or trusting an aggregate field.

## rev0183 — zone replacement chain seal

Audited the current zone-change replacement seam after the prevention/paid/fuzz hardening. The concrete risk was not missing doctrine; it was an endpoint-only validator that could accept malformed replacement chains whose second pass did not consume the first pass result, whose pass order drifted, or whose replacement row backlink named a movement that did not actually own the row.

The refactor keeps scope narrow and executable: `ZoneChangeRecord` validation now proves contiguous replacement-chain continuity, pass-index order, affected-player consistency, duplicate source/definition/LKI rejection, and backlink range ownership. The existing chain regression now corrupts each of those fields so future refactors fail closed.


## rev0185 — SBA pass barrier

Audit/refactor focus: hidden Aura cleanup inside zone-change link clearing was too eager. Rev0185 makes `apply_state_based_actions` collect candidates at the pass boundary, adds `StateBasedActionRecord.check_index` alongside `pass_index` and `pass_candidate_count`, and validates pass monotonicity only within one SBA check. The cloudtainer fuzz run caught and corrected the first over-strict validator that treated pass indexes as globally monotonic across later priority checks.


## rev0191 audit/refactor note — discard-cost payment receipt

Refactored the datacube wiring probe from the rev0190 sacrifice-only transaction receipt to the new discard-cost payment receipt path. The audit now requires `PaidActionTransactionJournal.v6`, `DiscardCostPaymentRecord`, discard payment range/hash fields, validator diagnostics for declaration/transaction/payment drift, focused C++ tamper tests, and this ledger/doc surface. This keeps the audit useful as a guardrail over executable semantics instead of adding another passive registry.

## rev0193 — Life Cost Receipt Spine

Refactored the datacube wiring probe from the rev0192 tap-cost receipt path to the new life-cost payment receipt path. The audit now requires `LifeCostPaymentRecord`, `PaidActionTransactionJournal.v7`, life payment range/hash fields, validator diagnostics for declaration/transaction/payment drift, focused C++ tamper coverage, and scenario DSL support for `life_cost=` / `:life=N`. This keeps the pass code-first: paying life as a locked cost is now distinguishable from damage or ordinary effect-driven life loss.

## rev0194 — Loyalty Cost Receipt Spine

Refactored the datacube wiring probe from the rev0193 life-cost receipt path to the new loyalty-cost payment receipt path. The audit now requires `LoyaltyCostPaymentRecord`, `PaidActionTransactionJournal.v8`, loyalty payment range/hash fields, validator diagnostics for counter-change/event/transaction drift, and focused C++ tamper coverage. This is a risk-bearing semantic change: loyalty costs are no longer inferred from a generic paid-action counter-change span.

## rev0195 — Return Cost Receipt Gate

Refactored the datacube wiring probe from the rev0194 loyalty-cost receipt path to the new return-to-hand cost receipt path. The audit now requires `ReturnCostPaymentRecord`, `PaidActionTransactionJournal.v9`, return payment range/hash fields, validator diagnostics for zone-change/event/transaction drift, and focused C++ tamper coverage. This is a risk-bearing semantic change: return-to-hand costs are no longer inferred from generic battlefield-to-hand movement during a paid-action window.
