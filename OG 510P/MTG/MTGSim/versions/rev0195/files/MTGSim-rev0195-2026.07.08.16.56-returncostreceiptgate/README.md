# MTGSim rev0195 — Return Cost Receipt Gate

Current linked revision: `MTGSim-rev0195-2026.07.08.16.56-returncostreceiptgate.zip`.

rev0195 is a code-bearing risk-seam pass, not a registry pass. It extends the typed paid-action receipt spine to return-to-hand costs: `ReturnCostPaymentRecord` now seals the payer, source object, locked return-cost definition, exact selected objects, selected pre-payment zone snapshots, battlefield→hand `ZoneChangeRecord` witness range, `pay_return_cost` event witness, and stable payment hash. The declaration, stack placement, committed transaction, committed declaration snapshot, and `PaidActionTransactionJournal.v9` must now agree on the return-cost receipt.

Validation snapshot from the rev0195 tree: release C++ tests passed 355/355, CTest passed 59/59, scenarios passed 95/95, broad fuzz passed 12/12, risk-seam fuzz passed 8/8, rule coverage reported 0 errors / 0 warnings, card catalog generation passed, and matrix planning refreshed 355 C++ cases / 95 scenarios / 462 work units.

---

# MTGSim rev0194 — Loyalty Cost Receipt Spine

Current linked revision: `MTGSim-rev0194-2026.07.08.16.15-loyaltycostreceiptgate.zip`.

rev0194 is a code-bearing risk-seam pass. It extends the typed paid-action receipt spine to loyalty costs: `LoyaltyCostPaymentRecord` now seals the payer, planeswalker source, source zone-change snapshot, signed loyalty-cost delta, before/after loyalty totals, exact `CounterChangeRecord` row, `loyalty_cost_paid` event witness, and stable payment hash. The declaration, stack placement, terminal transaction, committed declaration snapshot, and `PaidActionTransactionJournal.v8` must now agree on that typed receipt.

Audit/refactor focus: `tools/audit_datacube.py` now probes the loyalty-cost receipt spine across schemas, engine accessors, serialization/parsing, validator diagnostics, C++ tamper tests, docs, and the rules ledger. This pass converts loyalty payment from a generic counter-change inference into explicit transaction evidence.

Validation snapshot from the rev0194 tree: release C++ tests passed 354/354 after the new loyalty-cost receipt regression and journal v8 parser update. Full report paths are emitted under `reports/*/*rev0194_latest*` after the package refresh.

# MTGSim rev0193 — Life Cost Receipt Spine

Current linked revision: `MTGSim-rev0193-2026.07.08.15.09-lifecostreceiptgate.zip`.

rev0193 is a code-bearing risk-seam pass. It extends the paid-action receipt spine from sacrifice/discard/tap costs to life-as-cost: `LifeCostPaymentRecord` now seals the payer, source object, locked amount, before/after life totals, linked pure life-loss row, exact `pay_life_cost` event witness, and stable payment hash. The declaration, stack placement, terminal transaction, and `PaidActionTransactionJournal.v7` must now agree on that typed receipt.

Audit/refactor focus: the scenario DSL now accepts `life_cost=N` and activated `:life=N`/`:life_cost=N`, so executable fixtures can cover life-cost semantics directly instead of only through C++ helper construction. `tools/audit_datacube.py` was refreshed to probe the life-cost receipt spine across schemas, engine accessors, serialization, validator diagnostics, C++ tamper tests, scenario fixtures, docs, and the rules ledger.

Validation snapshot from the rev0193 tree: release C++ tests passed with the new life-cost regression; scenario CTest passed 48/48 including the new spell and activated life-cost scenarios. Full report paths are emitted under `reports/*/*rev0193_latest*`.

# MTGSim rev0192 — Tap Cost Receipt Spine

Current linked revision: `MTGSim-rev0192-2026.07.08.14.29-tapcostreceiptgate.zip`.

rev0192 is a code-bearing risk-seam pass. It extends the paid-action nonmana receipt spine from sacrifice/discard costs to tap-as-cost: `TapCostPaymentRecord` now seals the payer, source object, source zone-change snapshot, before/after tapped flags, exact tap `EventRecord` witness, and stable payment hash. The declaration, stack placement, terminal transaction, and `PaidActionTransactionJournal.v6` must now agree on that typed receipt.

Audit/refactor focus: `tools/audit_datacube.py` now probes the tap/discard nonmana receipt spine across source, validator, focused C++ tamper tests, docs, and the rules ledger. The source refactor also closes a hash-coverage gap by sealing discard payment fields into the stack-placement identity alongside the new tap payment fields.

Validation snapshot from the rev0192 tree: release build and focused tap-cost regression passed during the linked-package refresh; full report paths are emitted under `reports/*/*rev0192_latest*`.

# MTGSim rev0191 — Discard Cost Receipt Spine

Current linked revision: `MTGSim-rev0191-2026.07.08.12.10-discardcostproofgate.zip`.

rev0191 is a code-bearing risk-seam pass. It extends the rev0190 nonmana payment spine from sacrifice-only receipts to discard-as-cost: `DiscardCostPaymentRecord` now seals selected hand cards, pre-payment zone snapshots, exact `DiscardRecord` rows, hand-to-graveyard `ZoneChangeRecord` rows, and the summary `pay_discard_cost` event. The declaration, stack placement, terminal transaction, and `PaidActionTransactionJournal.v6` must now agree on that typed receipt.

Audit/refactor focus: `tools/audit_datacube.py` now probes the v5 discard-cost spine across source, validator, focused C++ tamper tests, docs, and the rules ledger. This keeps the project moving through executable cost-payment semantics rather than adding registry breadth.

Validation snapshot from the rev0191 tree: release build and focused discard-cost regression passed before the full linked-package harness refresh; full report paths are emitted under `reports/*/*rev0191_latest*`.

# MTGSim rev0190 — Nonmana Receipt Spine

Current linked revision: `MTGSim-rev0190-2026.07.08.10.50-nonmanareceiptspine.zip`.

rev0190 is a code-bearing risk-seam pass, not another registry/doctrine pass. It promotes exact typed sacrifice-cost payment receipts from stack-placement-only evidence into the paid-action declaration and committed transaction rows, then emits them in `PaidActionTransactionJournal.v4`. The goal is to make nonmana cost payment auditable from the transaction spine itself: an auditor no longer has to infer the sacrifice payment from the broader paid-action zone-change span.

Validation snapshot from the rev0190 tree: release build and CTest are green; focused C++ regressions now check declaration, transaction, serialized journal, and validator-tamper paths for sacrifice-cost payment receipt drift. Full harness reports are refreshed under `reports/*/*rev0190_latest*`.

# MTGSim rev0189 — Mission Freshness Waste Cut

Current linked revision: `MTGSim-rev0189-2026.07.08.10.14-missionfreshnesswastecut.zip`.

rev0189 is a deep mission/freshness/waste revision. Its thesis: MTGSim's heart is not raw card-count breadth; it is deterministic Magic transitions with durable, typed evidence that can be validated, replayed, branched, fuzzed, searched, and explained. This cut reconciles the packaged Comprehensive Rules source metadata to the observed 2026-06-19 official source date, adds `docs/architecture/mission_freshness_waste_audit_rev0189.md`, and teaches the package helper to leave stale generated report histories, stdout/JUnit mirrors, SQLite metric stores, and older per-revision dumps in the cloud container instead of copying them into every linked zip.

Validation snapshot from the rev0189 tree: release build passed; C++ release tests 352/352; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; datacube audit passed after package hygiene; card catalog 56 cards.

# MTGSim rev0188 — Trigger Resolution Seal

Current linked revision: `MTGSim-rev0188-2026.07.08.09.28-triggerresolutionseal.zip`.

rev0188 seals the riskiest remaining trigger handoff after the rev0187 stack-gate work: when a triggered ability resolves and then ceases to exist, the durable audit trail now reciprocally links `TriggerRecord` and `StackResolutionRecord`. The code records the resolved sequence, resolution outcome, target mirror, payload-application mirror, and an auxiliary `EventRecord` backlink for stack-resolution rows.

Validation snapshot from the rev0188 tree: release build passed; C++ release tests 352/352; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; card catalog 56 cards. See `docs/architecture/trigger_resolution_backlink_seal_rev0188.md` and `reports/session/trigger_resolution_seal_audit_rev0188.json`.

# MTGSim rev0187 — Trigger Target Seal

rev0187 is the current linked revision: `MTGSim-rev0187-2026.07.08.08.52-triggertargetseal.zip`.

This revision targets the riskiest remaining gap from the trigger stack barrier: a targeted trigger can be stacked or dropped, but durable history must prove which target-choice surface was actually seen. `TriggerRecord` now seals required target count, chosen targets, legal target-set count, target-set hash, and no-legal-choice state before the trigger either becomes a stack object or is removed.

Validation snapshot from the rev0187 tree: release build passed; C++ release tests 351/351; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; card catalog 56 cards.

See `docs/architecture/trigger_target_choice_seal_rev0187.md` for the code-bearing seam note.

# MTGSim rev0186 — Trigger Stack Barrier

rev0186 is the current linked revision: `MTGSim-rev0186-2026.07.08.07.58-triggerstackbarrier.zip`.

This revision targets the triggered-ability stack gate. Simple targeted triggers now validate legal target sets before synthetic stack-object creation; if no legal choices exist, the pending trigger is dropped with linked `TriggerRecord`/`EventRecord` evidence and the stack remains unchanged.

Validation snapshot from the renamed rev0186 tree: release build passed; C++ release tests 350/350; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; card catalog 56 cards.

See `docs/architecture/trigger_stack_barrier_rev0186.md` for the code-bearing seam note.

# MTGSim rev0185 — SBA Pass Barrier

rev0185 is the current linked revision: `MTGSim-rev0185-2026.07.08.07.21-sbapassbarrier.zip`.

This revision targets the state-based-action pass barrier instead of adding registry surface. `apply_state_based_actions` now records a `check_index`, `pass_index`, and `pass_candidate_count` for typed SBA rows, and Aura cleanup created by a leaving enchanted creature waits for the repeated SBA check instead of being moved directly by attachment link cleanup.

Validation snapshot from the renamed rev0185 tree: release build passed; C++ release tests 349/349; scenarios 93/93 with 566 assertions; broad fuzz 12/12; risk-seam fuzz 8/8; rule coverage 0 errors / 0 warnings; card catalog 56 cards.

See `docs/architecture/sba_pass_barrier_rev0185.md` for the code-bearing seam note.

# MTGSim rev0184 — Replacement Tier Seal

## rev0184 — Replacement Tier Seal

rev0184 is a code-bearing risk-seam revision. It prioritizes the next rule-616 replacement danger after chain continuity: a supported zone-change replacement pass now chooses the earliest applicable `ReplacementPriorityTier` before falling back to deterministic `choice_rank`.

Highlights:
- Added `ReplacementPriorityTier` to `ZoneChangeReplacementDefinition`.
- Added `priority_tier`, `candidate_min_priority_tier`, and `eligible_candidate_count` to `ZoneChangeReplacementRecord`.
- Validation rejects tier skips, zero eligible candidates, and eligible counts greater than total candidates.
- Added `test_zone_change_replacement_priority_tier_forces_eligible_choice` and updated audit/ledger/doc wiring.

Audit/refactor: datacube audit history now emits compact v2 rows and the local history was normalized below the large-file review threshold.

Datacube: `MTGSim-rev0184-2026.07.08.06.54-replacementtierseal.zip`

# MTGSim rev0183 — Replacement Chain Seal

## rev0183 — Replacement Chain Seal

rev0183 is a code-bearing risk-seam revision. It prioritizes the rule-616 replacement chain over additional registry doctrine: linked zone-change replacement rows are now validated as a contiguous repeated event chain rather than trusted only by first/final destination endpoints.

What changed: `src/validation.cpp` now checks that each replacement pass consumes the original requested destination or the previous pass's replacement result; `pass_index` must match contiguous range order; affected-player evidence must match the moved object's pre-move controller/owner; duplicate source/definition/source-zone LKI applications in one event chain are rejected; and replacement rows must be owned by the movement range they backlink. The focused C++ regression now corrupts each of those audit holes.

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

- `--write-demo-replay`
- `--verify-replay`
- `StateCoreSnapshot.v1`
- `ActionTrace.v1`
- `ReplayArtifactManifest.v3`
- `paid-action journal attachment`
- `ReplayArtifactManifest.v2`
- `manifest_schema`
- `--artifact-bundle-roundtrip`
- `manifest-bound`
- `--inspect-replay-bundle`
- `diagnostic`
- `ReplayArtifactFailureKind`
- `--write-replay-prefix`
- `longest known-good prefix`
- `mtgsim_cli_replay_bundle_prefix_roundtrip`
- `--write-replay-resume-probe`
- `resume probe`
- `mtgsim_cli_replay_bundle_resume_roundtrip`
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
- `StackPlacementRecord`
- `rev0150`
- `Cost Witness Receipts`
- `tap_cost_event_sequence`
- `rev0151`
- `Sacrifice Cost Witnesses`
- `first_sacrifice_cost_zone_change_record_index`
- `rev0152`
- `Choice Lock Receipts`
- `first_choice_event_sequence`
- `rev0153`
- `Choice Payload Anchors`
- `choice_mode_index`
- `target_choice_event_sequence`
- `rev0154`
- `Choice Anchor Hash Seal`
- `journal_hash`
- `rev0155`
- `Target Set Hash Witness`
- `choice_target_set_hash`
- `rev0156`
- `Mode Contract Hash Witness`
- `choice_mode_contract_hash`
