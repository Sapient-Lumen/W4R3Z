
## rev0192 — Tap Cost Payment Receipt Spine

Refactored the nonmana receipt audit probe from discard-only rev0191 coverage to a tap/discard paid-action spine. The probe now requires `TapCostPaymentRecord`, `tap_payment_*` journal fields, validator diagnostics for typed tap-cost payment receipt drift, focused C++ tamper coverage, and this doc/ledger surface. This keeps the pass executable: tap-as-cost can be challenged through declaration, placement, transaction, journal export, and validation instead of being inferred from a plain `tap` log row.

## rev0190 — nonmana receipt transaction spine

Audited the paid-action body for the user's requested failure mode: useful work getting lost in doctrine/registry bureaucracy while the risky execution spine remains incomplete. The concrete waste was semantic indirection: sacrifice-cost payment receipt proof existed on stack-placement/cost witness surfaces, but the paid-action declaration and terminal transaction did not carry the exact typed sacrifice-cost payment receipt.

This revision promotes the receipt into `PaidActionDeclarationRecord.v2`, `PaidActionTransactionRecord.v6`, and `PaidActionTransactionJournal.v4`. Validation now rejects placement/declaration/transaction/payment-row drift and rejects rollback rows that pretend to contain committed sacrifice-payment evidence.

The next correction over time is a reusable nonmana cost-plan transaction, not more prose: choices, alternative/additional costs, tap/sacrifice/discard/life/counter payments, replacement/prevention interposition, rollback, and final commit should share one ordered proof surface.

---


## rev0184 — zone replacement priority-tier seal

Audited the replacement chain after rev0183. Chain continuity was now sealed, but tier ordering remained a risky gap: a durable row could claim a general replacement was chosen even when an earlier rule-616 priority tier was available. This slice adds `ReplacementPriorityTier`, records `candidate_min_priority_tier` and `eligible_candidate_count` on `ZoneChangeReplacementRecord`, and validates tier skips and malformed eligible counts.

The regression `test_zone_change_replacement_priority_tier_forces_eligible_choice` keeps the cut code-bearing: a high-rank general replacement loses to a represented self-replacement tier, and corrupted records fail closed. The remaining hard work is an interactive rule-616/APNAP choice kernel and real ETB replacement modeling, not more registry surface.

---

## rev0178 — damage life-result receipt links

Audited the next positive damage-result seam after rev0177. `DamageRecord::dealt` already summarized player and lifelink damage, and `LifeChangeRecord` already captured life total mutations, but replay consumers still had to infer the link from event order.

rev0178 adds `first_damage_life_change_record_index` / `damage_life_change_record_count` to `DamageRecord` and damage-result backlinks on `LifeChangeRecord`. The engine snapshots the life-change stream around player damage and lifelink gain, then validation checks source identity, source zone-change identity, target snapshot, amount, row kind, backlink, and exact loss/gain counts. The executable anchor is `test_damage_record_links_player_and_lifelink_life_change_rows`.

---

## rev0170 — paid journal bundle artifact trust

Audited the replay bundle / paid-action transaction boundary after rev0169. The wasteful failure mode was not another missing registry row; it was an omission risk: replay artifacts could prove the final StateCore while paid-action cost/payment receipts remained a separate optional journal.

rev0170 promotes that seam to `ReplayArtifactManifest.v3` with an explicit paid-action journal attachment contract. Attached manifests require `PaidActionTransactionJournal.v3` text, bind the journal's text hash, record count, final-state hash, journal hash, and payload hash into the manifest, and fail old three-file verification with `PaidActionJournalMissing` rather than silently ignoring the attachment requirement.

The refactor is carried through source, tests, CLI, CMake, rules ledger, README, changelog, and this datacube audit. The new executable anchors are `test_replay_artifact_manifest_binds_paid_action_transaction_journal` and `mtgsim_cli_paid_replay_bundle_roundtrip`. This is artifact trust work: it makes paid-action evidence harder to omit from a replayed claim.

---

# rev0158 audit note — paid action declaration / cost lock

Audited the riskiest seam named in rev0157: the paid spell path had stack-entry, mode/target choice anchors, payment spans, and stack placement receipts, but no single typed declaration saying what was locked before payment.

This slice adds `PaidActionDeclarationRecord`, `GameState::paid_action_declaration_records`, `paid_action_declaration_record_hash(...)`, `EventRecordKind::PaidActionDeclaration`, and stack-placement backlinks through `paid_action_declaration_record_index` / `paid_action_declaration_hash`. The record is created after stack entry and choice locking, then sealed after payment with the same paid-action span used by `StackPlacementRecord`. Failed staged casts roll it back with the rest of the speculative body.

The focused regression is `test_paid_spell_declaration_record_locks_costs_before_payment`: success records a declaration before payment, failure does not leak one, and validation catches missing backlinks plus locked-cost hash drift. The next risky implementation slice is activation/loyalty parity and a reusable cost-plan record, not more doctrine.

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

# rev0149 audit note — paid action phase receipts

The rev0148 mission read called out a named paid-action phase as the missing inner seam. rev0149 wires that seam into source, validation, regression tests, docs, and the datacube audit. `seal_paid_action_phase` is now the narrow engine boundary that turns stack-entry timing, choice lock, mana payment, tap/sacrifice payment, and stack placement into durable evidence.

The audit probe intentionally spans docs and ledger surfaces because this is an architectural refactor, not just a helper edit: paid action phase receipts are now part of the trusted transition mission.

---

# rev0148 audit note — mission heart and metadata provenance

The deep read found the core semantic direction sound but the artifact provenance contract under-audited: rev0147's top-level filename/revision identity was current, while some nested `REVISION.json` release/package fields still referenced rev0146. The audit now checks nested artifact/package filename fields and scans selected revision metadata surfaces for stale `rev####` references. This supports the session rule that each turn's linked zip filename is the authoritative revision pointer.

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

## rev0133 — mission spine compass

Deep-read compass slice after the transition trace-entry seal. The mission remains trusted transitions, but the next gap is no longer another outer proof field. The next code-bearing seam should move inward to a reusable paid-casting/activation transaction body with named phases, rollback, and one causal receipt only after all phases succeed. See `docs/architecture/mission_spine_compass_rev0133.md`.

## rev0129 — transition preflight choice seal

rev0129 audits the before-mutation seam left after boundary diagnostics. `TransitionResult` now carries a separate schema-versioned preflight seal through `kTransitionPreflightSealSchemaVersion`, `transition_preflight_schema_version`, `transition_preflight_hash`, public `transition_result_preflight_hash(...)`, `has_transition_preflight_seal()`, and `committed_with_preflight_choice_seal()`.

`seal_transition_result_preflight(...)` hashes the proposal checkpoint, canonical selected action, local `ChoiceRequest`, APNAP `ChoiceRequestQueue`, `LegalActionValidation`, checked page/queue proof locations, proof sentinels, and `legal_before` before staged mutation can be adopted. `check_transition_result_boundary(...)` now localizes `PreflightSealMissing` and `PreflightSealMismatch`, and `TransitionBoundaryVerifyResult` echoes expected/observed preflight hashes so callers can separate stale choice/validation evidence from checkpoint or receipt drift.


## rev0127 — transition boundary seal

rev0127 audits the handoff after `verify_transition_result_boundary(...)`: callers could compose the boundary check, but the returned `TransitionResult` did not yet carry one compact seal for the exact result surface being checked. The refactor adds `kTransitionBoundarySealSchemaVersion`, `transition_boundary_schema_version`, `transition_boundary_hash`, public `transition_result_boundary_hash(...)`, `has_transition_boundary_seal()`, and `committed_with_transition_boundary_seal()`. `seal_transition_result_boundary(...)` runs only after status/reason, checkpoint, choice, page/queue proof, post-action journal, causal receipt, and staged-adoption fields are final. The verifier now rejects stale or schema-drifted boundary seals first, then still falls through to checkpoint and causal receipt guards so malicious resealing cannot bypass `transition_result_matches_receipt(...)`.

## rev0125 — Transition checkpoint seal

Audited the transition-result boundary after the selected-action seal. `TransitionResult` now carries `StateCheckpointSeal checkpoint_before` and `StateCheckpointSeal checkpoint_after`, `capture_transition_before(...)` / `capture_transition_after(...)` derive their scalar fields from those seals, and `committed_with_atomic_adoption_guard()` requires `committed_with_checkpoint_seals()` before a staged state can be adopted. The refactor also removed the duplicate private action-receipt count helper and makes `transition_result_matches_receipt(...)` reject checkpoint-seal drift.

## rev0121 — Transition action journal seal

- Exposed the staged action-body journal sample on `TransitionResult` through `journal_hash_after_action` and `journal_entries_after_action`.
- Strengthened `transition_receipt_matches_result(...)` so the causal receipt's post-action journal hash/count must match the immediate transition result before adoption.
- Added `has_post_action_journal_seal()` and `committed_with_action_journal_seal()`; the atomic adoption guard now includes the post-action journal seal.
- Added `test_commit_action_transition_carries_post_action_journal_seal` and datacube audit probes for the new seal.
- Remaining refactor target: push this transaction boundary inside paid casting and activated ability cost/payment phases, not only around the top-level LegalAction mutation.

## rev0117 — transition result spine audit/refactor

## rev0120 — Transition atomic adoption guard

- Added an atomic adoption guard on top of the rev0119 staged commit seam.
- `TransitionResult` now carries `staged_receipt_checked`, `staged_receipt_consistent`, and `staged_adoption_guard_passed` so the commit result states whether the staged causal receipt was audited before adoption.
- `transition_receipt_matches_result(...)` compares the staged `ActionReceiptRecord` against the transition result's action/schema hashes, StateCore before/after hashes, selected choice-page proof, and `ChoiceQueueLocation` proof.
- `commit_action_transition(...)` now returns `staged_receipt_guard_failed` without adopting the staged state if the staged receipt/proof guard does not pass.
- `committed_with_atomic_adoption_guard()` is the new public helper for callers/tests that need the stricter trusted-transition postcondition.
- Added `test_commit_action_transition_checks_staged_receipt_before_adoption` and extended `audit_transition_result_wiring(...)` so the atomic adoption guard remains wired through code, docs, tests, and the ledger.


Audited the action boundary against the rev0116 mission-spine finding that MTGSim needed an explicit reducer result rather than only side-effecting boolean helpers. The refactor adds `TransitionStatus` / `TransitionResult`, `pending_transition_for_player(...)`, and `commit_action_transition(...)`; factors the LegalAction mutation switch into `apply_legal_action_mutation(...)`; and proves pure NeedChoice inspection, nonmutating rejection, and single-receipt commit with focused C++ regressions. Legacy `apply_action(...)` intentionally keeps illegal-attempt receipts for full-trace audit compatibility.

## rev0095 — legal-surface truth and benchmark reachability audit

- Corrected the strongest semantic audit blind spot found in the cube: bounded combat enumeration could silently present a 128-action prefix as the complete legal set and reject legal omitted choices.
- Added `LegalActionFrontier` completion/budget evidence, direct canonical validation for omitted combat choices, receipt invariants, and replay regressions across attackers, blockers, and damage order.
- Removed repeated requirement-maximization searches and duplicate `apply_action(...)` enumeration.
- Added a retained legal-frontier benchmark, exposed the orphaned branch benchmark, and added a build guard requiring every benchmark source to be reachable through the primary build tool.
- Reframed structural string probes as continuity alarms rather than semantic proof in `mission_legal_surface_budget_audit_rev0095.md`.

## rev0091 — declaration priority gate audit

- Fixed the public action-surface ordering around combat declarations: priority actions are now gated until explicit attacker/blocker declarations, including legal empty declarations, complete.
- Refactored declaration enumeration into helper functions so future combat slices do not have to duplicate batch/empty declaration generation.
- Added a regression that proves `PassPriority` is not legal while a defender's blocker declaration is pending and that priority resumes after explicit no-block.

## rev0090 — combat cost optional payment transaction

- Added mana-only `attack_cost` and `block_cost` fields to `CardDefinition` and wired them into hash/snapshot evidence.
- Refactored combat declaration legality so whole attack/block batches are cost-gated before commit.
- Added shared `pay_combat_declaration_mana_cost(...)` so attack and block costs use the existing mana-ability payment search without turning the turn-based declaration into a priority action.
- Corrected the requirement maximizers to ignore paid combat-cost assignments when deciding what a player is required to do, while still allowing paid declarations when chosen and payable.

## rev0089 — all-able blockers lure requirement solver

- Added `CardDefinition::all_able_blockers_block_this_if_able` as a narrow lure-style blocker assignment requirement.
- Refactored block requirement scoring to include per-blocker obligations in the same maximum-satisfaction search as required blockers and must-be-blocked attackers.
- Added focused public action and replay regressions instead of broad registry growth.

# Audit and refactor notes through rev0014

## rev0088 — Must-be-blocked requirement solver

- Added `CardDefinition::must_be_blocked_if_able` as an attacker-side block requirement with StateCore hash and snapshot coverage.
- Refactored block requirement counting so `maximum_satisfied_block_requirements(...)` scores both required blockers and must-be-blocked attackers in one candidate search.
- Added public LegalAction regressions for no-block filtering, single-blocker maximum choice conflicts, and menace complete-pair satisfaction.
- Kept the audit/refactor localized to the combat declaration seam; the revision does not expand broad registries or claim full CR 509 solving.


## rev0087 — Combat alone restriction solver

- Added a narrow per-creature restriction family, `cant_attack_alone` and `cant_block_alone`, to the same public declaration surface that already handles explicit none, batches, menace, and max-satisfaction requirements.
- Refactored attacker declaration checking through `attack_declaration_basic_constraints_satisfied(...)` so duplicate checks, per-attacker target legality, global caps, and the new alone restriction are evaluated against the complete proposed declaration before commit.
- Replaced the rev0086 attack requirement shortcut with a small candidate search so optional attackers can make a restricted must-attack creature genuinely able.
- Added validation diagnostics for impossible committed combat metadata: `combat.cant_attack_alone_violation` and `combat.cant_block_alone_violation`.


## Why audit belongs in the cube

The datacube is revised every turn. That makes drift likely: stale revision metadata, missing test metadata, bundled build outputs, stale rule rows, malformed scenario files, broken fuzz wiring, broken card-db wiring, broken trigger wiring, or accidental official-rules redistribution. `tools/audit_datacube.py` is the fast structural check that catches these hazards before packaging.

## Prior audit/refactor slices

rev0004 refactored zone container semantics around owner-vs-controller. The regression test proves that a permanent controlled by another player dies into its owner's graveyard, not the controller's graveyard.

rev0005 strengthened the audit by cross-checking `REVISION.json`, `rules_ledger.json`, C++ case rule refs, and ledger test links.

rev0006 centralized zone-container policy in shared helpers and added scenario-file shape checks.

rev0007 normalized target metadata around stack-only storage and expanded audit checks for fuzz wiring.

rev0008 applied the same lifecycle discipline to combat metadata and added card catalog wiring checks.

## rev0009 audit/refactor slice

rev0009 refactors simple effect execution into shared payload dispatch so spells and triggered abilities do not duplicate effect code. It also adds validation and audit hooks for the new trigger machinery:

- pending trigger records must have valid controllers, valid source IDs, and non-empty effect payloads;
- synthetic ability objects must be token/synthetic objects and may only live on the stack or in exile after resolution;
- the audit verifies trigger scenario files, C++ type definitions, engine hooks, validation codes, scenario syntax, test names, CMake wiring, and ledger rows;
- scenario files are still checked for shape, duplicate names, create commands, and validation commands.

## Refactor pattern

When modifying the engine:

1. add or adjust a narrow C++ primitive;
2. expose it through a legal action when player choice is involved;
3. add focused C++ cases with rule refs and tags;
4. add scenario files when the behavior can be described as data;
5. add fuzz coverage when the behavior can participate in legal-action random walks;
6. update the rule-module registry;
7. update the ledger;
8. run `harness.py quick`, `harness.py scenarios`, `harness.py fuzz`, then `harness.py all` or relevant shards;
9. update docs and artifact report.

## rev0010 audit/refactor slice

The rules refactor in this revision was deliberately narrow: damage application now has a prevention/replacement midpoint instead of having combat call `lose_life` or `mark_damage` directly. This is a cleaner seam for future rule 614/615 machinery and prevents combat from bypassing prevention effects.

The audit now checks two new areas:

- prevention wiring across types, engine, validation, scenarios, tests, CMake, rule modules, and ledger rows;
- test-matrix inventory wiring for planner schema v2, work units, duration-greedy bins, and harness arguments.

## rev0011 audit/refactor slice

rev0011 refactors combat and SBA math through `effective_power` and `effective_toughness`. The engine can now grow a real layer/derived-characteristic engine behind those helpers without rewriting callers.

The audit now checks counter wiring across:

- C++ type definitions and public engine APIs;
- effect resolution, state-based actions, zone-change cleanup, and invariant validation;
- C++ test names and rule refs;
- scenario syntax and counter fixture files;
- CMake/CTest wiring;
- rule-module registry entries;
- the metadata-only rules ledger;
- the new counters architecture doc.
- the `--no-sqlite` metrics-summary skip behavior in the matrix harness path.

## rev0012 audit/refactor slice — keyword/static ability plumbing

rev0012 audited the combat and damage call sites that were beginning to hard-code derived behavior. The refactor introduces `KeywordAbilityMask`, `CardDefinition::ability_mask`, and `object_has_ability(...)` so combat/damage code asks a shared query rather than duplicating card-definition reads.

The audit also expanded structural checks for keyword wiring across types, engine APIs, validation, scenario syntax, C++ tests, CMake, card catalog schema, rule-module registry, and the metadata-only rule ledger. This is intentionally boring machinery: future ability work should fail fast if a new scaffold is only half-wired.

## rev0013 audit/refactor slice

The audit/refactor target was combat keyword handling. The risky pre-rev0013 behavior was that “blockedness” was inferred from the current presence of blocker objects. That breaks down as soon as first strike, removal-before-damage, or trample matters. rev0013 adds explicit blocked-attacker memory and validation checks for stale/incoherent blocked metadata.

The second refactor was combat damage itself. Rather than adding first strike/double strike as one-off branches around the old one-pass code, combat damage now runs through deterministic batches. This keeps future additions—damage assignment ordering, damage prevention choices, triggers, and ML action masking—closer to one common path.

Audit coverage now checks the new keyword wiring across C++ types, engine code, validation, scenarios, CMake, card DB masks, and rule-ledger rows.


## rev0014 audit/refactor slice

The refactor target was two pieces of duplicated or missing legality context. Attack legality, tap-mana activation, and validation now share `object_has_summoning_sickness(...)` instead of guessing from zone state. Targeted spell casting and resolution now share `target_ref_is_legal_for_source(...)` instead of having action generation and resolution drift apart.

Audit coverage now checks the new control-start and source-aware target wiring across C++ types, engine APIs, validation codes, scenario syntax, C++ test names, CMake scenario smoke tests, rule-module descriptors, card DB keyword masks, and ledger rows for `302.6`, `702.3`, `702.10`, `702.11`, and `702.18`.


## rev0015 audit/refactor slice

The audit was expanded to probe color/protection/menace wiring through C++ types, engine helpers, validation, scenarios, CMake, card DB schema, rule modules, docs, and ledger rows. The refactor focus was source-characteristics centralization: targeting, damage, and combat now share protection/color helpers instead of each path owning separate ad hoc checks.

## rev0016 audit/refactor slice: destroy versus regeneration

The refactor target for rev0016 was the old implicit “damaged creature goes to graveyard” path. Lethal-damage and deathtouch SBAs now route through `destroy_permanent(...)`, while non-positive toughness still moves directly to the owner graveyard. That separation matters because regeneration can replace destruction but not the non-positive-toughness SBA.

The datacube audit gained a `destroy_regeneration_wiring` section that checks C++ types, public APIs, effect dispatch, validation, scenario syntax, fuzz exposure, CMake smoke wiring, sample card metadata, rule-module registration, and exact ledger rows for `701.8`, `701.19`, `704.5f`, `704.5g`, and `704.5h`.

## rev0017 attachment audit/refactor

rev0017 refactors Aura/Equipment state around explicit `AttachmentKind` and `GameObject::attached_to` metadata instead of leaving attachment behavior as ad hoc future work. The important audit boundary is that attachment legality is centralized in `can_attach_object(...)`, while movement cleanup, state-based actions, validation, stack resolution, scenarios, and effective-characteristic helpers all call shared seams.

The new `audit_attachment_wiring(...)` probe checks that attachment support is wired through C++ types/APIs, engine behavior, validation, scenarios, CMake, rule modules, card DB schema/importer/sample data, docs, and the metadata-only rules ledger. This reduces the chance that future refactors update only one layer of the datacube.

## rev0018 token/exile/sacrifice audit/refactor

rev0018 refactors token lifecycle around an explicit tombstone state. Tokens keep dense object IDs for deterministic logs and trigger references, but once a token has left the battlefield and state-based actions run, it is removed from all zone containers and marked `ceased_to_exist`.

The refactor target was zone-change behavior that previously treated every object as a normal card-like object. `move_object(...)`, validation, the one-shot effect payload dispatcher, and SBAs now share token-aware lifecycle seams. Sacrifice deliberately bypasses `destroy_permanent(...)`, while lethal/deathtouch destruction continues to use the destroy/regeneration seam from rev0016.

The datacube audit gained `audit_token_exile_sacrifice_wiring(...)`, which checks C++ APIs, effect dispatch, validation codes, scenario fixtures, CMake smoke wiring, the rule-module registry, card-catalog schema/importer/sample data, and metadata-only ledger rows for `111`, `406`, `701.7`, `701.13`, `701.21`, and `704.5d`.


## rev0019 audit/refactor slice

Planeswalker work refactored combat defenders from player-only metadata toward target-ref based metadata. The new audit probes check planeswalker types, engine APIs, validation codes, scenario syntax, CMake wiring, card-catalog v6 columns, sample planeswalker cards, rule modules, and ledger rows.


## rev0020 audit/refactor slice: battles

The rev0020 audit pass adds battle wiring checks across C++ types/APIs, engine hooks, validation errors, scenario syntax, CMake smoke tests, card DB schema, docs, rule modules, and metadata-only ledger rows. The code refactor moved combat-object targeting toward a reusable `TargetRef` path shared by planeswalkers and battles.


## rev0021 audit/refactor slice

Modal spell support was used to audit the assumption that every spell has one card-level payload. The refactor added explicit chosen-mode stack metadata, validation for stale/invalid modal metadata, card-catalog columns for mode inventory, CMake scenario smoke, rule-module registry entries, and audit probes that require those pieces to stay wired together.

## rev0022 audit/refactor slice

Timing and land play were used to audit a risky early shortcut: paid casting used to mostly mean “can pay the mana cost.” The refactor split timing into `can_cast_spell_now(...)`, split lands into `can_play_land(...)` / `play_land_from_hand(...)`, added scenario fixture controls for main-phase and arbitrary priority windows, and made the datacube audit require timing/land wiring across C++ APIs, scenario syntax, CMake smoke tests, the card catalog, rule modules, docs, and the metadata-only ledger.

## Rev0023 audit/refactor slice

The refactor target was the old assumption that only spells, loyalty abilities, and triggers could create stack-resolving effect payloads. Generic activated abilities now share the effect payload path, while the audit checks C++ APIs, scenario syntax, fuzz counters, CMake smoke wiring, card DB schema, sample metadata, docs, rule modules, and ledger rows.


## rev0024 audit/refactor: mana ability payment seam

The audit now probes explicit mana-ability wiring across the C++ type model, engine APIs, scenario DSL, fuzz counters, CMake smoke tests, card catalog schema/importer/sample data, rule modules, docs, and ledger rows. The refactor target was the old assumption that paid spells and activated abilities could only consume mana already sitting in a pool.

## rev0025 audit/refactor slice

This revision audited the old assumption that derived characteristics were only printed values plus counters/attachments. The refactor adds a static-effect layer seam and audit probes that require the C++ APIs, scenario syntax, CMake smoke, card DB fields, docs, rule modules, and ledger rows to stay wired together.


## rev0026 audit/refactor slice — control and controller zones

rev0026 audits the owner-vs-controller seam again, but this time through an explicit control-changing effect rather than only a stolen-creature death regression. The refactor target was battlefield controller containers: `gain_control_of_permanent(...)` moves a permanent from the old controller's battlefield vector to the new controller's vector while preserving owner identity.

The second audit target was derived behavior after control changes. The same operation now refreshes summoning-sickness control-start metadata, clears combat metadata, and lets controller-scoped static effects recompute through `object_has_ability(...)`, `effective_power(...)`, and `effective_toughness(...)`.

The audit now checks control wiring across C++ APIs, effect dispatch, scenarios, fuzz sample data, CMake smoke tests, card DB sample/statistics, docs, the rule-module registry, and the metadata-only ledger rows for `108.4`, `109.4`, `110.2`, and `613.1b`.


## rev0027 audit/refactor slice — type/color derived characteristics

rev0027 audits the printed-characteristic shortcut. The refactor target is any gameplay consumer that needs current object type or color: combat, SBAs, validation, protection/source-color checks, fuzz fixture selection, and scenario assertions now have explicit derived helpers to call.

The audit now checks type/color layer wiring across C++ APIs, engine behavior, validation codes, scenario syntax, CMake smoke tests, card DB schema/importer/sample data, docs, rule modules, and metadata-only ledger rows for `205`, `613.1d`, and `613.1e`.

## rev0028 audit/refactor: ability and base-P/T shortcuts

rev0028 audits the next printed-characteristic shortcut after rev0027's type/color pass. Static ability removal and base-P/T setting are now handled inside `object_has_ability(...)`, `effective_power(...)`, and `effective_toughness(...)` so combat, SBAs, and action enumeration do not need one-off exceptions. The datacube audit now probes the new layer-6 and layer-7b fields across C++ types, engine code, validation, scenario syntax, CMake smoke tests, card DB schema/importer/sample data, docs, rule modules, and the metadata-only ledger.
## rev0029 audit/refactor: static-only assumption

This turn audited the assumption that all continuous derived-characteristic changes came from battlefield static sources. The refactor introduced `ContinuousEffectDefinition`, `EffectKind::CreateContinuousEffect`, locked target snapshots, and cleanup expiry while keeping the same derived-characteristic query seams. `tools/audit_datacube.py` now probes C++ APIs, validation, scenarios, CMake, card DB schema, docs, rule modules, and ledger rows for the temporary-effect wiring.

## rev0031 audit/refactor: timestamp ordering

The audited assumption was that static battlefield effects could be applied before generated temporary effects. That is too rigid for real layer work. rev0031 adds `GameObject::layer_timestamp`, a shared monotonic timestamp source, timestamp validation, timestamp-focused scenarios, and audit probes that ensure the type/color/ability/base-P/T projectors sort static and generated applications together.


## rev0032 dependency-order audit

rev0032 audited the derived-characteristic projection assumption that timestamp order was sufficient. `collect_layer_effects(...)` now delegates to a dependency-aware ordering seam after timestamp sorting. The first implementation uses explicit `depends_on_effect_names` metadata so scenario fixtures, fictional card-catalog rows, rule-ledger rows, and future Oracle-text-derived dependency detectors can all feed the same machinery.

The audit added probes for C++ types, engine ordering, validation, scenario syntax, CMake smoke wiring, SQLite catalog dependency counts, sample card metadata, rule modules, and metadata-only ledger rows for 613.8/613.8a/613.8b/613.8c.

## rev0037 target identity audit guard

`tools/audit_datacube.py` now has a `target_identity_wiring` probe. It checks the object target zone-change field, engine stamping/recheck hooks, validation warning, C++ regression, scenario fixture, CMake entry, rules-ledger refs, and effects/targets documentation. This is intentionally a small structural tripwire around a high-risk stack-resolution seam.


## rev0038 mana plan audit/refactor

rev0038 audits the cost-payment assumption that a greedy colored-first mana plan is sufficient. That shortcut is unsafe when one object exposes mutually exclusive tap modes and only a wider mode can satisfy both colored and generic requirements. The refactor moves auto-payment to a bounded deterministic search over legal mana-ability candidates, while preserving same-source tap exclusivity and adding `mana_auto_plan` trace visibility.

The datacube audit now checks the search cap, trace event, C++ regression, scenario fixture, CMake entry, rules-ledger refs, and mana architecture docs so this seam stays wired as later cost, restriction, and choice machinery lands.


## rev0044 audit/refactor note: stack counterspell seam

rev0044 adds `audit_stack_counterspell_wiring(...)` to keep stack-object targeting from regressing across types, engine resolution, scenario parsing, CMake registration, sample card metadata, card-catalog reporting, rules-ledger rows, and docs. This is deliberately a static wiring audit: semantic behavior is covered by the focused C++ regression and `stack_counterspell_targets_stack_object.mtgscn`.

The engine refactor keeps countering inside `apply_effect_payload(...)` rather than as a scenario-only primitive. That means future countering restrictions can be layered onto target legality/effect resolution instead of duplicating stack movement logic in callers.

## rev0045 mission/rule-ID/fuzz-loop audit

The stack counterspell audit now guards CR `701.6` for countering rather than the adjacent cast action rule. This matters because audit probes can otherwise entrench metadata drift. Release fuzz also received a guard against a no-cost optional life-gain activation that had been dominating stochastic priority windows and wasting invariant budget. The fuzzer now also aggregates action-kind counters, prefers legal non-pass actions, seeds short-run combat bodies, and can see defender blocker actions during the declare-blockers step.


## rev0046 audit/refactor note: structured zone-change records

The refactor target was the old movement shortcut where `move_object(...)` was semantically central but left durable evidence mostly as a string event. rev0046 adds `ZoneChangeRecord` and `GameState::zone_change_records` as a typed companion to the `move_object` event. Each record preserves owner/controller transition, source zone, requested destination, finalized destination after replacement, pre/post zone-change indexes, replacement-applied status, and whether the moved object was a battlefield creature whose final destination counts as dying.

This is intentionally not a full event bus. It is the smallest executable bridge toward LKI, replacement, replay, and trigger correctness without adding broad registries. The focused regression proves a lethal SBA move requested as `battlefield -> graveyard` but replaced to exile preserves both destinations, links to the corresponding string event sequence, and fails validation if the finalized zone-change index is corrupted.

The datacube audit now has `audit_zone_change_record_wiring(...)`, which checks the type/header/API, movement hook, validation codes, focused C++ regression, zone-change replacement docs, and rules-ledger references.

## rev0047 audit/refactor: typed damage records

The audit/refactor target was the old damage pipeline assumption that string events were enough evidence for prevention, protection, lifelink, deathtouch, and counter-removal outcomes. That is a high-risk seam because real replacement/prevention, damage triggers, replay, and agent-facing state APIs need structured source/target snapshots and a precise requested/prevented/dealt split.

rev0047 adds `DamageRecord` and `GameState::damage_records` as the typed companion to final damage string events. `deal_damage_to_target(...)` now snapshots source color/abilities, source zone-change identity, object target zone-change identity, target-kind flags, protection-prevention status, and loyalty/defense counters removed. `apply_damage_prevention(...)` returns both remaining and prevented damage so the typed record no longer has to infer prevention from strings.

The validator now rejects malformed damage records, including impossible protection-prevented quantities, bad target/source references, mismatched target zone-change indexes, invalid source masks, future/non-monotonic event sequence numbers, and amount splits where prevented plus dealt does not equal requested amount. The datacube audit now has `audit_damage_record_wiring(...)`, which checks type/header/API wiring, the damage path, validation codes, focused C++ regression, prevention docs, audit notes, and rules-ledger references.

## rev0048 audit/refactor: typed trigger lifecycle records

The audit/refactor target was the old trigger lifecycle shortcut: `PendingTrigger` already carried useful LKI fields, but the durable audit trail ended at string events and synthetic stack objects. That was risky because zone-change and damage records can only support replacement, replay, and agent-facing state if triggers also expose a typed bridge from the causing event to the stack object.

rev0048 adds `TriggerRecord` and `GameState::trigger_records`. Queueing a trigger now appends a durable record that captures event kind, subject object and zone-change identity, source LKI color/ability/zone-change metadata, controller, payload, target requirements, and the causing event sequence. When `put_pending_triggers_on_stack(...)` creates the synthetic ability object, it updates the same record with `stack_object`, `put_on_stack_sequence`, and deterministic stack order; dropped triggers record their dropped sequence instead.

The refactor is intentionally small but substantive: `PendingTrigger` now carries a `trigger_record_index`, so the transient queue cannot drift from the durable record vector. The invariant validator rejects missing links and impossible trigger-record sequencing. `audit_trigger_record_wiring(...)` checks the type/header/API, queue and stack-placement path, validation codes, focused C++ regression, architecture notes, and rules-ledger references.

## rev0049 audit/refactor: unified typed event spine

The audit/refactor target was the remaining string-only event bridge. rev0046 through rev0048 created typed records for zone movement, damage, and trigger lifecycle, but consumers still needed to correlate those vectors with the human-readable `Event` log manually. That is risky for replay, debugging, agent-facing projections, and future replacement/prevention batches.

rev0049 adds `EventRecord` and `GameState::event_records` as a one-to-one typed spine beside `GameState::events`. `record_event_with_links(...)` centralizes emission and attaches typed links for zone changes, damage, trigger queueing, trigger stack placement, and dropped triggers. The specialized records remain the payload authorities; EventRecord supplies the ordered bus and link integrity.

The validator now checks stream cardinality, monotonic sequence alignment, log-kind alignment, object/player/target references, typed-link validity, and reciprocal link counts from `ZoneChangeRecord`, `DamageRecord`, and `TriggerRecord`. `audit_event_record_wiring(...)` checks the type/header/API, emission path, validation codes, focused C++ regression, architecture notes, and rules-ledger references.

## rev0050 audit/refactor: stack-resolution records and Aura late-target failure

The audit/refactor target was the old stack-resolution shortcut where late target legality and resolution outcome were mostly recoverable only from event strings. That was especially risky for Auras: because an Aura spell has no generic effect payload, the resolver could treat its missing/illegal enchant target differently from normal targeted spells.

rev0050 adds `StackResolutionRecord` and `GameState::stack_resolution_records`. `resolve_top_of_stack(...)` now records chosen-target snapshots, required and legal target counts, outcome, payload-applied status, stack-zone identity, and the linked stack-leaving `ZoneChangeRecord`. The focused regression proves an Aura whose target leaves before resolution records `NoLegalTargets` and goes directly from stack to graveyard rather than entering the battlefield and failing attachment afterward.

The validator rejects broken `EventRecord` links, malformed target-failure flags, invalid stack-leave zone-change links, invalid outcomes, and payload-application claims when resolution was blocked. `audit_stack_resolution_record_wiring(...)` checks the type/header/API, resolver, validation codes, focused regression, effects-and-targets documentation, audit notes, and rules-ledger references.

## rev0051 audit/refactor: zone-change replacement records and dead-code cleanup

The risky seam was replacement ordering. rev0050 had durable final movement through `ZoneChangeRecord`, but each applied replacement in the chain still lived mostly as string log text. rev0051 adds `ZoneChangeReplacementRecord` and `GameState::zone_change_replacement_records`, links each applied replacement through `EventRecordKind::ZoneReplacement`, and backfills the final `ZoneChangeRecord` with the replacement-record range.

The focused regression covers a two-pass replacement chain with a multi-candidate first pass. It verifies affected-player fallback choice metadata, candidate count, choice rank, source zone-change identity, event-to-zone rewrite order, final movement linkage, and validator failure when a replacement record is detached from its movement.

The audit also removes two small dead duplicate returns in `definition_has_flash(...)` and `target_label(...)` while touching the replacement path. This was intentionally kept to source hygiene rather than broad rearrangement.

## rev0052 audit/refactor: typed state-based action records

The risky seam was the state-based action pass. By rev0051, zone movement, damage, triggers, stack resolution, and zone-change replacement all had typed records, but the SBA coordinator still forced consumers to infer why a permanent moved, regenerated, detached, ceased to exist, or caused a player loss by reading string events and side effects.

rev0052 adds `StateBasedActionRecord` and `GameState::state_based_action_records`, linked through `EventRecordKind::StateBasedAction`. The record captures the SBA kind, object/player subject, battlefield zone-change snapshot, effective P/T, marked damage, deathtouch damage, +1/+1 and -1/-1 counters, loyalty/defense counters, regeneration shields before and after, indestructible status, whether regeneration_applied, whether an object left the battlefield, and the linked `ZoneChangeRecord` when movement occurs.

The engine refactor centralizes SBA emission through `record_state_based_action(...)` and zone movement back-linking through `link_state_based_action_to_zone_change(...)`. That keeps the high-risk paths small: lethal damage, deathtouch damage, non-positive toughness, zero loyalty, zero defense, illegal attachment cleanup, Aura cleanup, counter-pair cancellation, token cease, and player-loss checks now leave typed evidence in the same ordered event spine used by the other record families.

The validator rejects malformed SBA records, including damage-destroy records with neither regeneration nor a zone move, regeneration records that do not consume a shield, stale or mismatched zone-change links, unexpected regeneration on non-destroy SBAs, missing player/object subjects, and token/attachment flags that do not match their SBA kind. `audit_state_based_action_record_wiring(...)` checks the type/header/API, engine helper, validation codes, focused C++ regression, architecture docs, audit notes, and rules-ledger references.

## rev0053 audit/refactor: typed combat-damage assignment records

The risky seam was combat damage assignment. By rev0052, damage and SBAs had durable typed records, but the combat step still explained routing through strings such as `combat_damage_object` and `combat_damage_trample_defender`. That left trample excess, first-strike batches, blocked-attacker memory, and blocker damage difficult to audit without parsing human-readable logs.

rev0053 adds `CombatDamageAssignmentRecord` and `GameState::combat_damage_assignment_records`, linked through `EventRecordKind::CombatDamageAssignment`. The record captures source/target zone-change snapshots, source controller, assigned amount, source role, first-strike/split-batch flags, blocked-attacker context, blocker count, trample/excess flags, and the resulting `DamageRecord` index.

The engine refactor centralizes combat assignment emission through `record_combat_damage_assignment(...)` and uses a small `assign_and_record(...)` helper inside `assign_combat_damage(...)`, keeping the changed surface local to the combat step. The validator now rejects broken damage links, malformed source roles, missing LKI snapshots, impossible blocker/trample flags, and broken event-spine links. `audit_combat_damage_assignment_record_wiring(...)` checks type/header/API wiring, combat emission, validation codes, focused C++ regression, combat docs, audit notes, and rules-ledger references.

## rev0054 audit/refactor: typed combat-declaration records

The risky seam was combat declaration. By rev0053, combat damage assignment had typed records, but attacker and blocker declarations were still verified mostly through transient object metadata and human-readable events. That made vigilance, attacked-object snapshots, menace batch blocking, and final blocked-attacker state hard to audit before damage assignment consumed them.

rev0054 adds `CombatDeclarationRecord` and `GameState::combat_declaration_records`, linked through `EventRecordKind::CombatDeclaration`. The record captures attacker/blocker role, actor and target zone-change snapshots, defending player, tapped-before/tapped-after state, vigilance, flying/reach/menace snapshots, blocker batch size, final blocker count for the attacker, `menace_satisfied`, and whether the attacker was marked blocked after declaration.

The engine refactor centralizes declaration emission through `record_combat_declaration(...)` and uses `blocker_count_for_attacker(...)` to snapshot final batch context only after the blocker batch is committed. This keeps the declaration audit close to the combat declaration helpers rather than spreading more registry or scenario-only code.

The validator rejects broken declaration event links, invalid role fields, stale zone-change snapshots, attack/block target mismatches, vigilance tap mismatches, blocker tap mutation, flying/reach snapshot corruption, and menace records whose final blocker count contradicts the recorded satisfaction flag. `audit_combat_declaration_record_wiring(...)` checks type/header/API wiring, engine emission, validation codes, focused C++ regression, combat docs, audit notes, and rules-ledger references.


## rev0055 audit/refactor slice: stack placement and priority handoff

rev0055 audits the pre-resolution stack placement seam. `StackPlacementRecord` and `GameState::stack_placement_records` now make spell casts, activated abilities, and loyalty abilities leave typed records linked into the `EventRecord` spine. The records capture source/stack identity, chosen targets, modal index, stack size before/after, paid mana/tap/sacrifice/loyalty cost flags, and `priority_after`.

The concrete correction is that spell and loyalty paths now retain priority for the acting controller after placement instead of advancing to the next player. Counterspell response tests were updated to require the caster's priority pass before the opponent may respond. The audit probes `types.hpp`, `engine.hpp`, `engine.cpp`, `validation.cpp`, focused C++ tests, activated-ability docs, and the rules ledger for `StackPlacementRecord` wiring.
## rev0056 audit/refactor slice: typed priority-transition records

The risky seam after rev0055 was the pass chain itself. Stack placement now kept priority with the acting controller, but a later pass could hand priority to the next player, resolve the top stack object, advance the step, or gate the pass behind pending triggers. Those outcomes were still mostly implicit in mutable engine state and string events.

rev0056 adds `PriorityTransitionRecord` and `GameState::priority_transition_records`, linked through `EventRecordKind::PriorityTransition`. The records capture the acting player, active player, priority before/after, step before/after, stack sizes and top object snapshots, pending-trigger counts, consecutive-pass snapshots, outcome flags, and the linked `StackResolutionRecord` when a pass causes resolution.

The local refactor centralizes this seam through `capture_priority_transition_snapshot(...)` and `record_priority_transition(...)` inside `pass_priority(...)`. Validation rejects broken event links, impossible priority handoff, stack-resolution links without a resolved stack outcome, step-advance records without a step change, and pass-count snapshots that no longer match the recorded outcome. `audit_priority_transition_record_wiring(...)` checks type/header/API wiring, engine emission, validator codes, focused C++ regression, timing docs, audit notes, and rules-ledger references.



## rev0057 audit/refactor slice: draw records and zone-pipeline correction

The risky seam was card draw. The old `draw_card(...)` path popped the library vector, assigned `object.zone = Zone::Hand`, and pushed into the hand vector directly. That bypassed `move_object(...)`, so drawn cards did not produce `ZoneChangeRecord` entries and could not be replayed through the typed `EventRecord` spine.

rev0057 fixes that by routing successful draws through `move_object(game, top, player_id, Zone::Hand)` and adding `DrawRecord` / `GameState::draw_records`. Each successful draw captures the drawing player, card, library/hand size transition, empty-library attempt counters, card zone-change identity before/after, and the linked library-to-hand movement. Empty-library attempts record no card movement but capture the attempt counter increment.

The validator rejects broken draw event links, successful draws without a zone-change link, library/hand size mismatches, non-advancing card zone-change identities, and empty-library records that claim card movement or fail to increment the attempt counter. `audit_draw_record_wiring(...)` checks type/header/API wiring, the engine draw path, validation codes, focused C++ regression, engine-design docs, audit notes, and rules-ledger references.

## rev0058 audit/refactor slice: typed mulligan redraw records

The risky seam was pregame hand churn. rev0057 fixed normal card draw so successful draws use `move_object(...)` and leave `DrawRecord` evidence, but mulligans were still absent. That left the highest-risk opening-hand operation—return hand, shuffle, redraw—without an executable API or typed audit trail.

rev0058 adds `MulliganRecord` and `GameState::mulligan_records`, linked through `EventRecordKind::Mulligan`. `take_mulligan(...)` returns the whole hand to library via hand-to-library `ZoneChangeRecord`s, shuffles with the deterministic engine RNG, redraws via `draw_card(...)`, increments `PlayerState::mulligans_taken`, and records the return and redraw ranges.

The validator rejects malformed mulligan records, including a hand that was not cleared before redraw, broken return movement ranges, draw-count mismatches, shuffle size drift, failed pipeline flags, player mismatches, and missing event-spine links. `audit_mulligan_record_wiring(...)` checks type/header/API wiring, engine emission, validation codes, focused C++ regression, engine docs, audit notes, and rules-ledger references.

## rev0059 audit/refactor slice: typed mulligan keep/bottom records

The risky seam was the part rev0058 deliberately left open: after a mulligan redraw, the engine could increment `mulligans_taken` but had no executable keep step that bottomed cards. That meant opening-hand setup still became non-replayable at the exact point where the London mulligan requires a choice-bearing hand-to-library transition.

rev0059 adds `MulliganKeepRecord` and `GameState::mulligan_keep_records`, linked through `EventRecordKind::MulliganKeep`. `keep_mulligan_hand(...)` bottoms a number of cards equal to `PlayerState::mulligans_taken`, validates explicit choices, provides a deterministic fallback when no choices are supplied, routes each bottomed card through `move_object(...)`, and then inserts those cards at the library bottom in recorded order.

The local refactor adds `record_mulligan_keep_record(...)` and `place_library_object_on_bottom(...)` rather than spreading bottom placement across setup code. Validation rejects broken event links, bad bottom-count snapshots, duplicate or invalid bottomed cards, malformed hand-to-library `ZoneChangeRecord` ranges, missing zone-pipeline flags, and records that fail to mark bottom placement. `audit_mulligan_keep_record_wiring(...)` checks type/header/API wiring, engine implementation, validator codes, focused C++ regression, engine docs, roadmap, audit notes, and the rules ledger.

## rev0061 — life-total mutation audit/refactor

The risky direct path in this slice was not another registry gap; it was `lose_life(...)` and `gain_life(...)` mutating `PlayerState::life` while leaving only human-readable event strings behind. rev0061 adds `LifeChangeRecord`, stores those records in `GameState::life_change_records`, links them via `EventRecordKind::LifeChange`, and validates the gain/loss delta plus one-to-one EventRecord linkage. This gives the reducer a replayable life-total seam for damage, lifelink, and triggered life-gain effects without pretending to solve every replacement or “can’t gain life” effect yet.

## rev0062 — mana-pool mutation audit/refactor

The risky direct path in this slice was mana-pool mutation: `add_mana(...)`, `pay_mana_cost(...)`, automatic payment, mana-ability activation, and `clear_mana_pool(...)` changed `PlayerState::mana_pool` while leaving only prose logs. rev0062 adds `ManaChangeRecord`, stores records in `GameState::mana_change_records`, links them via `EventRecordKind::ManaChange`, and validates production/payment/emptying deltas plus one-to-one EventRecord linkage.

The local refactor consolidates production, payment, and clearing through small recorded helpers rather than duplicating mutation logic at public API, mana-ability, and auto-payment call sites. The new focused regression corrupts both a paid colored-cost delta and an event-record link so the validator proves this seam is executable rather than a registry-only claim.


## rev0063 — counter mutation audit/refactor

The risky direct path in this slice was counter mutation. Object counters, poison counters, planeswalker loyalty, battle defense, damage-driven counter removal, and SBA +1/+1/-1/-1 cancellation changed state while leaving consumers to infer meaning from string events and final object snapshots. rev0063 adds `CounterChangeRecord`, stores records in `GameState::counter_change_records`, links them via `EventRecordKind::CounterChange`, and validates object/player identity, counter kind, before/after deltas, source zone identity, damage-result flags, monotonic sequences, and one-to-one EventRecord linkage.

The local refactor consolidates object and player counter writes through recorded helpers rather than duplicating event emission at public counter APIs, planeswalker/battle entry, damage handling, and SBA pair cancellation. The focused regression covers object add/remove, player poison, corrupted player deltas, and planeswalker damage removing loyalty counters with a source snapshot. `audit_counter_change_record_wiring(...)` now checks type/header/API wiring, engine emission, validation codes, focused C++ coverage, engine docs, audit notes, and rules-ledger references.

## rev0064 — counter cost and zone-cleanup audit/refactor

The riskiest counter leftovers after rev0063 were not new registry rows; they were two direct mutation seams that could still hide state changes from replay consumers. `activate_loyalty_ability(...)` paid loyalty by mutating `obj.counters.loyalty` directly, and `clear_counters_for_zone_change(...)` erased an object's whole `CounterSet` while emitting only a string event. Both paths are now typed.

rev0064 adds cause metadata to `CounterChangeRecord`: `cost_payment`, `zone_change_cleanup`, and `zone_change_record_index`. Loyalty ability costs now record +N/-N loyalty as cost-payment rows with source/object identity, before/after counts, and EventRecord linkage. Zone changes now emit one object-removal `CounterChangeRecord` per nonzero counter kind removed, and the owning `ZoneChangeRecord` stores `first_counter_change_record_index` plus `counter_change_record_count` so the move and the cleanup range stay auditable together.

The validator now checks cleanup back-links in both directions, rejects malformed ZoneChangeRecord cleanup ranges, rejects cleanup rows that carry damage/source/cost payloads, and requires cost-payment counter rows to identify their source object. The focused regression covers positive loyalty costs, EventRecord counter links, two-kind zone cleanup, ZoneChangeRecord cleanup ranges, and corruption of a cleanup backlink. This is deliberately executable plumbing; replacement/modification effects for counter placement remain future work.

## rev0065 — prevention shield record audit/refactor

The riskiest prevention leftover after typed `DamageRecord`s was the mutable shield vector. Adding a shield, consuming part of a shield, and expiring object-targeted shields on movement changed `GameState::damage_prevention_shields` while leaving replay consumers to infer the details from generic damage or zone events. That was especially fragile for a future replacement/prevention kernel, because shield consumption is an event-ordering decision rather than a mere final damage total.

rev0065 adds `DamagePreventionRecord` and `GameState::damage_prevention_records`. Shield creation emits `ShieldAdded`, damage consumption emits `ShieldConsumed`, and zone-change cleanup emits `ShieldExpired`. The rows are linked into the unified `EventRecord` spine through `EventRecordKind::DamagePrevention`; consumed rows also link to the owning `DamageRecord`, while expired rows are owned by a prevention-record range on `ZoneChangeRecord`.

The validator now rejects broken damage-prevention event links, invalid damage-record prevention ranges, consumption totals that do not match prevented damage, stale active object shields, and zone-expiry backlinks that point at the wrong movement. `audit_damage_prevention_record_wiring(...)` checks the type fields, engine helpers, validator errors, focused tests, prevention architecture notes, and rules-ledger rows. This is intentionally event-kernel progress rather than registry expansion: real source filters, redirection, and rule-616 ordering still belong to the future replacement resolver.

## rev0066 — discard choice and cleanup audit/refactor

The risky seam after prevention shields was not another registry row; it was discard movement. `discard_down_to_max_hand_size(...)` selected cards and moved them from hand to graveyard, but replay consumers had to infer that those zone moves were discard choices from prose events and surrounding state. Explicit discard helpers were also missing a typed choice row.

rev0066 adds `DiscardRecord` and `GameState::discard_records`, linked through `EventRecordKind::Discard`. cleanup discard and explicit choice discard both route through `discard_card_for_reason(...)`, preserve the normal `move_object(...)` zone pipeline, and record hand/graveyard deltas, max-hand-size context, card zone-change identity before/after, and the linked `ZoneChangeRecord`.

The validator rejects broken discard EventRecord links, invalid player/card references, hand/graveyard deltas that do not match a single discard, missing zone-pipeline movement, explicit/cleanup flag mismatches, cleanup records that were not required by hand size, and zone-change records that do not describe hand-to-graveyard movement. `audit_discard_record_wiring(...)` checks type/header/API wiring, engine emission, validation codes, focused C++ regressions, engine docs, audit notes, and rules-ledger rows for cleanup and discard coverage.

## rev0067 — mission truth, revision identity, and hard cloud budgets

The audit target is infrastructure truth rather than another rule registry row. The repository had begun calling typed evidence rows “replay” without a serializer, checkpoint, state hash, or reconstruction API, while `GameState` continued to own both authoritative state and every unbounded history vector. rev0067 records the distinction explicitly: current rows are forensic transition evidence; replay becomes a valid claim only after checkpoint-plus-input reconstruction proves the same canonical state hash.

The cloudtainer also had a concrete budget failure. `tools/build.py --time-budget-sec` checked time only before starting a command, so one GCC compile could exceed the whole budget. Sanitizer compilation of `src/validation.cpp` did exactly that. The build helper now gives every compile/link the remaining deadline, runs it in a process group, kills the group on timeout, and defaults sanitizer-mode validation to `-O0 -g1` with ASan/UBSan retained. `tests/python/test_build_tool.py` exercises both guards.

A separate identity audit found `REVISION.json` at rev0066 while the official-rules manifest said rev0061, `pyproject.toml` said rev0059, and the CLI banner said rev0001. The datacube audit now treats those drifts as errors. The priority-pass benchmark also reports pass pairs and actual pass calls separately and labels itself a microbenchmark, closing a misleading “passes/game” unit.

The recommended next revision is the state/journal boundary with canonical state hashing and configurable journal retention. Adding another per-mutation record vector before that boundary would deepen the very coupling this audit identifies.

## rev0069 — action receipts as replay seeds, not UI labels

rev0069 targets the next risky gap after the StateCore/Journal split: `LegalAction` values were executable but not durable. The only stable external-looking action surface was a display label, which is not replay data. The revision adds `ActionReceiptRecord` rows around `apply_action(...)`, recording canonical action fields, a label-independent canonical action hash, legal/applied status, pre/post StateCore hashes, and journal hash/count deltas sampled before the receipt itself is appended.

This is intentionally not full replay. It is a replay-seed boundary: future checkpoint reconstruction can consume the canonical action stream and compare the resulting StateCore hashes. The audit/refactor also covers trimmed branches so a branch can prove its first new action started from zero inherited journal entries.

## rev0070 — action trace replay check, not another registry

rev0070 focuses on the riskiest remaining replay seam after action receipts: receipts could describe transitions, but the cube still could not export them and reapply them against a checkpoint. The revision adds `ActionTraceEntry`, `export_action_trace(...)`, and `replay_action_trace(...)`, with step-local checks for action-hash, pre-state hash, applied/rejected status, and post-state hash divergence.

The refactor is deliberately small: `action_from_receipt(...)` is now the single receipt-to-action projection used both by validation and trace export. This removes a drift point where validation could accept a receipt that replay export would canonicalize differently.
## rev0071 action trace text codec audit

The action boundary now has a plain-text trace codec instead of relying on in-memory vectors. `serialize_action_trace(...)` and `parse_action_trace(...)` keep labels out of replay data, preserve vector targets and zone-change stamps, and reject malformed/non-contiguous trace steps before replay can mutate a checkpoint. This is a narrow replay artifact seam, not a new registry. The next high-risk gap is checkpoint serialization.


## rev0072 — checkpoint seal replay guard

The risky replay gap after rev0071 was not another action registry; it was starting-state ambiguity. A text action trace could cross a file boundary, but the engine still trusted the caller to supply the right in-memory checkpoint. rev0072 adds `StateCheckpointSeal`, a stable `MTGSim.StateCheckpointSeal.v1` codec, and `replay_action_trace_from_checkpoint(...)` so the wrong starting state fails before trace step one mutates StateCore or writes journal rows.

This is intentionally not full state deserialization. The seal is a compact identity contract over StateCore hash, journal hash/count, action receipt count, object/player/stack counts, RNG state, allocators, turn/step, active/priority players, and journal-trimmed status. The next larger snapshot codec can build on the same guard instead of letting persisted traces float free.

## rev0073 — StateCore snapshot replay root

rev0073 addresses the riskiest remaining replay gap after checkpoint seals: the engine could verify that a trace belonged to a checkpoint, but could not yet reconstruct that checkpoint from a durable artifact. The revision adds a compact `MTGSim.StateCoreSnapshot.v1` codec plus `StateCoreSnapshotParseResult`, preserving the same continuation fields covered by `canonical_state_hash(...)`.

The refactor deliberately keeps the snapshot as a replay-root artifact, not another journal registry. Parsed snapshots carry a trimmed/empty journal and preserve the source checkpoint seal, so trace replay can cross process/file boundaries without pretending evidence rows were serialized. Regression coverage now proves parsed snapshots can replay parsed action traces and that pending triggers, prevention shields, and continuous effects survive StateCore reconstruction.

## rev0074 — risk-seam fuzz coverage guard

rev0074 turned a passive fuzz metric into an executable requirement. The broad random walk had counters for trigger-stack and loyalty actions, but ordinary seeds could still pass while exercising neither. The risk profile now creates fixture states that make pending-trigger stack placement and loyalty activation legal, prioritizes those actions, and can fail if either seam is missed.

This is validation substance rather than registry growth: `mtgsim_fuzz --profile risk-seams --require-risk-seams` makes the high-risk branches observable in short cloud runs.

## rev0075 — CLI replay artifact verify

The risky gap after StateCore snapshots and action traces was the process boundary. Library tests could serialize and parse replay data, but the shipped CLI could not write a snapshot/trace pair and then verify it from disk. rev0075 adds a disk-bound replay workflow through `mtgsim_cli --write-demo-replay`, `--verify-replay`, and `--artifact-roundtrip`.

The refactor keeps this path narrow: it does not invent a new card registry or serialize journal evidence. It wires the existing `StateCoreSnapshot.v1`, `ActionTrace.v1`, `parse_state_core_snapshot(...)`, `parse_action_trace(...)`, and `replay_action_trace(...)` pieces into an executable CLI path with a CMake smoke test and datacube audit probes.


## rev0076 — replay artifact manifest trust

The risky gap after rev0075 was artifact trust, not another rules registry. A CLI could write a `StateCoreSnapshot.v1` and `ActionTrace.v1` pair, but the pair had no single manifest binding exact bytes, source checkpoint metadata, action count, and expected final StateCore hash. That made it too easy to verify the wrong pair or to lose the final-state intent outside the process that wrote the files.

rev0076 adds `ReplayArtifactManifest.v1`, a parser, a self-hash `bundle_hash`, and `verify_replay_artifact_bundle(...)`. Verification now rejects changed snapshot text, changed trace text, checkpoint metadata mismatch, action-count mismatch, replay divergence, and final StateCore drift before a bundle is accepted. The refactor is intentionally narrow: it wraps the existing snapshot and trace codecs instead of creating more registry bureaucracy or serializing journal evidence.

## rev0077 — replay bundle diagnostics and inspection

The risky gap after rev0076 was not another serialization format. The manifest could prove snapshot/trace/checkpoint/final-state trust, but a failed bundle still needed sharper operational diagnostics. rev0077 adds `ReplayArtifactFailureKind`, expected/actual checkpoint and action-count fields, and `mtgsim_cli --inspect-replay-bundle` so a caller can localize text-hash tampering, checkpoint-seal mismatch, action-count mismatch, replay-step divergence, or final StateCore mismatch from a compact disk-bound report.

The refactor keeps the prior bundle design intact. Inspection wraps the existing snapshot, trace, manifest, and replay verifier instead of creating another registry layer.

## rev0078 — replay prefix localization

The risky gap after rev0077 was not another serialization schema. The bundle verifier could classify failures, but a trace replay divergence still left the user with a full trace and a mismatch index. That is operationally wasteful when failures eventually come from long fuzz or agent traces.

rev0078 adds `ReplayArtifactPrefixResult` and `make_replay_artifact_prefix_bundle(...)`. For replay-step failures, the prefix bundle contains the longest known-good prefix and records `next_bad_step`; for final-StateCore mismatches, the full replay-good trace is retained and the prefix manifest is rewritten to the replayed final hash. The CLI exposes this as `--write-replay-prefix`, and CTest keeps `mtgsim_cli_replay_bundle_prefix_roundtrip` executable.

The audit/refactor focus is the artifact boundary itself: reduce failing replay bundles to small, manifest-bound evidence without adding a doctrine registry or serializing the forensic journal.

## rev0079 — Replay resume probe

The replay-bundle path now has an actionable resume artifact, not only a reduced prefix. `ReplayArtifactResumeResult` and `make_replay_artifact_resume_probe(...)` replay the longest known-good prefix, serialize a fresh `StateCoreSnapshot.v1` at that boundary, and write the remaining suffix as `ActionTrace.v1` plus `ReplayArtifactManifest.v1`. This keeps manifest trust checks intact while making the suspect transition suffix step one for smaller repros. The CLI exposes the path through `--write-replay-resume-probe`, and CTest keeps `mtgsim_cli_replay_bundle_resume_roundtrip` executable.

A small audit/refactor cleanup also removed duplicate `--help` printing in `mtgsim_cli`, which mattered because the CLI is now the durable replay-artifact surface.

## rev0080 — Choice request trace guard

- Audited the action/replay seam after resume probes and found the selected action was bound more strongly than the offered choice surface.
- Added typed ChoiceRequest hashing and carried it into receipts/traces so enumeration drift is diagnosed before mutation.
- Refactored Release compile options for the monolithic mtgsim_tests target to avoid optimizer budget dominating validation.

## rev0081 — Choice request queue APNAP guard

The riskiest rules/replay gap after rev0080 was that a trace could bind the selected player's local `ChoiceRequest` but still ignore the global ordered choice surface. That is too weak for future APNAP simultaneous choices, trigger-order choices, and replacement-order prompts: the selected action may be locally stable while the surrounding ordered request queue has changed.

rev0081 adds a compact `ChoiceRequestQueue` rather than another registry. `apnap_ordered_players(...)` gives the engine a reusable active-player-then-turn-order spine, `choice_request_queue(...)` filters it down to non-empty choice surfaces, and `choice_request_queue_hash(...)` binds the ordered queue to StateCore. Action receipts and `ActionTrace.v1` now store queue hash/index/size, and replay checks that queue before applying the action.

The audit/refactor change is deliberately narrow: it does not attempt full simultaneous-choice resolution yet. It makes any future work on APNAP choices observable and replay-guarded, and it adds validation/audit probes so queue metadata cannot silently disappear from receipts, traces, or CLI diagnostics.


rev0081 audit phrase: choice queue metadata is now a guarded replay seam.

## rev0082 — core-only branch cost correction and semantic truth audit

The deep read found that the replay/evidence shell had advanced beyond the semantic transaction it certifies. The highest-risk example is combat: `LegalAction` cannot carry a whole blocker declaration, so the public action surface cannot express the legal two-blocker answer to menace even though an internal batch helper can. The new `mission_semantic_kernel_audit_rev0082.md` records atomic combat declarations, real trigger-order choices, transactional casting, and a proposal/replacement/commit event kernel as the next semantic sequence.

The immediate refactor removes a concrete branch/search tax. `make_branch_state(..., ClearAll)` no longer deep-copies all journal vectors and then clears them; it constructs a branch from continuation fields only and detaches pending-trigger journal anchors. Choice queue construction also reuses one precomputed StateCore hash across all per-player requests instead of hashing the whole state once per APNAP participant.

This revision intentionally adds a behavioral C++ guard rather than another broad string-presence registry. The audit script remains useful for package integrity, but future semantic assurance should move toward end-to-end contracts and negative tests.


## rev0083 — Public menace batch action bridge

The riskiest reachable semantic gap after rev0082 was not another ledger row: a legal two-blocker menace declaration could be made only through the internal helper/scenario escape hatch, not through the public `LegalAction` boundary that receipts and traces trust. rev0083 adds a narrow pair-vector encoding for blocker batches, decodes that shape back into `BlockAssignment` records, and routes scenario `block_batch` through `apply_action(...)` instead of bypassing receipts.

This is intentionally a bridge toward atomic combat, not the final design. The old single-blocker encoding still round-trips for compatibility, while the menace batch now proves enumerate -> apply -> receipt -> trace replay for the first blocker batch that previously fell outside the trusted transition boundary. The audit probe was tightened around the new public helpers rather than adding another broad registry.

## rev0084 — Declaration finality action surface

The next risky seam after the menace batch bridge was declaration finality. The engine could now carry a blocker batch, but attacker declarations still looked like incremental one-creature actions, and empty declarations were encoded as absence. rev0084 adds `AttackAssignment`, attacker-batch action encoding/decoding, explicit no-attack and no-block actions, and declaration-completion state in StateCore.

The useful refactor is deliberately local: blocker legality now flows through `block_assignment_basic_legal(...)`, while final batch checks such as menace remain at the batch layer. This reduces drift between the legacy single-blocker helper, the batch helper, and legal-action enumeration without pretending the full restriction/requirement solver exists yet.

The validator now treats malformed blocker-completion player lists as errors. Stale completion flags outside their natural step are warnings because older direct fixture tests still assign `game.step` manually; normal step advancement clears the fields.


## rev0096 — validation source trace frontier proof

The audit/refactor focus was the action proof boundary, not another registry. The selected action now carries a durable validation source through receipt hash material, `ActionTrace.v2`, and replay. This distinguishes a listed `OfferedAction` from `DirectDomainValidation` on an incomplete combat frontier and lets replay reject source drift before mutation.

The cleanup also removed the stale membership-only helper and moved audit probes toward the executable source-aware path: `validate_legal_action(...)`, `choice_validation_source`, and `ChoiceValidationSourceMismatch`.

## rev0097 — combat legal-action cursor paging

The riskiest leftover after validation-source traces was discovery. A caller could validate a known omitted combat action, but still had no structured way to enumerate beyond the bounded 128-action prefix.

rev0097 adds `LegalActionPage` and `enumerate_legal_action_page(...)` for attack declarations, block declarations, and combat-damage order permutations. The bounded frontier remains a cheap truthful prefix; the page API resumes by deterministic cursor so agents and replay tooling can reach late legal choices without inflating the default budget.

The useful refactor is small: shared combat action labelling helpers reduce drift between frontier generation and page generation, and invalid player ids are rejected at both query surfaces without mutating StateCore. The CMake Release defaults for hotspot translation units were also lowered to avoid optimizer time becoming the cloudtainer bottleneck; performance-oriented local builds remain available through the existing build tool overrides.


## rev0098 — legal-action page location

The audit/refactor target was the seam between direct validation and cursor-paged discovery. rev0097 let callers enumerate beyond the bounded frontier, but a selected action still had no executable way to prove its page position without hand-rolling a scan.

rev0098 adds `LegalActionPageLocation` and `locate_legal_action_page(...)`. The locator reports the containing page cursor, zero-based action cursor, index in page, scanned page count, and requested/effective page-limit metadata. A zero requested page limit is normalized to an effective one for the locator so external probes cannot produce a non-progressing cursor loop.

The refactor is deliberately narrow: validation remains cheap and authoritative, paging remains discovery, and location remains opt-in proof. The new tests reconstruct late attack and damage-order actions from their page/index pair and verify wrong-chooser probes do not mutate StateCore.

## rev0099 — replay-guarded page-location evidence

The audit/refactor target was the remaining seam after rev0098: page location existed as an opt-in query, but it was not yet part of action evidence. A run could prove that an omitted bounded-frontier action was legal without proving that the same action still occupied the same deterministic cursor position.

rev0099 carries page-location metadata through `ActionReceiptRecord` and `ActionTrace.v3`, including page cursor, action cursor, index in page, next cursor, scan count, and page completion. Replay recomputes `locate_legal_action_page(...)` and returns `ChoicePageLocationMismatch` before StateCore mutation when the trace and current engine disagree.

The refactor cleanup removed a duplicate `classify_choice_request(...)` assignment in the request construction path and extended receipt validation to reject legal action receipts that lack deterministic page-location evidence.


## rev0100 — page hash and zero-limit cursor progress

The riskiest remaining choice-protocol gap was not another registry entry; it was that a page-location receipt proved cursor/index metadata without binding to the page content, and a public zero-limit page request could produce a non-progressing cursor. rev0100 adds `LegalActionPage::effective_limit`, `LegalActionPage::page_hash`, public `legal_action_page_hash(...)`, `LegalActionPageLocation::page_hash`, receipt `choice_page_hash`, and `ActionTrace.v4` `choice_page_hash` serialization. The zero-limit API now preserves `requested_limit == 0` while normalizing to `effective_limit == 1`, and replay rejects page-hash drift before StateCore mutation.


## rev0102 legal-action page protocol refactor

rev0102 audited the legal-choice paging seam and found a drift hazard: bounded frontier prefixes and cursor pages shared labels and tests but still had separate executable enumeration loops for attack declarations, block declarations, and combat-damage order. The refactor routes frontier prefixes through the same per-domain `for_each_legal_*` emitters as pages via `append_bounded_frontier_actions(...)`, preserving the 128-action budget while removing a future split-brain legality risk. The revision also adds `kLegalActionPageSchemaVersion`, hashes `LegalActionPage::schema_version`, carries `page_schema_version` through locators/receipts, and promotes serialized traces to `MTGSim.ActionTrace.v5` with `choice_page_schema=`.

## rev0103 — legal-action page count contract

The audit/refactor target was the page cardinality seam. rev0102 made pages schema-bound, but the exact-vs-lower-bound meaning of `actions_seen`, `complete`, and `next_cursor` still lived mostly in comments and caller convention.

rev0103 adds explicit count-contract fields to `LegalActionPage`, `LegalActionPageLocation`, action receipts, and `ActionTrace.v6`: `total_actions_lower_bound`, `total_actions_exact`, and `remaining_actions_lower_bound`. Page finalization now computes those fields in one place before hashing, and replay rejects count drift through `ChoicePageLocationMismatch` before mutation.

This does not add closed-form random access. It makes the current enumerator-backed knowledge honest and queryable, which is the right next step before building agent/search APIs on top of the legal-choice surface.


## rev0104 page context seal audit/refactor

rev0104 adds page context evidence to `LegalActionPage`, `LegalActionPageLocation`, action receipts, and `ActionTrace.v7`: the page `state_hash` and `choice_request_hash` now travel with the page proof itself. The refactor bumps the page schema to v3, folds the context into `legal_action_page_hash(...)`, validates receipt context against `state_hash_before`/`choice_request_hash`, and makes replay reject page-context drift through `ChoicePageLocationMismatch` before mutation.


## rev0106 — action trace page-proof sentinel

rev0106 audits the trace/receipt seam after the rev0104 context seal. The bug-shaped ambiguity was that `choice_page_found=false` overloaded two different meanings: a checked negative page-location proof versus no page proof checked at all for an illegal full-trace audit row.

The refactor adds `choice_page_location_checked` to action receipts and `expected_choice_page_location_checked` / `choice_page_checked=` to `ActionTrace.v8`. Legal applied actions must have a checked positive page proof; illegal attempts exported with `export_action_trace(game, false)` remain replayable without claiming page proof. Replay rejects applied-action proof elision as `ChoicePageLocationMismatch` before mutation, and receipt validation rejects legal receipts without checked page proof, illegal receipts with checked proof, or positive page locations that were not marked checked.

## rev0106 — page-location hash seal

rev0106 follows the rev0105 checked-proof sentinel by adding `LegalActionPageLocation.v1`, a compact hash over the full page-location tuple plus the selected action hash. This turns page proof from a collection of adjacent fields into a self-sealing record: replay and receipt validation can now reject a stale locator, page hash, count field, or selected-action hash before mutation.

## rev0107 — APNAP queue-entry hash seal

The page proof chain is now self-sealing, so rev0107 moves one boundary outward to the APNAP queue. Before this cut, the trace carried `choice_queue_hash`, `choice_queue_index`, and `choice_queue_size`, but not a compact proof that those fields still pointed at the same selected request/action pair.

rev0107 adds `ChoiceQueueLocation.v1`, `choice_queue_location_hash(...)`, receipt `choice_queue_location_hash`, and `ActionTrace.v10` `choice_queue_location_hash=` serialization. Receipt validation recomputes the seal from typed queue/request/action fields, and replay rejects queue-entry seal drift before StateCore mutation while preserving the more specific `ChoiceRequestHashMismatch` classification for local request-hash drift.

## rev0108 — APNAP queue proof sentinel

rev0108 mirrors the earlier page-proof sentinel at the APNAP queue boundary. rev0107 made queue-entry evidence self-sealing with `choice_queue_location_hash`, but the proof surface still inferred proof status from whether the hash was nonzero.

This cut adds explicit `choice_queue_location_checked` and `choice_queue_location_found` receipt fields plus `ActionTrace.v11` `choice_queue_checked=` / `choice_queue_found=` serialization. Legal applied transitions must carry checked and positive queue proof; illegal audit rows remain allowed to carry coarse queue metadata without claiming a checked proof. Replay rejects applied-action queue-proof elision before StateCore mutation, even when the compact hash itself still matches.

## rev0109 — APNAP queue-location schema evidence

rev0109 audits the proof-version seam left after the queue hash seal and checked/found sentinel. `ChoiceQueueLocation.v1` was present inside the hash domain, but the trace/receipt surface did not expose the queue-location schema the way page proof exposes `choice_page_schema`.

This cut adds `kChoiceQueueLocationSchemaVersion`, `ChoiceQueueLocation::schema_version`, receipt `choice_queue_location_schema_version`, and `ActionTrace.v12` `choice_queue_schema=` serialization. Replay rejects queue-location schema drift before mutation through the APNAP queue evidence channel, and receipt validation recomputes the compact queue-location hash from schema-bearing typed fields.


## rev0110 — canonical action schema seal

rev0110 audits the selected-action identity seam left after the page and APNAP queue proof schemas became explicit. `legal_action_hash(...)` already had a stable `MTGSim.Action.v1` hash domain, but receipts and traces did not expose that protocol version as typed replay evidence.

This cut adds `kLegalActionSchemaVersion`, receipt `action_schema_version`, `ActionTrace.v13` `action_schema=` serialization, and replay diagnostics for expected/actual action schema. Replay rejects action-schema drift before mutation through `ActionHashMismatch`, even when the compact action hash is otherwise current. Receipt validation also rejects unsupported action schema versions, and `tools/audit_datacube.py` now probes the selected-action schema seam directly.

## rev0111 — Choice request schema seal

rev0111 exposes the local offered-choice protocol version as first-class evidence. `ChoiceRequest` now carries `schema_version = kChoiceRequestSchemaVersion`, receipts persist `choice_request_schema_version`, and `ActionTrace.v14` serializes it as `choice_schema=` beside `choice_hash=`. Replay rejects schema drift through `ChoiceRequestHashMismatch` before StateCore or journal mutation, and receipt validation rejects unsupported choice request schema versions. The change keeps older v1-v13 traces parseable with a compatibility default while making new artifacts self-describing.


## rev0112 — Choice queue schema seal

rev0112 exposes the global APNAP `ChoiceRequestQueue` protocol version as first-class evidence. `ChoiceRequestQueue` now carries `schema_version = kChoiceRequestQueueSchemaVersion`, receipts persist `choice_queue_schema_version`, and `ActionTrace.v15` serializes it as `choice_queue_schema=` beside `choice_queue_hash=`, `choice_queue_index=`, and `choice_queue_size=`. Replay rejects queue schema drift through `ChoiceQueueHashMismatch` before StateCore or journal mutation, and receipt validation rejects unsupported choice queue schema versions. The trace parser preserves v12-v14 compatibility by treating their legacy `choice_queue_schema=` field as queue-location schema evidence, while v15 uses `choice_queue_location_schema=` for that narrower proof.

## rev0113 — State hash schema seal

rev0113 exposes the StateCore hash protocol version as first-class replay evidence. `kStateCoreSchemaVersion` now travels through `ActionReceiptRecord::state_schema_version`, receipt hashing, and `ActionTrace.v16` as `state_schema=` beside `state_before=` / `state_after=`. Replay rejects schema drift through `StateHashSchemaMismatch` before StateCore or journal mutation, and receipt validation rejects unsupported state schema versions. This keeps future StateCore hash-domain migration from collapsing into a generic state-content mismatch.


## rev0114 — replay artifact manifest schema seal

rev0114 audits the trust wrapper around persisted replay bundles. `ReplayArtifactManifest.v1` already bound snapshot text, trace text, checkpoint metadata, action count, final StateCore hash, and `bundle_hash`, but the manifest schema lived only in the header/hash-domain convention.

This cut promotes manifests to `ReplayArtifactManifest.v2`, adds `kReplayArtifactManifestSchemaVersion`, serializes `manifest_schema=2`, includes the schema in the manifest payload hash, and adds `ManifestSchemaMismatch` verification diagnostics. Historical v1 manifests remain parseable for diagnostics, while verification rejects unsupported manifest schemas before snapshot parsing or trace replay.

## rev0115 — checkpoint schema seal

rev0115 audits the starting-state replay guard after the replay manifest schema seal. The standalone `StateCheckpointSeal` text artifact now serializes as `MTGSim.StateCheckpointSeal.v2` and carries `checkpoint_schema=` so checkpoint protocol drift is typed rather than disguised as a checkpoint hash mismatch. `replay_action_trace_from_checkpoint(...)` rejects unsupported checkpoint schemas as `CheckpointSchemaMismatch` before StateCore, journal, or action-receipt mutation.

The same audit removed a duplicated `priority_player` read from the checkpoint snapshot reader, aligning the read path with the writer without changing the snapshot text surface.

## rev0118 — transition choice-proof spine

rev0118 audits the seam introduced by rev0117: `TransitionResult` could report `Committed` and name the causal receipt, but the selected-choice page proof and APNAP queue-entry proof were still mainly receipt surfaces. The refactor makes the transition result itself carry `LegalActionPageLocation`, `ChoiceQueueLocation`, checked/found sentinels, and `committed_with_choice_proofs()`, while preserving nonmutating rejection. The datacube audit now includes a `transition_result_wiring` probe that binds the public type, commit path, C++ regression, rules ledger, and architecture note together.
## rev0119 — transition staged commit spine

rev0119 audits the transition-result seam after rev0118's proof carrying. The remaining risk was that `commit_action_transition(...)` preflighted legally but then mutated the caller state directly; a future multi-phase action failure could leak partial StateCore or journal writes through a supposedly rejected transition. The refactor adds `ActionTransitionPreflight` / `preflight_action_transition(...)`, routes legacy and transition APIs through the shared preflight surface, and makes `commit_action_transition(...)` mutate a staged `GameState` copy before atomically adopting it. `TransitionResult` now carries staged commit sentinels plus `committed_with_staged_adoption()`, and the datacube audit probes that staged commit spine across code, tests, docs, and ledger.


## rev0122 — receipt journal alias seal

rev0122 audits the naming seam between `TransitionResult` and `ActionReceiptRecord`. rev0121 made `TransitionResult::journal_hash_after_action` and `TransitionResult::journal_entries_after_action` first-class, but the persisted receipt row still used the older `journal_hash_after` / `journal_entries_after` names for the same post-action/pre-receipt sample. The refactor adds explicit `ActionReceiptRecord` aliases, `ActionReceiptRecord::has_post_action_journal_seal()`, validator errors for post-action journal alias drift, and `test_action_receipt_post_action_journal_alias_is_validated`. This keeps `ActionTrace.v16` compatible while preventing the receipt row from blurring the action-body journal boundary with the final post-receipt journal hash.

## rev0123 — transition causal receipt hash

rev0123 audits the row-identity seam left after the receipt journal alias seal. `TransitionResult` could name the causal receipt index and check the staged receipt fields before adoption, but immediate callers still lacked a compact proof of the exact `ActionReceiptRecord` row that was inspected.

This cut adds `kActionReceiptRecordSchemaVersion`, public `action_receipt_hash(...)`, `TransitionResult::causal_receipt_hash`, and `committed_with_hashed_causal_receipt()`. `commit_action_transition(...)` samples the hash of the latest staged receipt before adoption, and `committed_with_atomic_adoption_guard()` now requires that hashed receipt contract alongside the existing staged/adoption, choice-proof, and post-action journal seals. Rejected transitions continue to carry no causal receipt hash.

## rev0124 — transition selected-action seal

rev0124 audits the selected-action handoff after the causal receipt hash. `TransitionResult` now carries a canonical `LegalAction action` in addition to its hash, and `commit_action_transition(...)` canonicalizes the caller action before preflight, staging, hashing, mutation, and receipt append. Display labels are stripped before they can become transition evidence; target vectors are normalized into the replay/audit shape.

The public `transition_result_matches_receipt(...)` verifier exposes the same receipt/result guard used before atomic staged adoption. It checks selected-action fields, action hash, StateCore hashes, choice-page proof, APNAP queue proof, post-action/pre-receipt journal seal, receipt index, and applied status. The new regression proves accepted label-only drift and rejected semantic action/receipt drift.

## rev0126 — transition boundary verifier

rev0126 audits the seam left after rev0125's checkpoint seals. The transition result had durable before/after checkpoint fields and a public receipt verifier, but callers still had to compose the full proposal/adoption check themselves. The refactor adds `verify_transition_result_boundary(...)`, which verifies `StateCheckpointSeal checkpoint_before` against the proposal state, `StateCheckpointSeal checkpoint_after` against the adopted or unchanged after state, and—only for committed transitions—the latest causal `ActionReceiptRecord` via `transition_result_matches_receipt(...)` plus `causal_receipt_hash`.

The verifier deliberately handles all three transition statuses: `NeedChoice` must be pure inspection with non-empty offered actions, `Rejected` must satisfy nonmutating checkpoint stability with zero causal receipt identity, and `Committed` must satisfy the existing atomic adoption guard plus latest-receipt/index/hash agreement. This keeps branch/search/agent callers from forgetting a proof surface when deciding whether a returned transition is trusted; for committed results, the after state is the adopted state.

## rev0128 — transition boundary diagnostics

rev0128 audits the usability seam left after the boundary seal. `verify_transition_result_boundary(...)` could reject invalid `TransitionResult` evidence, but replay, fuzz, search, and agent callers still had to reproduce the verifier if they needed to know which seam failed.

The refactor adds `TransitionBoundaryFailureKind`, `TransitionBoundaryVerifyResult`, and public `check_transition_result_boundary(...)`. The diagnostic verifier returns stable failure kinds for status drift, missing or stale `transition_boundary_hash`, before/after checkpoint mismatch, broken `NeedChoice`/`Rejected` nonmutation contracts, committed staged-adoption guard failure, and causal `ActionReceiptRecord` count/index/hash/payload mismatch. The legacy bool verifier now delegates to `check_transition_result_boundary(...).passed()`, so existing call sites remain compatible while richer callers get first-failure localization.

## rev0130 — transition trace handoff seal

rev0130 audits the seam between the committed `TransitionResult` and the replay-facing `ActionTraceEntry`. The transition boundary had already bound checkpoints, choice proofs, preflight evidence, causal receipt hashes, and selected-action evidence, but replay consumers still had to trust that the result projected to the same trace row that `export_action_trace(...)` would later emit.

This cut adds `kTransitionTraceHandoffSealSchemaVersion`, `transition_trace_handoff_hash`, `transition_result_trace_handoff_hash(...)`, `committed_with_trace_handoff_seal()`, `action_trace_entry_from_transition_result(...)`, `action_trace_entry_hash(...)`, and `transition_result_matches_action_trace_entry(...)`. `check_transition_result_boundary(...)` now reports `TraceHandoffSealMissing` and `TraceHandoffSealMismatch` with expected/observed trace handoff hashes. The refactor routes receipt export through `action_trace_entry_from_receipt_record(...)`, so the projected transition row and receipt-exported row share one mapping and one stable hash.

## rev0131 — transition trace-entry hash refactor

rev0131 audits the small but dangerous duplicate-hash seam inside the rev0130 transition trace handoff. The handoff seal already proved that a committed `TransitionResult` projects to an `ActionTraceEntry`, but its implementation re-listed the trace-entry hash fields instead of reusing the canonical `action_trace_entry_hash(...)` path.

This cut adds `transition_result_trace_entry_hash(...)` and routes `transition_result_trace_handoff_hash(...)` through that helper. The helper projects with `action_trace_entry_from_transition_result(...)` and then hashes with `action_trace_entry_hash(...)`, so receipt-exported traces, transition-projected traces, and transition handoff seals share one canonical trace-entry hash spine. `test_transition_trace_handoff_uses_canonical_trace_entry_hash` guards the refactor and proves maliciously resealed projection drift still fails boundary verification at the receipt/result seam.

## rev0132 — transition trace-entry seal

rev0132 audits the small handoff between a committed `TransitionResult` and the replay-facing `ActionTraceEntry` row it projects. rev0131 removed duplicate trace-entry hashing, but the result still required callers to recompute `transition_result_trace_entry_hash(...)` to know which replay row was being certified.

This cut adds `kActionTraceEntrySchemaVersion`, `action_trace_entry_schema_version`, `action_trace_entry_hash`, and `has_action_trace_entry_seal()` to `TransitionResult`. `commit_action_transition(...)` computes the carried seal before trace handoff and boundary sealing; `check_transition_result_boundary(...)` now reports `TraceEntrySealMissing` and `TraceEntrySealMismatch` with expected/observed trace-entry schema/hash echoes. The result is a first-class replay projection seal that fails before broader handoff or receipt/result diagnostics.

## rev0150 — paid action cost witness receipts

Audited the first seam left by rev0149's paid-action phase receipts: the phase named the cost window, but not every nonmana payment witness was first-class on the stack-placement receipt. Tap-cost activation payment still required an event scan, and loyalty counter payment was only implied by the event span.

The refactor adds `tap_cost_event_sequence` plus a paid-action counter-change range to `StackPlacementRecord`. Validation now rejects missing/wrong tap witnesses by source zone-change snapshot and missing/non-loyalty counter ranges for paid loyalty costs. The new audit probe keeps the field-level wiring connected across source, tests, docs, ledger, README, and changelog.

## rev0160 — Ability declaration/cost-lock audit

rev0160 audited the asymmetry left by the paid-action transaction work: paid spell casts had a `PaidActionDeclarationRecord`, while activated and loyalty ability transactions only sealed stack-placement/phase evidence. The refactor extends the declaration/cost-lock spine to stack-using abilities, adds ability-specific declaration fields, and changes validation so committed paid actions of all three modeled kinds must link to a declaration receipt.

The important reduction in inference debt is not another registry row. It is executable: `test_activated_ability_declaration_record_locks_costs_before_payment` proves target/ability/cost declaration comes after synthetic stack-object creation and choice locking but before mana/tap payment witnesses, and it proves tampered hash and self-consistent cost-flag drift are both rejected. Existing loyalty paid-phase coverage now checks that loyalty activation placement and transaction receipts seal the same declaration hash.

The remaining high-risk gap is rollback for failed ability activations that currently die in preflight. Future work should separate "invalid to attempt" from "legal to attempt but unpayable" and send the latter through the paid-action rollback receipt path.

## rev0166 — journalverifycli

- Audited the rev0165 journal export/access seam and found the next weak link: exported receipts were visible but not independently challengeable from the artifact text.
- Added a parser/verifier API and CLI roundtrip so `MTGSim.PaidActionTransactionJournal.v1` can reject tampered transaction hashes, committed declaration snapshot hashes, speculative rollback snapshot hashes, and state bindings.
- Refactored paid-mana committed/rollback fixture construction for reuse by future spell/ability/loyalty journal verifier coverage.
- Kept the work executable and narrow: no new registry taxonomy, only one architecture note and regenerated rule/audit evidence.

## rev0167 — journalpayloadseal

- Audited the rev0166 verifier and found a remaining artifact-level seam: single rows verified, but the header did not bind the ordered exported row payloads.
- Bumped newly emitted paid-action journals to `MTGSim.PaidActionTransactionJournal.v2` and added `record_payload_hash` over the ordered parsed transaction rows plus exported recomputed transaction/snapshot hashes.
- Refactored the journal parser to fail closed on unknown header fields, unknown record fields, unexpected snapshot-prefixed fields, and blank lines that could hide manual splicing or truncation.
- Extended the executable parser/verifier regression to reject tampered payload hashes and a mixed valid rollback row spliced under a committed journal header.

## rev0172 — pending trigger order choice

Audited the trigger-placement seam left by the earlier deterministic APNAP scaffold. The problem was not another missing registry row: a legal action could move pending triggers to the stack without carrying the player-selected ordering evidence that replay and receipts need.

The refactor splits pending-trigger ordering into reusable helpers for default ordering, APNAP-block validation, label generation, and bounded order-action generation. `ActionReceiptRecord` and `ActionTrace.v17` now preserve `trigger_order`, and validation rejects wrong-kind payloads, duplicates, invalid trigger references, and stack-order mismatches.

## rev0173 — target legality receipt

Audited the CR 608.2b target-resolution seam after rev0172. The engine already distinguished all-illegal and partially legal target sets, but the typed resolution record mostly preserved aggregate counts. That left replay/audit consumers to infer which target failed and whether the effect payload used the same late legality decision.

The refactor adds ordered `TargetResolutionCheckRecord` rows inside `StackResolutionRecord`, computes target legality once at the start of stack resolution, and sends only the derived legal-target vector to `apply_effect_payload(...)`. Validation now rejects tampered per-target legality receipts and count drift. The regression suite distinguishes graveyard-zone failure from blink identity failure and proves legal-target receipts snapshot battlefield state before a legal target is moved by lethal payload damage.

## rev0175 simultaneous SBA look-back batch

rev0175 fixes a simultaneous SBA/LKI hazard in the existing dies-trigger seam. `apply_state_based_actions(...)` now captures one pre-batch battlefield trigger-source snapshot before moving/destroying creatures for nonpositive-toughness or lethal-damage SBAs, then passes that snapshot through `move_object_with_precomputed_ltb_snapshots(...)` for every creature in the batch.

The important behavioral guarantee is narrow but substantive: when two creatures with creature-dies triggers die in the same SBA pass, each source can still see the other death even if one source has already been moved by the internal sequential movement loop. The public movement API remains stable; the new helper is internal evidence plumbing for simultaneous-batch callers, with the `pre_creature_sba_ltb_snapshots` variable naming the one shared pre-SBA snapshot.

This does not yet create a full event-batch record, nor does it cover every possible zone-change trigger form. It removes the highest-risk local bug: cross-dies trigger discovery no longer depends on the order in which the engine records simultaneous creature movements.

## rev0176 damageability gate

rev0176 fixes a concrete damage receipt bug: a plain artifact or other non-battle/non-creature/non-planeswalker battlefield object could previously receive a `DamageRecord` with positive `dealt` even though the engine had no legal damage result for that object type.

The refactor adds `DamageRecord::not_dealt`, `DamageRecord::target_was_damageable`, and `DamageRecord::damage_disallowed_by_target_type`. `deal_damage_to_target(...)` now gates object targets before applying protection/prevention; impossible target-type damage records all requested damage as `not_dealt`, leaves prevention shields unchanged, and produces no lifelink or deathtouch result. Validation rejects both accounting drift and old-style impossible object damage receipts.

## rev0177 damage counter-result links

rev0177 audits the receipt seam left after damageability and typed counter records. Planeswalker and battle damage already removed loyalty/defense counters through `CounterChangeRecord`, and `DamageRecord` already carried `counters_removed`, but those two facts were only correlated by event order and aggregate amount.

The refactor adds `first_damage_counter_change_record_index` and `damage_counter_change_record_count` to `DamageRecord`, snapshots the counter-change stream around planeswalker/battle damage, and validates that the linked rows are damage-result object removals for the same source, source zone-change identity, target object, counter kind, and sequence window. The focused regression proves loyalty and defense damage receipts reject missing counter ranges and source drift.

Audit probe anchor: damage counter-change.

## rev0183 — zone replacement chain seal

Audited the current zone-change replacement seam after the prevention/paid/fuzz hardening. The concrete risk was not missing doctrine; it was an endpoint-only validator that could accept malformed replacement chains whose second pass did not consume the first pass result, whose pass order drifted, or whose replacement row backlink named a movement that did not actually own the row.

The refactor keeps scope narrow and executable: `ZoneChangeRecord` validation now proves contiguous replacement-chain continuity, pass-index order, affected-player consistency, duplicate source/definition/LKI rejection, and backlink range ownership. The existing chain regression now corrupts each of those fields so future refactors fail closed.

### rev0184 audit-history compaction refactor

The final rev0184 datacube audit exposed a waste seam in `reports/audit/datacube_audit_history.jsonl`: compact history rows still copied full C++ case-name and scenario-name inventories, pushing the history file over the large-file review threshold. `tools/audit_datacube.py` now emits `mtgsim.datacube_audit_history.compact.v2` rows that preserve trend counts and revision-identity booleans while omitting heavy inventories. The existing local history was normalized to the recent compact trend window so future linked revisions do not carry multi-megabyte audit history bloat.


## rev0185 — SBA pass barrier

Audit/refactor focus: hidden Aura cleanup inside zone-change link clearing was too eager. Rev0185 makes `apply_state_based_actions` collect candidates at the pass boundary, adds `StateBasedActionRecord.check_index` alongside `pass_index` and `pass_candidate_count`, and validates pass monotonicity only within one SBA check. The cloudtainer fuzz run caught and corrected the first over-strict validator that treated pass indexes as globally monotonic across later priority checks.


## rev0187 — trigger target-choice seal

Audit/refactor focus: rev0186 prevented no-legal-choice targeted triggers from making targetless stack objects, but the long-lived `TriggerRecord` did not prove the target-choice payload after stack objects later resolved or cleared targets. Rev0187 adds `chosen_targets`, `legal_target_set_count`, `choice_target_set_hash`, `target_choice_recorded`, and `no_legal_choices` to the trigger record, plus validator failures for tampering and missing choice gates.

The datacube audit probe now checks this wiring across source, tests, docs, and the rules ledger so future trigger refactors cannot quietly drop the seal.

## rev0188 — trigger resolution backlink seal

This revision tightens the seam between trigger stack placement and ability resolution. `TriggerRecord::stack_resolution_record_index` links resolved triggered abilities to the exact `StackResolutionRecord` that performed CR 608-style late target checks and payload application, while `StackResolutionRecord::trigger_record_index` points back to the originating trigger row. The trigger row also mirrors `resolved_sequence`, `resolution_outcome`, and `resolved_effect_payload_applied` so branch/replay consumers can audit the result without chasing an ability object that has already ceased to exist.

The refactor also teaches the EventRecord validator that `trigger_record_index` is an auxiliary link only on `EventRecordKind::StackResolution`; all other typed event rows still obey the exactly-one-primary-payload rule.



## rev0191 audit/refactor note — discard-cost payment receipt

Refactored the datacube wiring probe from the rev0190 sacrifice-only transaction receipt to the new discard-cost payment receipt path. The audit now requires `PaidActionTransactionJournal.v6`, `DiscardCostPaymentRecord`, discard payment range/hash fields, validator diagnostics for declaration/transaction/payment drift, focused C++ tamper tests, and this ledger/doc surface. This keeps the audit useful as a guardrail over executable semantics instead of adding another passive registry.

## rev0193 — Life Cost Receipt Spine

Refactored the datacube wiring probe from the rev0192 tap-cost receipt path to the new life-cost payment receipt path. The audit now requires `LifeCostPaymentRecord`, `PaidActionTransactionJournal.v7`, life payment range/hash fields, validator diagnostics for declaration/transaction/payment drift, focused C++ tamper coverage, and scenario DSL support for `life_cost=` / `:life=N`. This keeps the pass code-first: paying life as a locked cost is now distinguishable from damage or ordinary effect-driven life loss.

## rev0194 — Loyalty Cost Receipt Spine

Refactored the datacube wiring probe from the rev0193 life-cost receipt path to the new loyalty-cost payment receipt path. The audit now requires `LoyaltyCostPaymentRecord`, `PaidActionTransactionJournal.v8`, loyalty payment range/hash fields, validator diagnostics for counter-change/event/transaction drift, and focused C++ tamper coverage. This is a risk-bearing semantic change: loyalty costs are no longer inferred from a generic paid-action counter-change span.

## rev0195 — Return Cost Receipt Gate

Refactored the datacube wiring probe from the rev0194 loyalty-cost receipt path to the new return-to-hand cost receipt path. The audit now requires `ReturnCostPaymentRecord`, `PaidActionTransactionJournal.v9`, return payment range/hash fields, validator diagnostics for zone-change/event/transaction drift, and focused C++ tamper coverage. This is a risk-bearing semantic change: return-to-hand costs are no longer inferred from generic battlefield-to-hand movement during a paid-action window.
