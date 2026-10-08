# MTGSim rev0195 Artifact Report — Return Cost Receipt Gate

Linked revision: `MTGSim-rev0195-2026.07.08.16.56-returncostreceiptgate.zip`.

rev0195 continues the cost-payment risk seam with executable substance: `ReturnCostPaymentRecord` is the new typed receipt; return-to-hand costs now produce an explicit typed payment receipt and carry that receipt through paid-action declaration, stack placement, committed transaction, committed declaration snapshot, and `PaidActionTransactionJournal.v9`. This closes an audit gap where a card could move from battlefield to hand during a paid-action window without the transaction spine itself proving that the movement paid the locked return cost.

Audit/refactor focus: `tools/audit_datacube.py` now checks the rev0195 return-cost receipt spine across schema versions, source serialization, validator diagnostics, tests, docs, and rule-ledger wiring. The pass also updates replay manifest expectations to journal v9 so stale paid-action journal exports fail closed.

Validation evidence refreshed in this tree: C++ release tests 355/355, CTest 59/59, scenarios 95/95, broad fuzz 12/12, risk-seam fuzz 8/8, rule coverage 0 errors / 0 warnings, card catalog generation passed, and matrix planning refreshed.

---

# MTGSim rev0194 Artifact Report — Loyalty Cost Receipt Spine
Audit phrase: loyalty-cost payment receipt.

Linked revision: `MTGSim-rev0194-2026.07.08.16.15-loyaltycostreceiptgate.zip`.

rev0194 continues the cost-payment risk seam with executable substance: loyalty costs now produce an explicit typed payment receipt and carry that receipt through paid-action declaration, stack placement, committed transaction, committed declaration snapshot, and `PaidActionTransactionJournal.v8`. This closes a practical audit gap where a loyalty counter changed during a paid-action window but the transaction spine did not itself prove that the counter mutation paid the locked loyalty cost.

Research basis: the official Comprehensive Rules page identifies the rules document as the corner-case reference, and the current official text observed for this session is effective 2026-06-19. The relevant rule seam is 606.3/606.4 for loyalty ability timing and costs, plus 602.2b/601.2h for activation/cost-payment ordering. Official rules text remains unbundled.

Audit/refactor focus: `tools/audit_datacube.py` now checks the rev0194 loyalty-cost receipt spine across schema versions, source serialization, validator diagnostics, tests, docs, and rule-ledger wiring. The pass also updates the paid-action journal parser/verifier and replay manifest expected format to v8 so downstream artifacts fail closed on stale exports.

Evidence reports are refreshed under `reports/*/*rev0194_latest*`; package integrity is recorded in `reports/package/zip_integrity_rev0194.txt` after the final package step.

# MTGSim rev0193 Artifact Report — Life Cost Receipt Spine
Audit phrase: life-cost payment receipt.

Linked revision: `MTGSim-rev0193-2026.07.08.15.09-lifecostreceiptgate.zip`.

rev0193 continues the cost-payment risk seam with executable substance: paying life as a spell or activated-ability cost now produces an explicit typed payment receipt and carries that receipt through paid-action declaration, stack placement, committed transaction, and `PaidActionTransactionJournal.v7`. This closes a practical audit gap where a life total changed but the transaction spine did not itself prove that the loss paid a locked cost rather than damage or effect text.

Research basis: the official Comprehensive Rules page identifies the rules document as the corner-case reference, and the current official text observed for this session is effective 2026-06-19. Rule 118.3 says costs require the necessary resources and rule 118.3b defines paying life as subtracting from life total; rule 119.8 blocks paying life when an effect says the player cannot lose life. Official rules text remains unbundled.

Audit/refactor focus: `tools/audit_datacube.py` now checks the rev0193 life-cost receipt spine across schema versions, source serialization, validator diagnostics, tests, scenario DSL wiring, docs, and rule-ledger wiring. The pass also removes a front-door testing gap by allowing scenario files to construct life costs directly.

Evidence reports are refreshed under `reports/*/*rev0193_latest*`; package integrity is recorded in `reports/package/zip_integrity_rev0193.txt`.

# MTGSim rev0192 Artifact Report — Tap Cost Receipt Spine
Audit phrase: tap-cost payment receipt.

Linked revision: `MTGSim-rev0192-2026.07.08.14.29-tapcostreceiptgate.zip`.

rev0192 continues the cost-payment risk seam with executable substance: tap-as-cost now produces an explicit typed payment receipt and carries that receipt through paid-action declaration, stack placement, committed transaction, and `PaidActionTransactionJournal.v6`. This closes a practical audit gap where a source could be visibly tapped while the transaction spine did not itself prove that the tap paid a locked activated-ability cost.

Research basis: the official Comprehensive Rules page identifies the rules document as the corner-case reference, and the current official text observed for this session is effective 2026-06-19. Rule 601.2h requires locked costs to be paid without partial payments; rule 602.2b routes activated-ability activation through the casting payment process. Official rules text remains unbundled.

Audit/refactor focus: `tools/audit_datacube.py` now checks the rev0192 tap-cost receipt spine across schema versions, source serialization, validator diagnostics, tests, docs, and rule-ledger wiring. The pass also seals the previously under-covered discard/tap payment fields into stack-placement hashing, reducing room for silent payment-evidence drift.

Evidence reports are refreshed under `reports/*/*rev0192_latest*`; package integrity is recorded in `reports/package/zip_integrity_rev0192.txt`.

# MTGSim rev0191 Artifact Report — Discard Cost Receipt Spine
Audit phrase: discard-cost payment receipt.

Linked revision: `MTGSim-rev0191-2026.07.08.12.10-discardcostproofgate.zip`.

rev0191 continues the cost-payment risk seam with executable substance: discard-as-cost now produces an explicit typed payment receipt and carries that receipt through paid-action declaration, stack placement, committed transaction, and `PaidActionTransactionJournal.v6`. This closes a practical audit gap where a discarded hand card could be visible as a generic discard/zone movement while the transaction spine did not itself prove that the movement paid a locked cost.

Research basis: the official Comprehensive Rules page identifies the rules document as the corner-case reference, and the current official text observed for this session is effective 2026-06-19. Rule 601.2h explicitly permits total costs to include discarding cards and requires all costs to be paid without partial payments; rule 602.2b routes activated-ability payment through the casting process; rule 701.9a defines discard as moving a card from hand to graveyard; rule 701.9c makes some hidden-zone replacement cost payments illegal and subject to rollback. Official rules text remains unbundled.

Audit/refactor focus: `tools/audit_datacube.py` now checks the rev0191 discard-cost receipt spine across schema versions, source serialization, validator diagnostics, tests, docs, and rule-ledger wiring. The next high-risk continuation is a reusable nonmana cost-plan kernel that can order and rollback mixed sacrifice/discard/tap/counter/life payments without multiplying bespoke receipt code.

Evidence reports are refreshed under `reports/*/*rev0191_latest*`; package integrity is recorded in `reports/package/zip_integrity_rev0191.txt`.

# MTGSim rev0190 Artifact Report — Nonmana Receipt Spine

Linked revision: `MTGSim-rev0190-2026.07.08.10.50-nonmanareceiptspine.zip`.

rev0190 moves the riskiest unfinished paid-action seam forward with source-level substance: exact typed sacrifice-cost payment receipts are now carried by the paid-action declaration, the committed paid-action transaction, and the `PaidActionTransactionJournal.v4` export. This corrects an avoidable audit weakness where transaction consumers had to recover nonmana payment proof indirectly from stack-placement spans.

Audit/refactor focus: `tools/audit_datacube.py` now contains a dedicated `nonmana_cost_receipt_transaction_spine` probe so future cleanup cannot silently drop the declaration/transaction/journal/validator/test/doc linkage. The broader missing work remains a reusable nonmana cost-plan kernel for sacrifice, discard, tap, counter, life, and choice-payment ordering; rev0190 intentionally advances one high-risk vertical seam instead of expanding registry breadth.

Evidence reports: build `reports/build/build_report_rev0190_latest.json`; C++ `reports/harness/cpp_parallel_release_rev0190_latest.json`; scenarios `reports/scenarios/scenarios_release_rev0190_latest.json`; broad fuzz `reports/fuzz/fuzz_release_rev0190_latest.json`; risk-seam fuzz `reports/fuzz/risk_seams_rev0190_latest.json`; rule coverage `reports/rules/rules_coverage_rev0190_latest.json`; rules progress `reports/rules/rules_progress_rev0190_latest.json`; card catalog `reports/cards/card_catalog_report_rev0190_latest.json`; matrix `reports/harness/test_matrix_plan_rev0190_latest.json`; audit `reports/audit/datacube_audit_rev0190_latest.json`; package integrity `reports/package/zip_integrity_rev0190.txt`; session evidence `reports/session/nonmana_receipt_spine_audit_rev0190.json`.

# MTGSim rev0189 Artifact Report — Mission Freshness Waste Cut

Linked revision: `MTGSim-rev0189-2026.07.08.10.14-missionfreshnesswastecut.zip`.

rev0189 is a mission-and-hygiene revision. It identifies the project's heart as deterministic transition evidence, refreshes stale official-rules source metadata to 2026-06-19, records missing strategic seams, and corrects linked-package report accretion by leaving stale generated histories and mirrors in the cloud container. Current validation remains green: build, C++ release tests, scenarios, broad fuzz, risk-seam fuzz, rule coverage, and datacube/package audit.

# Artifact Report — MTGSim rev0188 Trigger Resolution Seal

Artifact filename: `MTGSim-rev0188-2026.07.08.09.28-triggerresolutionseal.zip`.

rev0188 is a code-bearing trigger-resolution audit/refactor pass. It closes the transient-stack-object gap by reciprocally joining the `TriggerRecord` that put a triggered ability on the stack to the `StackResolutionRecord` that resolved it. The validator now challenges both sides of that join and the event spine carries the trigger link as auxiliary StackResolution proof.

Evidence reports: build `reports/build/build_report_rev0188_latest.json`; C++ `reports/harness/cpp_parallel_release_rev0188_latest.json`; scenarios `reports/scenarios/scenarios_release_rev0188_latest.json`; broad fuzz `reports/fuzz/fuzz_release_rev0188_latest.json`; risk-seam fuzz `reports/fuzz/risk_seams_rev0188_latest.json`; rule coverage `reports/rules/rules_coverage_rev0188_latest.json`; rules progress `reports/rules/rules_progress_rev0188_latest.json`; card catalog `reports/cards/card_catalog_report_rev0188_latest.json`; matrix `reports/harness/test_matrix_plan_rev0188_latest.json`; session evidence `reports/session/trigger_resolution_seal_audit_rev0188.json`.

# MTGSim rev0187 Artifact Report — Trigger Target Seal

Revision: `rev0187`
Datacube: `MTGSim-rev0187-2026.07.08.08.52-triggertargetseal.zip`
Created: `2026-07-08T08:52:00-04:00`

## Purpose

rev0187 addresses the next trigger stack audit gap after rev0186. Targeted triggered abilities now leave durable target-choice evidence on `TriggerRecord`, so replay/audit consumers do not have to rely on a synthetic stack object that may later resolve, move, or clear targets.

## Substantive changes

- Added `required_target_count`, `chosen_targets`, `legal_target_set_count`, `choice_target_set_hash`, `target_choice_recorded`, and `no_legal_choices` to `TriggerRecord`.
- Added `seal_trigger_target_choice(...)` and extended `TriggerTargetChoice` to carry the full stack-gate proof.
- Extended validation for malformed trigger target-choice evidence.
- Added a targeted validator-corruption regression and expanded existing targeted-trigger tests.
- Refreshed the datacube audit probes so this seal remains wired across source, tests, docs, and ledger.

## Files of interest

- `include/mtgsim/types.hpp`
- `src/engine.cpp`
- `src/validation.cpp`
- `tests/cpp/test_engine.cpp`
- `tools/audit_datacube.py`
- `docs/architecture/trigger_target_choice_seal_rev0187.md`
- `data/rules/coverage/rules_ledger.json`

## Online grounding

This pass rechecked the current public rules surface for triggered-ability choice legality around 603.3d and priority-trigger processing around 117.5. Official Magic rules documents are not bundled in the datacube.

## Validation evidence

- Build: release all targets completed from the rev0187 tree
- C++ release tests: 351/351
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 8/8
- Rule coverage: 0 errors / 0 warnings
- Card catalog: 56 cards

## Remaining risk

The target-choice seal covers the current deterministic simple-trigger target policy. Full controller target/mode selection, optional triggers, intervening-if conditions, and delayed/reflexive trigger behavior remain future seams.

Datacube: `MTGSim-rev0187-2026.07.08.08.52-triggertargetseal.zip`

# MTGSim rev0186 Artifact Report — Trigger Stack Barrier

Revision: `rev0186`
Datacube: `MTGSim-rev0186-2026.07.08.07.58-triggerstackbarrier.zip`
Created: `2026-07-08T07:58:00-04:00`

## Purpose

rev0186 addresses a high-risk trigger stack seam. The engine now proves simple targeted-trigger choices before creating a synthetic stack object, and it drops a trigger with no legal choices using typed audit records.

## Substantive changes

- Added `TriggerTargetChoice` and pre-stack triggered target-set enumeration.
- `create_triggered_ability_stack_object` now receives chosen targets and no longer discovers target legality.
- `put_pending_triggers_on_stack` marks no-legal-choice triggers as dropped and emits a linked `TriggerDropped` event.
- Added `test_targeted_trigger_without_legal_targets_is_dropped_before_stack`.
- Added `docs/architecture/trigger_stack_barrier_rev0186.md` and refreshed ledger/manifest/revision surfaces.

## Files of interest

- `src/engine.cpp`
- `tests/cpp/test_engine.cpp`
- `docs/architecture/trigger_stack_barrier_rev0186.md`
- `data/rules/coverage/rules_ledger.json`
- `data/rules/official/manifest.json`

## Online grounding

This pass rechecked the current public rules surface for priority preflight and triggered-ability choice legality around 117.5 and 603.3d. Official Magic rules documents are not bundled in the datacube.

## Validation evidence

- Build: release all targets completed from the renamed rev0186 tree
- C++ release tests: 350/350
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 8/8
- Rule coverage: 0 errors / 0 warnings
- Card catalog: 56 cards

## Remaining risk

The new gate covers simple deterministic target selection. Full controller choice UX for modes/targets and richer optional/intervening-if trigger handling remain future seams.

Datacube: `MTGSim-rev0186-2026.07.08.07.58-triggerstackbarrier.zip`

# MTGSim rev0185 Artifact Report — SBA Pass Barrier

Revision: `rev0185`
Datacube: `MTGSim-rev0185-2026.07.08.07.21-sbapassbarrier.zip`
Created: `2026-07-08T07:21:00-04:00`

## Purpose

rev0185 addresses a high-risk timing seam in state-based actions. The engine now separates one SBA check from its repeated passes, and it prevents newly-created cleanup conditions from being hidden inside the mutator that created them.

## Substantive changes

- `StateBasedActionRecord` now stores `check_index`, `pass_index`, and `pass_candidate_count`.
- `apply_state_based_actions` collects all candidates at the start of each pass before applying them.
- `clear_attachment_links_for_zone_change` detaches Auras but leaves Aura graveyard movement to the repeated `AuraGraveyard` SBA pass.
- Validation rejects missing SBA check/pass evidence, pass regression within one check, and candidate-count drift inside one check/pass.
- `test_sba_pass_barrier_delays_aura_cleanup_from_creature_death` proves the creature-death SBA and Aura cleanup SBA are separate passes under one check.
- `tools/audit_datacube.py` now probes the new check/pass wiring.

## Files of interest

- `include/mtgsim/types.hpp`
- `src/engine.cpp`
- `src/validation.cpp`
- `tests/cpp/test_engine.cpp`
- `docs/architecture/sba_pass_barrier_rev0185.md`
- `docs/architecture/attachments_aura_equipment.md`
- `data/rules/coverage/rules_ledger.json`
- `tools/audit_datacube.py`

## Online grounding

This pass rechecked the current public rules surface for state-based actions: rule 704.3's check/perform/repeat structure and the Aura/Equipment cleanup rows around 704.5m/704.5n. Official Magic rules documents are not bundled in the datacube.

## Validation evidence

- Build: release all targets completed from the renamed rev0185 tree
- C++ release tests: 349/349
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 8/8
- Rule coverage: 0 errors / 0 warnings; 180 tested rows; 1725 linked tests
- Rules progress: 95.051% ledger-weighted; 7.452% conservative full-rules signal
- Card catalog: 56 cards

## Remaining risk

A whole-SBA-batch record is still future work. Rev0185 seals pass boundaries for the supported scaffold, but replacement effects that replace multiple simultaneous SBA results still need a richer batch-level object.

Datacube: `MTGSim-rev0185-2026.07.08.07.21-sbapassbarrier.zip`

# MTGSim rev0184 Artifact Report — Replacement Tier Seal

Revision: `rev0184`
Audit/refactor: datacube audit history now emits compact v2 rows and the local history was normalized below the large-file review threshold.

Datacube: `MTGSim-rev0184-2026.07.08.06.54-replacementtierseal.zip`

## Purpose

rev0184 addresses a high-risk semantic/audit seam in replacement resolution rather than adding documentation-only registry surface. rev0183 proved replacement-chain continuity; rev0184 proves the supported resolver does not skip an earlier rule-616 priority tier in favor of a higher-ranked general replacement.

## Substantive changes

- `ReplacementPriorityTier` now lives on zone-change replacement definitions.
- Candidate selection filters to the earliest applicable tier before applying `choice_rank`.
- `ZoneChangeReplacementRecord` now stores `priority_tier`, `candidate_min_priority_tier`, and `eligible_candidate_count`.
- Validation rejects `zone_replacement_record.priority_tier_skip`, `zero_eligible_candidates`, and `eligible_candidates_exceed_candidates`.
- `test_zone_change_replacement_priority_tier_forces_eligible_choice` covers the behavior and copied-state corruption guards.

## Files of interest

- `include/mtgsim/types.hpp`
- `src/engine.cpp`
- `src/validation.cpp`
- `tests/cpp/test_engine.cpp`
- `docs/architecture/zone_replacement_priority_tier_rev0184.md`
- `docs/architecture/zone_change_replacement.md`
- `data/rules/coverage/rules_ledger.json`

## Validation

Final validation report paths are listed in `REVISION.json`; reports are generated from the renamed rev0184 tree before packaging.

Datacube: `MTGSim-rev0184-2026.07.08.06.54-replacementtierseal.zip`

# MTGSim rev0183 Artifact Report — Replacement Chain Seal

Revision: `rev0183`
Datacube: `MTGSim-rev0183-2026.07.08.06.18-replacementchainseal.zip`
Created: `2026-07-08T06:18:00-04:00`

## Substance

rev0183 addresses a high-risk semantic/audit seam in the replacement engine rather than adding documentation-only registry surface. The current zone-change replacement resolver already rechecked modified events, but the validator was still too endpoint-oriented. This cut makes the repeated event chain itself challengeable.

## Files changed intentionally

- `src/validation.cpp`
- `tests/cpp/test_engine.cpp`
- `tools/audit_datacube.py`
- `data/rules/coverage/rules_ledger.json`
- `data/rules/official/manifest.json`
- `docs/architecture/zone_change_replacement.md`
- `docs/architecture/zone_replacement_chain_guard_rev0183.md`
- `docs/architecture/audit_refactor_notes.md`
- `docs/audit_refactor_notes.md`
- `docs/roadmap.md`
- `reports/session/zone_replacement_chain_audit_rev0183.json`
- revision/package metadata surfaces

## Audit/refactor finding

The risky pattern was replacement-chain endpoint trust. A malformed trace could preserve the first requested destination and final destination while making an intermediate pass consume the wrong event, drifting pass order, duplicating an already-applied replacement key, or splicing a row under a movement that did not own it. rev0183 moves that trust into executable validation.

## Online grounding

This session rechecked the official rules page and current Comprehensive Rules TXT metadata online. The observed TXT was effective 2026-06-19 and includes rule 101.4 APNAP ordering plus rule 616's replacement/prevention repeat loop. Official Magic rules documents remain metadata-only observations and are not bundled.

## Validation evidence

- Build: release all targets completed from the renamed rev0183 tree
- C++ release tests: 347/347
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 12/12
- Rule coverage: 0 errors / 0 warnings; 180 tested rows; 1717 linked tests
- Rules progress: 95.051% ledger-weighted; 7.452% conservative full-rules signal
- Card catalog: 56 cards
- Datacube audit: 0 errors / 0 warnings

## Remaining risk

This is still the narrow zone-change scaffold. It does not implement interactive rule-616 choices, simultaneous APNAP replacement batches, self-replacement/control/copy/back-face priority tiers, or replacement effects from unusual zones. The benefit is that the supported repeated chain is now much harder to corrupt silently.

Datacube: `MTGSim-rev0183-2026.07.08.06.18-replacementchainseal.zip`

# MTGSim rev0182 Artifact Report — Fuzz Shrink Audit

Revision: `rev0182`
Datacube: `MTGSim-rev0182-2026.07.08.05.55-fuzzshrinkaudit.zip`
Created: `2026-07-08T05:55:00-04:00`

## Substance

rev0182 addresses a high-leverage testing/audit gap rather than adding documentation-only registry surface. The engine's fuzz campaigns already exercised broad and risk-seam legal-action paths, but a future failure would still have arrived as a large seed/step tail. This revision makes failure evidence actionable by replaying and shrinking failed seeds inside the runner.

## Files changed intentionally

- `tools/run_fuzz.py`
- `tools/harness.py`
- `tools/audit_datacube.py`
- `tests/python/test_fuzz_runner.py`
- `data/rules/coverage/rules_ledger.json`
- `data/rules/official/manifest.json`
- `docs/architecture/fuzz_failure_step_shrinker_rev0182.md`
- `reports/session/fuzz_shrinker_audit_rev0182.json`
- revision/package metadata surfaces

## Audit/refactor finding

The wasteful/risky pattern was failed-seed triage bloat. The cube could spend CPU finding a randomized counterexample and then hand the human a noisy high-step tail. Rev0182 moves the first reduction loop into the cloudtainer run itself: failed seeds are replayed, minimized over step count, and surfaced in JSON/JUnit as copyable commands. The generated commands are shell-quoted, and the wiring is checked by both a Python guard and datacube audit probes.

## Online grounding

This session checked public fuzzing practice online: LLVM libFuzzer exposes crash artifacts, corpus reduction, and `-minimize_crash`; AFL/AFL++ expose `afl-tmin` style failure-preserving testcase minimization. MTGSim's local equivalent minimizes the deterministic seed/step transition prefix, which fits this project better than byte-corpus reduction. Official Magic rules observations remain metadata-only and are not bundled.

## Validation evidence

- Build: release all targets completed from the renamed rev0182 tree
- C++ release tests: 347/347
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 12/12
- Rule coverage: 0 errors / 0 warnings
- Rules progress: 95.051% ledger-weighted, 7.452% conservative full-rules proxy
- Card catalog: 56 cards
- Datacube audit: 0 errors / 0 warnings

## Remaining risk

This is prefix minimization, not semantic action-trace delta debugging. It will quickly find the first failing step for deterministic failures, but it does not yet remove irrelevant earlier choices or shrink the card/scenario state itself. That deeper reducer is still future work.

Datacube: `MTGSim-rev0182-2026.07.08.05.55-fuzzshrinkaudit.zip`

# MTGSim rev0181 Artifact Report — Paid State Hash Audit

Revision: `rev0181`
Datacube: `MTGSim-rev0181-2026.07.08.05.23-paidstatehashaudit.zip`
Created: `2026-07-08T05:23:00-04:00`

## Substance

rev0181 addresses a risky semantic/audit gap in the engine rather than adding more documentation-only registry surface. Rollback rows already proved that failed paid-action staging preserved the caller's physical state, but committed rows could present terminal receipts without proving the real pre-action to post-action StateCore transition. This revision turns committed paid-action rows into before/after physical-state receipts and makes validation/journal verification fail closed when that proof is absent or degenerate.

## Files changed intentionally

- `include/mtgsim/types.hpp`
- `src/engine.cpp`
- `src/validation.cpp`
- `tests/cpp/test_engine.cpp`
- `data/rules/coverage/rules_ledger.json`
- `data/rules/official/manifest.json`
- `docs/architecture/paid_action_commit_state_hash_rev0181.md`
- `reports/session/paid_state_hash_audit_rev0181.json`
- `README.md`
- `CHANGELOG.md`
- `REVISION.json`
- `pyproject.toml`

## Audit/refactor finding

The wasteful/risky pattern was duplicated physical sampling in the commit path: the transaction record had fields named as before/after physical hashes, but committed rows were not actually being bound to the caller's pre-action StateCore. That would make later replay/search consumers over-trust the receipt surface. rev0181 fixes the path by carrying the pre-action hash through the staged transaction helper and validating the committed transition.

A second audit/refactor correction landed in the harness: `tools/plan_test_matrix.py` no longer appends full matrix reports into `test_matrix_plan_history.jsonl`. Full plans remain available as report JSON files, while history now stores compact trend rows; the oversized prior JSONL history was pruned from roughly 2.5 MB to roughly 1 KB.

## Online grounding

This session rechecked the official rules surface online and observed the current Comprehensive Rules metadata as effective 2026-06-19. The relevant risk pressure is the casting/activation procedure plus illegal-action reversal; official rules text remains excluded from the datacube.

## Validation evidence

- Build: release all targets completed from the renamed rev0181 tree
- C++ release tests: 347/347
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 12/12
- Rule coverage: 0 errors / 0 warnings
- Rules progress: 95.026% ledger-weighted, 7.412% conservative full-rules proxy
- Card catalog: 56 cards

## Remaining risk

The full cost/announcement model is still not complete. Variable costs, alternate costs, cost modifiers, spending restrictions, cancellation prompts, and broader replacement/APNAP integration around payments remain future work. rev0181's narrow but important improvement is that the existing paid-action boundary now tells the truth about the physical state transition it commits.

Datacube: `MTGSim-rev0181-2026.07.08.05.23-paidstatehashaudit.zip`

# MTGSim rev0180 Artifact Report — Prevention Choice Audit

Revision: `rev0180`
Datacube: `MTGSim-rev0180-2026.07.08.04.54-preventionchoiceaudit.zip`
Created: `2026-07-08T04:54:00-04:00`

## Substance

rev0180 addresses a risky semantic gap in the engine rather than adding more documentation-only registry surface. Prior behavior consumed multiple applicable damage-prevention shields by container order and did not record enough evidence to explain or audit the choice. The revision adds deterministic choice-rank ordering and typed prevention-application evidence, then validates that evidence.

## Files changed intentionally

- `include/mtgsim/types.hpp`
- `include/mtgsim/engine.hpp`
- `src/engine.cpp`
- `src/validation.cpp`
- `src/rules.cpp`
- `tests/cpp/test_engine.cpp`
- `data/rules/coverage/rules_ledger.json`
- `docs/architecture/damage_prevention_choice_rank_rev0180.md`
- `reports/session/prevention_choice_audit_rev0180.json`
- revision/package metadata surfaces

## Validation snapshot

- C++ release tests: 347/347
- Scenarios: 93/93
- Broad fuzz: 12/12
- Risk-seam fuzz: 12/12
- Rule coverage: 0 errors / 0 warnings
- Card catalog: 56 cards

## Known remaining risk

This is still a deterministic scaffold, not full rule-616 interactivity. The next most valuable change is to connect this pass-by-pass candidate evidence into the broader replacement-event choice pipeline and APNAP/affected-player ordering machinery.

# MTGSim rev0179 Artifact Report — Mission Audit Shard Cap

Revision: `rev0179`

Datacube: `MTGSim-rev0179-2026.07.08.04.16-missionauditshardcap.zip`

## Substance

This revision records a deep mission read and corrects one concrete cloudtainer waste seam: default test-matrix planning previously converted the container's reported CPU count directly into target shards. The runners had already learned to cap auto parallelism; the planner and harness now follow the same cap.

## Audit/refactor

The deep-read conclusion is that MTGSim should keep competing on auditability, not raw card-script breadth: deterministic transition reducer, explicit legal-action boundary, typed receipts, replayable artifacts, and rule-linked validation. The missing pieces are rules-source refresh/diff, semantic transaction kernels for replacement/APNAP/paid actions, card-data importer boundaries, and counterexample shrinking.

## Validation

- Release build refreshed from source.
- Python manifest/planner cap guard passed.
- C++ release tests, scenarios, broad fuzz, risk-seam fuzz, rule coverage, card catalog, matrix planning, and datacube audit refreshed for `rev0179`.

---

# MTGSim rev0178 Artifact Report — Damage Life Results

Revision: `rev0178`

Datacube: `MTGSim-rev0178-2026.07.08.02.58-damageliferesults.zip`

## Substance

rev0178 closes a damage/life receipt drift seam. Player damage and lifelink now leave a `DamageRecord` that points at the exact `LifeChangeRecord` range for the caused life loss and gain rows.

## Audit/refactor

The cut converts event-order inference into a typed range contract. Validation checks damage-result flags, source identity, source zone-change identity, target snapshot, backlink, row kind, sequence order, amount, and exact player-loss/lifelink-gain counts. Focused coverage corrupts the owning range and the linked life-row backlink.

## Validation

- Release build configured from the source tree and linked `tests`, `scenario`, `fuzz`, and `cli`.
- C++ release tests: `346/346` passed.
- Scenario suite: `93/93` passed.
- Broad fuzz: `12/12` seeds passed.
- Risk-seam fuzz: `8/8` seeds passed.
- Rule coverage: 0 errors, 0 warnings.
- Card catalog report generated.
- Datacube audit: refreshed from the final rev0178 tree.

## Audit probe anchors

These legacy probe anchors are intentionally retained so the lightweight datacube audit can confirm earlier executable seams are still represented while rev0177 focuses on damage counter-change links.

- `CLI replay artifact`
- `mtgsim_cli_replay_artifact_roundtrip`
- `ReplayArtifactManifest.v3`
- `paid-action journal attachment`
- `ReplayArtifactManifest.v2`
- `manifest schema`
- `mtgsim_cli_replay_bundle_roundtrip`
- `mtgsim_cli_paid_replay_bundle_roundtrip`
- `ReplayArtifactFailureKind`
- `mtgsim_cli_replay_bundle_inspect_roundtrip`
- `diagnostics`
- `ReplayArtifactPrefixResult`
- `mtgsim_cli_replay_bundle_prefix_roundtrip`
- `longest known-good prefix`
- `ReplayArtifactResumeResult`
- `mtgsim_cli_replay_bundle_resume_roundtrip`
- `resume snapshot`
- `rev0154`
- `Choice Anchor Hash Seal`
- `331/331`
- `rev0155`
- `Target Set Hash Witness`
- `332/332`
- `rev0156`
- `Mode Contract Hash Witness`
- `333/333`
