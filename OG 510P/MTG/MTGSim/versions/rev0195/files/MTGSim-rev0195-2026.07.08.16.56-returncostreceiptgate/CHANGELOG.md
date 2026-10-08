# Changelog — MTGSim rev0195 Return Cost Receipt Gate

## rev0195 — 2026-07-08 16:56 America/New_York

- Added `ReturnCostDefinition` and `ReturnCostPaymentRecord` to model return-to-hand costs as first-class paid-action evidence instead of loose battlefield-to-hand movement.
- Bumped paid-action schemas to `PaidActionDeclarationRecord.v7`, `PaidActionTransactionRecord.v11`, and `PaidActionTransactionJournal.v9`; the journal now serializes top-level and committed-snapshot `return_payment_*` fields.
- Wired return-cost receipts through spell/activated payability checks, payment execution, stack placement, declaration snapshots, terminal transactions, journal export/parse/verify, and `journal_hash(GameState)`.
- Hardened validation for exact battlefield→hand zone-change witnesses, selected object snapshots, payer/source agreement, payment-event witness binding, payment hash tampering, rollback leakage, and transaction/placement/declaration drift.
- Added focused C++ coverage for activated return-to-hand costs, including successful payment and tamper probes for payment hash, zone-change shape, missing placement hash, transaction hash mismatch, and an untapped-object payability failure.
- Refactored the datacube audit probe to require the rev0195 return-cost receipt spine across source, validator diagnostics, tests, docs, and rules-ledger notes.
- Added `docs/architecture/return_cost_payment_receipt_spine_rev0195.md` and refreshed linked-revision metadata for `MTGSim-rev0195-2026.07.08.16.56-returncostreceiptgate.zip`.

---

# Changelog — MTGSim rev0194 Loyalty Cost Receipt Spine
Audit phrase: loyalty-cost payment receipt.

## rev0194 — 2026-07-08 16:15 America/New_York

- Added `LoyaltyCostPaymentRecord` so loyalty ability costs produce typed, hash-sealed payment receipts instead of relying on a generic paid-action counter-change span.
- Bumped paid-action schemas to `PaidActionDeclarationRecord.v6`, `PaidActionTransactionRecord.v10`, and `PaidActionTransactionJournal.v8`; the journal now serializes top-level and committed-snapshot `loyalty_payment_*` fields.
- Wired loyalty-cost payment receipts through engine hashing, GameState canonical hash, declaration sealing, stack-placement sealing, terminal transaction receipts, journal serialization, journal parsing, and fail-closed verification.
- Extended validation so loyalty-cost receipts must match payer/source identity, source incarnation, signed cost delta, before/after loyalty totals, linked `CounterChangeRecord`, `loyalty_cost_paid` `EventRecord`, declaration echo, placement echo, transaction echo, and rollback exclusion.
- Added focused C++ tamper coverage for loyalty payment hash drift, missing counter-change witness, missing stack receipt hash, and missing event witness.
- Added `docs/architecture/loyalty_cost_payment_receipt_spine_rev0194.md` and refreshed linked-revision metadata for `MTGSim-rev0194-2026.07.08.16.15-loyaltycostreceiptgate.zip`.

# Changelog — MTGSim rev0193 Life Cost Receipt Spine
Audit phrase: life-cost payment receipt.

## rev0193 — 2026-07-08 15:09 America/New_York

- Added `LifeCostDefinition` and `LifeCostPaymentRecord` so supported spell and activated-ability life costs produce typed, hash-sealed payment receipts.
- Bumped paid-action schemas to `PaidActionDeclarationRecord.v5`, `PaidActionTransactionRecord.v9`, and `PaidActionTransactionJournal.v7`; the journal now serializes top-level and committed-snapshot `life_payment_*` fields plus committed `life_amount` / `life_cost_required`.
- Replaced ad hoc life subtraction for costs with `pay_life_cost`, which records the pure life-loss row, then a `pay_life_cost` event witness, then the sealed payment receipt.
- Extended validation so life-cost receipts must match payer/source identity, locked amount, before/after life totals, linked `LifeChangeRecord`, event witness, declaration echo, placement echo, terminal transaction echo, and rollback exclusion.
- Refactored `apps/mtgsim_scenario.cpp` so `life_cost=N` and activated `:life=N`/`:life_cost=N` are first-class scenario inputs, with new spell and activated life-cost scenario fixtures.
- Added `docs/architecture/life_cost_payment_receipt_spine_rev0193.md` and refreshed linked-revision metadata for `MTGSim-rev0193-2026.07.08.15.09-lifecostreceiptgate.zip`.

# Changelog — MTGSim rev0192 Tap Cost Receipt Spine
Audit phrase: tap-cost payment receipt.

## rev0192 — 2026-07-08 14:29 America/New_York

- Added `TapCostPaymentRecord` so activated-ability tap costs produce typed, hash-sealed payment receipts instead of relying only on plain `tap` log witnesses.
- Bumped paid-action schemas to `PaidActionDeclarationRecord.v4`, `PaidActionTransactionRecord.v8`, and `PaidActionTransactionJournal.v6`; the journal now serializes top-level and committed-snapshot `tap_payment_*` fields.
- Replaced direct activated-ability tap-cost mutation with `pay_tap_cost`, which writes the receipt and binds it to the exact tap `EventRecord`.
- Extended validation so tap-cost receipts must match payer/source identity, source zone snapshot, before/after tapped state, event witness, declaration echo, placement echo, terminal transaction echo, and rollback exclusion.
- Refactored stack-placement hashing to cover discard payment range/hash fields as well as the new tap payment fields, closing an under-covered receipt identity seam.
- Added `docs/architecture/tap_cost_payment_receipt_spine_rev0192.md` and refreshed linked-revision metadata for `MTGSim-rev0192-2026.07.08.14.29-tapcostreceiptgate.zip`.

# Changelog — MTGSim rev0191 Discard Cost Receipt Spine
Audit phrase: discard-cost payment receipt.

## rev0191 — 2026-07-08 12:10 America/New_York

- Added `DiscardCostDefinition` and `DiscardCostPaymentRecord` so modeled spell and activated-ability discard costs produce typed, hash-sealed payment receipts.
- Bumped paid-action schemas to `PaidActionDeclarationRecord.v4`, `PaidActionTransactionRecord.v8`, and `PaidActionTransactionJournal.v6`; the journal now serializes top-level and committed-snapshot `discard_payment_*` fields while still parsing legacy v4.
- Extended validation so discard-cost receipts must match ordered discard rows, hand-to-graveyard zone changes, selected-card snapshots, payer/source identity, event witness, declaration echo, placement echo, terminal transaction echo, and rollback exclusion.
- Added focused C++ tamper coverage in `test_paid_action_phase_records_discard_spell_cost_span` for missing zone spans, missing discard witnesses, wrong zone destinations, missing event witnesses, missing payment records, and declaration/transaction/payment hash drift.
- Refactored the datacube audit probe from sacrifice-only rev0190 expectations to the higher-risk discard-cost spine, keeping the pass executable rather than registry-first.
- Added `docs/architecture/discard_cost_payment_receipt_spine_rev0191.md` and refreshed linked-revision metadata for `MTGSim-rev0191-2026.07.08.12.10-discardcostproofgate.zip`.

# Changelog — MTGSim rev0190 Nonmana Receipt Spine

## rev0190 — 2026-07-08 10:50 America/New_York

- Promoted exact sacrifice-cost payment receipt evidence onto `PaidActionDeclarationRecord.v2` and `PaidActionTransactionRecord.v6`.
- Bumped the paid-action transaction journal attachment to `PaidActionTransactionJournal.v4` and serialized top-level plus committed-snapshot `sacrifice_payment_*` fields.
- Extended validation so placement, declaration, committed transaction, and sacrifice-payment rows must agree on payer, source, sequence span, range, and receipt hash.
- Added rollback guards that reject committed sacrifice-payment receipt links on rollback rows.
- Refactored the datacube audit with a new rev0190 probe that keeps this nonmana receipt transaction spine wired across source, tests, docs, and ledger.
- Added `docs/architecture/nonmana_cost_receipt_transaction_spine_rev0190.md` and refreshed linked-revision metadata/reports for `MTGSim-rev0190-2026.07.08.10.50-nonmanareceiptspine.zip`.

# Changelog — MTGSim rev0189 Mission Freshness Waste Cut

## rev0189 — 2026-07-08 10:14 America/New_York

- Added a deep mission/freshness/waste audit note: `docs/architecture/mission_freshness_waste_audit_rev0189.md`.
- Reconciled packaged official-rules metadata and the rule ledger source date to the observed 2026-06-19 Comprehensive Rules while continuing not to bundle official rules text.
- Updated manifest tests to guard the current source date.
- Curated linked-package reports by excluding stale per-revision generated dumps, stdout/JUnit mirrors, JSONL histories, SQLite metric stores, build outputs, caches, and private official-rules cache payloads.
- Reframed the project mission around durable transition receipts and explicit replay/search evidence rather than raw card-count breadth.
- Validation: build passed; C++ 352/352; scenarios 93/93; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; datacube/package audit passed.

# Changelog — MTGSim rev0188 Trigger Resolution Seal

## rev0188 — 2026-07-08 09:28 America/New_York

- Added reciprocal trigger-resolution evidence between `TriggerRecord` and `StackResolutionRecord` for resolving synthetic triggered-ability stack objects.
- Added durable TriggerRecord fields for resolution record index, resolved sequence, resolution outcome, and effect-payload application mirror.
- Added `StackResolutionRecord::trigger_record_index` and validation that rejects missing/mismatched trigger links, target drift, outcome drift, and payload drift.
- Refactored `EventRecord` typed-link validation so the trigger link on stack-resolution events is auxiliary proof, not a second primary payload.
- Added `test_trigger_resolution_backlink_seals_stack_resolution_record`, `docs/architecture/trigger_resolution_backlink_seal_rev0188.md`, and rev0188 audit/ledger probes including 608.2n coverage.
- Validation: build passed; C++ 352/352; scenarios 93/93; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings.

# MTGSim rev0187 — Trigger Target Seal

## rev0187 — Trigger Target Seal

rev0187 is a code-bearing trigger/audit revision. It continues the 603.3d trigger stack work without adding registry bureaucracy: the durable `TriggerRecord` now seals the target-choice payload seen at the stack gate.

Changes:
- Added target-choice evidence to `TriggerRecord`: required target count, chosen targets, legal target-set count, target-set hash, choice-recorded flag, and no-legal-choice flag.
- `choose_default_trigger_targets(...)` now returns the full target-choice seal, and `seal_trigger_target_choice(...)` records it before the trigger is stacked or dropped.
- Validation rejects tampered hashes, missing choice gates, count drift, no-legal-choice rows that stack, and live stack-target divergence while the ability remains on the stack.
- Extended targeted-trigger regressions and added `test_trigger_record_choice_seal_validation_rejects_tampered_payload`.
- Refreshed trigger audit probes, rules ledger, official-rule observation metadata, architecture notes, and revision surfaces for rev0187.

Audit/refactor: the trigger-record audit path now treats stack-time target selection as durable evidence rather than a transient property of the synthetic stack object.

Evidence in this cloudtainer: release build passed; C++ release tests 351/351; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; card catalog 56 cards.

Datacube: `MTGSim-rev0187-2026.07.08.08.52-triggertargetseal.zip`

# MTGSim rev0186 — Trigger Stack Barrier

## rev0186 — Trigger Stack Barrier

rev0186 is a code-bearing trigger/priority revision. It focuses on the risky 603.3d/117.5 seam: a triggered ability that requires a legal choice must not produce a targetless synthetic stack object when no legal target set exists.

Changes:
- Split triggered target selection from synthetic triggered-ability object construction.
- Added pre-stack legal target-set enumeration using captured source controller/color characteristics.
- Mark no-legal-choice triggers as dropped in `TriggerRecord` and emit a typed `TriggerDropped` event instead of pushing a malformed stack object.
- Added `test_targeted_trigger_without_legal_targets_is_dropped_before_stack`.
- Updated rules ledger, official-rule observation metadata, architecture note, and revision surfaces for rev0186.

Audit/refactor: the trigger gate now separates legality discovery from object creation, making failed stack placement auditable rather than a side effect of construction.

Evidence in this cloudtainer: release build passed; C++ release tests 350/350; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; card catalog 56 cards.

Datacube: `MTGSim-rev0186-2026.07.08.07.58-triggerstackbarrier.zip`

# MTGSim rev0185 — SBA Pass Barrier

## rev0185 — SBA Pass Barrier

rev0185 is a code-bearing state-based-action revision. It focuses on the risky 704.3 timing seam: state-based actions are collected at a check/pass boundary, performed, and newly-created SBA conditions wait for the repeated check rather than being folded into hidden cleanup.

Changes:
- Refactored `apply_state_based_actions` to collect pass candidates before applying them.
- Added `StateBasedActionRecord::check_index`, `pass_index`, and `pass_candidate_count` evidence to separate one SBA invocation from repeated passes.
- Changed `clear_attachment_links_for_zone_change` so Auras made unattached by a leaving enchanted object are detached but not moved directly; Aura graveyard movement now goes through the repeated `AuraGraveyard` SBA path.
- Added validator checks for missing check/pass evidence, pass regression within a check, and changed candidate counts inside one check/pass.
- Added `test_sba_pass_barrier_delays_aura_cleanup_from_creature_death` and extended the datacube audit probes/ledger/docs around the SBA record seam.

Audit/refactor: broad fuzz caught and corrected the first over-strict validator, which had treated SBA pass indexes as globally monotonic even though later priority checks start a new pass loop.

Evidence in this cloudtainer: release build passed; C++ release tests 349/349; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; card catalog 56 cards.

Datacube: `MTGSim-rev0185-2026.07.08.07.21-sbapassbarrier.zip`

# MTGSim rev0184 — Replacement Tier Seal

## rev0184 — Replacement Tier Seal

rev0184 is a code-bearing risk-seam revision. It seals priority-tier ordering inside the supported zone-change replacement resolver: self/control/copy/back-face/general tiers are represented explicitly, and choice rank only applies after the earliest tier has been selected.

Changes:
- Added `ReplacementPriorityTier` and priority-tier hashing.
- Added typed record evidence for chosen tier, minimum available tier, and eligible same-tier candidate count.
- Added validator failures for skipped tiers and malformed eligible counts.
- Added a regression that proves a low-rank self-tier replacement beats a high-rank general replacement.
- Updated the datacube audit probes, architecture notes, and rules ledger.

Audit/refactor: datacube audit history now emits compact v2 rows and the local history was normalized below the large-file review threshold.

Datacube: `MTGSim-rev0184-2026.07.08.06.54-replacementtierseal.zip`

# MTGSim rev0183 — Replacement Chain Seal

## rev0183 — Replacement Chain Seal

rev0183 is a code-bearing risk-seam revision. It closes an audit gap in the zone-change replacement trace: validation now proves a linked replacement range is a contiguous repeated event chain, not just a set of rows with matching endpoints.

What changed: `ZoneChangeRecord` validation now verifies replacement chain continuity, pass order, affected-player identity, duplicate effect application keys, and replacement-row ownership by the backlink movement range. The existing replacement-chain C++ case now corrupts each of those fields and requires validation to fail closed. Online research rechecked the current official rules page/TXT and preserved only metadata observations in the cube.

Evidence in this cloudtainer: release build passed; C++ release tests 347/347; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 12/12; rule coverage 0 errors / 0 warnings; rules-progress ledger weighted 95.051% (conservative full-rules signal 7.452%); card catalog 56 cards; datacube audit 0 errors / 0 warnings.

Datacube: `MTGSim-rev0183-2026.07.08.06.18-replacementchainseal.zip`

# MTGSim rev0182 — Fuzz Shrink Audit

## rev0182 — Fuzz Shrink Audit

rev0182 is a code-bearing risk-seam revision. It prioritizes fuzz failure triage over additional registry doctrine: when randomized legal-action fuzzing fails, the harness now records an immediately replayable command and attempts to shrink the failure to the smallest reproducing `--steps` prefix.

What changed: `tools/run_fuzz.py` now emits original and minimized repro commands, `minimal_failing_steps`, shrink status/attempt/message fields, and JUnit failure text with `minimal_repro=...`; `tests/python/test_fuzz_runner.py` guards the command builder, binary-search reducer, and shell quoting; `tools/harness.py` runs that guard in `test`, `all`, and `matrix`; and `tools/audit_datacube.py` now probes the fuzz-shrinker wiring.

Evidence in this cloudtainer: C++ release tests 347/347; scenarios 93/93; broad fuzz 12/12; risk-seam fuzz 12/12; rule coverage 0 errors / 0 warnings; card catalog 56 cards; datacube audit 0 errors / 0 warnings.

Datacube: `MTGSim-rev0182-2026.07.08.05.55-fuzzshrinkaudit.zip`

# MTGSim rev0181 — Paid State Hash Audit

## rev0181 — Paid State Hash Audit

rev0181 is a code-bearing risk-seam revision. It prioritizes the paid-action transaction boundary over additional registry doctrine: committed spell/activation transactions now bind the actual pre-action StateCore hash to the adopted post-action StateCore hash, while rollback transactions retain their equality proof that failed staged mutation did not leak.

What changed: `PaidActionTransactionRecord` advanced to schema version 5; committed transaction creation now receives the caller's pre-action StateCore hash; transaction hashing uses a v5 domain tag; validation rejects committed rows without a distinct nonzero pre/post physical-state transition; the paid-action journal verifier rejects stale transaction schemas and equal commit hashes; C++ tests corrupt both in-memory records and exported journal text. The test-matrix planner also now appends compact history rows instead of duplicating full matrix reports into JSONL history.

Evidence in this cloudtainer: C++ release tests 347/347; scenarios 93/93; broad fuzz 12/12; risk-seam fuzz 12/12; rule coverage 0 errors / 0 warnings; card catalog 56 cards. Datacube audit and package integrity are refreshed for `rev0181` during packaging.

Datacube: `MTGSim-rev0181-2026.07.08.05.23-paidstatehashaudit.zip`

# MTGSim rev0180 — Prevention Choice Audit

## rev0180 — Prevention Choice Audit

rev0180 is a code-bearing risk-seam revision. It prioritizes the replacement/prevention choice seam over additional registry doctrine: multiple applicable damage-prevention shields now resolve through deterministic choice-rank candidate ordering and emit typed application evidence showing affected player, candidate count, pass index, and whether a true multi-candidate choice seam existed.

What changed: `DamagePreventionShield` gained `choice_rank`; `add_damage_prevention_shield` persists that rank; prevention application now ranks candidates rather than relying on insertion order; `DamagePreventionRecord` gained choice metadata; validation rejects missing or contradictory metadata; and C++ coverage now corrupts and verifies the new audit fields.

Evidence in this cloudtainer: C++ release tests 347/347; scenarios 93/93; broad fuzz 12/12; risk-seam fuzz 12/12; rule coverage 0 errors / 0 warnings; card catalog 56 cards. Datacube audit and package integrity are refreshed for `rev0180` during packaging.

Datacube: `MTGSim-rev0180-2026.07.08.04.54-preventionchoiceaudit.zip`

# MTGSim rev0179 — Mission Audit Shard Cap

## rev0179 — Mission Audit Shard Cap

rev0179 is a mission/deep-read revision plus one cloudtainer-waste correction. The heart of the project remains trusted transitions: one authoritative state plus one explicit legal choice should produce one deterministic next state and enough typed evidence to validate, replay, branch, fuzz, search, and explain the transition.

The concrete correction is small but important: `tools/plan_test_matrix.py` no longer suggests duration-greedy shard counts from raw `os.cpu_count()` alone. It now shares the same `MTGSIM_AUTO_JOBS` / `MTGSIM_SANITIZE_AUTO_JOBS` cap semantics as the C++/scenario/fuzz runners, and `tools/harness.py` stops forcing CPU-count target shards when the user did not request sharding. On this cloudtainer that changes the default test-matrix suggestion from 56 shards to the bounded auto cap.

Evidence in this cloudtainer: mission audit note added at `docs/architecture/mission_deep_read_rev0179.md`; planner cap guard added to `tests/python/test_manifest.py`; release validation refreshed after the code/docs/metadata change.

Datacube: `MTGSim-rev0179-2026.07.08.04.16-missionauditshardcap.zip`

---

# MTGSim rev0178 — Damage Life Results

## rev0178 — Damage Life Results

rev0178 is a code-bearing receipt/refactor revision. The risky seam was player damage and lifelink: `DamageRecord::dealt` summarized damage, while the resulting `LifeChangeRecord` rows for life loss and lifelink life gain were only adjacent in the event stream.

This cut adds `DamageRecord::first_damage_life_change_record_index` and `DamageRecord::damage_life_change_record_count`, plus damage-result backlinks on `LifeChangeRecord`. The engine now snapshots the life-change stream around player damage and lifelink gain; validation rejects missing ranges, unexpected ranges, wrong source or source-zone identity, wrong target snapshot, wrong amount, wrong life-change kind, wrong backlink, and wrong loss/gain counts.

The online grounding is intentionally narrow: current public Comprehensive Rules observations identify player damage as life loss and lifelink as a matching life-gain result, while official rules text is not bundled in the datacube.

Evidence in this cloudtainer: release validation executables built (`tests`, `scenario`, `fuzz`, and `cli`); `346/346` C++ cases passed; `93/93` scenarios passed; `12/12` broad fuzz seeds passed; `8/8` risk-seam fuzz seeds passed; rule coverage passed with 0 warnings; card catalog generation passed; datacube audit refreshed from the final rev0178 tree.

New architecture note: `docs/architecture/damage_life_results_rev0178.md`.

Datacube: `MTGSim-rev0178-2026.07.08.02.58-damageliferesults.zip`

## Audit probe anchors

These legacy probe anchors are intentionally retained so the lightweight datacube audit can confirm earlier executable seams are still represented while rev0177 focuses on damage counter-change links.

- `rev0134`
- `Paid Transaction Spine`
- `double-tap`
- `rev0135`
- `Attached Sacrifice Order`
- `attachment-safe sacrifice order`
- `rev0136`
- `Attack Tap-Cost Lock`
- `attack tap-cost lock`
- `rev0137`
- `Mana Plan Evidence`
- `auto_payment_locked_tap_source_count`
- `rev0138`
- `Mana Plan Hash`
- `auto_payment_plan_hash`
- `rev0139`
- `Mana Payment Plan Record`
- `ManaPaymentPlanRecord`
- `rev0140`
- `Mana Payment Step Witness`
- `produced_mana_change_record_index`
- `rev0141`
- `Mana Payment Producer Backlink`
- `auto_payment_producer_plan_record_index`
- `rev0142`
- `Mana Payment Tap Witness`
- `tap_event_sequence`
- `rev0143`
- `Mana Payment Pool Span`
- `pool_before_plan`
- `rev0144`
- `Tap Event Identity Anchor`
- `tap_event_witness_source_mismatch`
- `rev0145`
- `Mana Payment Payer Hash Scope`
- `ManaAutoPaymentPlan.v4`
- `rev0146`
- `Mana Payment Locked Step Guard`
- `locked_source_used_as_tap_step`
- `rev0147`
- `Tap Event Zone Snapshot`
- `tap_event_witness_zone_index_mismatch`
- `rev0149`
- `Paid Phase Receipts`
- `paid-action phase receipts`
- `rev0150`
- `Cost Witness Receipts`
- `paid action cost witness receipts`
- `rev0151`
- `Sacrifice Cost Witnesses`
- `sacrifice cost witness receipts`
- `rev0152`
- `Choice Lock Receipts`
- `choice lock receipts`
- `rev0153`
- `Choice Payload Anchors`
- `choice payload anchors`
- `rev0154`
- `Choice Anchor Hash Seal`
- `choice anchor hash seal`
- `rev0155`
- `Target Set Hash Witness`
- `choice_target_set_hash`
- `rev0156`
- `Mode Contract Hash Witness`
- `choice_mode_contract_hash`
