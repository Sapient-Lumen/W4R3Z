# Benchmark Program

This program defines how Concord evaluates repeated-game strategy behavior without overfitting to a single suite.

## Benchmark Families

1. Baseline deterministic worlds.
2. Noise/horizon robustness sweeps.
3. Holdout adversary suites.
4. Population-dynamics stress suites.
5. Negative-control suites (expected non-dominance).

## Required Benchmark Outputs

1. run metadata and seed reports
2. suite summary artifacts
3. failure-envelope summary
4. claim class mapping (`CC-*`)

## Benchmark Governance

1. New benchmark families require spec updates and schema validation.
2. Baseline changes require recorded rationale in docs/ADR/ledger.
3. Public-facing benchmark claims must include holdout context.

## Minimum cooperation benchmark card (implementor-facing)

For any cooperation benchmark that may eventually be compared across counterpart classes, human lanes, adaptation regimes, or asymmetric seats, keep one compact card with at least these rows:

1. counterpart class and counterpart-mix rule (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_counterpart_mix_as_a_first_class_evaluation_contract.md`)
2. counterpart-class × novelty-axis coverage (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_counterpart_class_x_novelty_axis_coverage.md`)
3. cold-start / familiarized / co-adaptive status (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_familiarization_practice_and_coadaptation_protocol.md`)
4. same-partner continuation vs fresh-partner transfer after acclimation (`docs/LIBRARY/topics/cooperation_benchmarks_should_separate_same_partner_coadaptation_from_fresh_partner_transfer.md`)
5. role / seat assignment and side-switch policy when roles are asymmetric (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_role_assignment_and_side_switch_policy.md`)
6. information visibility and asymmetry regime when task-relevant facts are not equally shared (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_information_visibility_and_asymmetry_regime.md`)
7. communication schedule and channel rights when any message channel exists (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_communication_schedule_and_channel_rights.md`)
8. interaction language, translation/localization regime, and pooling rule whenever the benchmark uses natural language (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_interaction_language_and_translation_policy.md`)
9. interaction horizon, stopping rule, and termination knowledge in repeated-interaction lanes (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_interaction_horizon_stopping_rule_and_termination_knowledge.md`)
10. intervention rights, delegation policy, and final-action authority when control is shared or overridable (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_intervention_rights_delegation_policy_and_final_action_authority.md`)
11. process-aware vs outcome-only interpretation (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_process_capture_and_common_ground_metrics_not_only_outcome_scores.md`)
12. human-lane type, proxy provenance, hosting posture, and real-human escalation status when any human-proxy partner is used (`docs/LIBRARY/topics/cooperation_benchmarks_should_publish_human_proxy_provenance_and_real_human_escalation_status.md`)
13. counterpart-disclosure condition, blinding / deception note, and participant-belief elicitation in real-human lanes (`docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_counterpart_disclosure_and_belief_protocol.md`)
14. participant-pool provenance, country / residence mix, key eligibility filters, and repeat-exposure policy in real-human lanes (`docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_participant_pool_provenance_and_repeat_exposure_policy.md`)
15. material payoff matrix, stake / compensation mapping, and comprehension protocol in real-human lanes (`docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_material_stakes_and_comprehension_protocol.md`)
16. incentive instruction, reward semantics, and payoff scaling in LLM / agent-only lanes (`docs/LIBRARY/topics/cooperation_benchmark_llm_lanes_should_publish_incentive_instructions_and_payoff_scaling.md`)

The retained card should stay tiny.
Do not widen the archive with bulky benchmark-sidecars when one compact publication object can state which lane was run, what changed, and what headline comparison is actually justified.

## Headline comparison discipline

Treat the minimum cooperation benchmark card as a **comparison license**, not as metadata decoration.
For every retained cooperation result, add two short fields to the card:

1. **headline comparison licensed**;
2. **headline comparison not licensed without further justification** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_the_headline_comparison_they_license.md`).

A generic “more cooperative” claim is warranted only when the non-target contract rows are held fixed or separately stratified.
If proxy vs real-human status, same-partner vs fresh-partner status, language lane, communication regime, or other contract rows are pooled together, label the retained roll-up as a descriptive convenience summary rather than as one unified comparative result.

## Score construction discipline

Treat every retained top-line cooperation score as a **declared estimand**, not as a self-explanatory scalar.
For every retained cooperation result, add three short score-construction fields on the card or in the neighboring compact receipt:

1. **scored unit / unit of analysis**;
2. **pooling / weighting / censoring rule**;
3. **primary estimand** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_the_scored_unit_pooling_rule_and_primary_estimand.md`).

Do not compare per-turn, per-episode, per-participant, or pooled-across-lane numbers as if they were the same quantitative object.
If a retained report includes convenience composites in addition to the primary score, label those roll-ups as descriptive rather than as interchangeable copies of the main cooperation result.

## Primary metric and multiplicity discipline

Treat every retained cooperation result as attached to a **declared metric-governance policy**, not as though any scalar shown after the fact could stand in for “the cooperation score.”
For every retained result where more than one plausible endpoint, metric family, or composite exists, add four short fields on the card or in the neighboring compact receipt:

1. **primary endpoint / governing metric**;
2. **auxiliary / guardrail metrics**;
3. **composite / normalization rule**;
4. **multiplicity / metric-selection policy** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_primary_endpoint_auxiliary_metrics_and_multiplicity_policy.md`).

Do not compare joint reward, cooperation rate, reciprocity score, common-ground score, judge composite, harm rate, and convenience roll-ups as though they were interchangeable copies of the same cooperation object.
If the headline claim comes from one chosen metric among several plausible ones, say so directly and narrow the comparison license accordingly.
If the benchmark intentionally studies a multidimensional profile rather than one governing endpoint, say that directly too.

## Uncertainty and dependence discipline

Treat every retained comparative cooperation result as an **uncertainty-bearing estimate**, not as a point number that explains itself.
For every retained comparative result, add three short inferential fields on the card or in the neighboring compact receipt:

1. **dependence / clustering structure**;
2. **inference / resampling unit**;
3. **primary uncertainty summary** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_dependence_structure_inference_unit_and_uncertainty_summary.md`).

Do not let repeated turns, repeated episodes, or repeated evaluations of the same partner silently become the effective sample size.
If dependence lives at the dyad, participant, partner-pool, or task level, say so directly and compute uncertainty at that level or with a model that encodes the dependence.
If a retained object is descriptive only, label it as descriptive rather than letting a point estimate masquerade as a comparative result with hidden row-wise independence assumptions.

## Variant selection and test-touch discipline

Treat every retained cooperation result as attached to a **declared evaluation wrapper policy**, not as though prompt, interface, scoring, or agent-shell choices were invisible.
For every retained result where more than one plausible wrapper existed, add four short fields on the card or in the neighboring compact receipt:

1. **variant family**;
2. **selection / tuning rule**;
3. **search budget**;
4. **test-touch policy** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_variant_selection_tuning_and_test_touch_policy.md`).

Do not publish the best observed prompt, wrapper, or answer-selection variant as if it were the same object as an ex-ante fixed benchmark run.
If the result is a prompt-family summary, say so directly.
If the wrapper was tuned after seeing benchmark outcomes, label the retained object as tuned-on-test or otherwise narrow the comparison license accordingly.

## Evaluated subject and deployment discipline

Treat every retained cooperation result as attached to a **declared evaluated subject**, not as though “the model” were a stable self-explanatory object.
For every retained result where the evaluated subject could differ across provider endpoint, dated model marker, local weight snapshot, serving engine, or deployment window, add four short fields on the card or in the neighboring compact receipt:

1. **evaluated-subject provenance**;
2. **serving stack / execution substrate**;
3. **evaluation window / snapshot date**;
4. **update / drift posture** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_evaluated_subject_provenance_serving_stack_and_drift_window.md`).

Do not compare rolling aliases, dated provider markers, local open-weight runs, hosted third-party endpoints, and shadow APIs as though they were the same cooperation object.
If provider-side updates, scaffold changes, or endpoint identity ambiguity could have changed the subject being evaluated, say so directly and narrow the comparison license accordingly.

## Tooling, external state, and knowledge-source discipline

Treat every retained cooperation result as attached to a **declared environment-and-knowledge contract**, not as though tool catalogs, world snapshots, or retrieval corpora were invisible benchmark plumbing.
For every retained result where available tools, writable state, live services, or external knowledge sources can materially affect the score, add four short fields on the card or in the neighboring compact receipt:

1. **tool / capability catalog and access policy**;
2. **external environment / state snapshot posture**;
3. **knowledge base / retrieval corpus provenance and snapshot**;
4. **reset / refresh / mutability policy** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_tool_access_external_state_and_knowledge_snapshot_policy.md`).

Do not compare fixed-tool, distraction-tool, live-service, frozen-snapshot, different-corpus, and writable-corpus results as though they were the same cooperation object.
If one result depends on a different tool surface, a different accessible corpus, or a different world-state snapshot, say so directly and narrow the comparison license accordingly.

## Resource budget, context, and timeout discipline

Treat every retained cooperation result as attached to a **declared execution-budget contract**, not as though turns, tool calls, context limits, or timeouts were invisible benchmark plumbing.
For every retained result where interaction budget, history retention, or runtime caps can materially affect the score, add four short fields on the card or in the neighboring compact receipt:

1. **turn / action / tool-call budget**;
2. **context / history-retention policy**;
3. **token / compute / latency budget**;
4. **limit-hit handling / truncation / stop rule** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_turn_tool_context_budget_and_timeout_policy.md`).

Do not compare low-turn, high-turn, fixed-tool-budget, open-ended, full-context, summarized-history, and generous-timeout results as though they were the same cooperation object.
If one result depends on a budget-amplified regime or on a more forgiving timeout / retry posture, say so directly and narrow the comparison license accordingly.
If the point of the benchmark is to study cooperation under a stated resource ceiling, say that directly too.

## Scenario draw, seed, and release discipline

Treat every retained cooperation result as attached to a **declared scenario-sampling contract**, not as though task/world draws were invisible benchmark plumbing.
For every retained result where task instances, world states, partner assignments, or simulated episodes are drawn from a family rather than being one canonical fixed suite, add four short fields on the card or in the neighboring compact receipt:

1. **scenario / world / template family**;
2. **sampling / randomization rule**;
3. **seed set / reroll / stopping policy**;
4. **release posture / holdout exposure** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_scenario_family_sampling_rule_seed_policy_and_release_posture.md`).

Do not compare fixed-suite, generated-world, curated-slice, and private-hosted results as though they were the same cooperation object.
If the headline score depends on one seed bundle, a hidden reroll policy, or a public/private split with different contamination risk, say so directly and narrow the comparison license accordingly.

## Failure handling and denominator discipline

Treat every retained cooperation result as attached to a **declared failure-handling policy**, not as though only successful attempts count by default.
For every retained result where malformed outputs, refusals, abstentions, timeouts, parser failures, judge failures, comprehension failures, or post-hoc repairs are possible, add five short fields on the card or in the neighboring compact receipt:

1. **raw attempt denominator**;
2. **scored denominator**;
3. **failure / invalid-output taxonomy**;
4. **retry / repair rule and budget**;
5. **exclusion / scoring rule** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_failure_handling_retry_repair_and_exclusion_policy.md`).

Do not compare raw-attempt, valid-attempt, repaired-attempt, and filtered-judgment scores as if they were the same cooperation object.
If manual repair or post-hoc filtering changed the effective sample, label the retained object as repaired or filtered and narrow the comparison license accordingly.

## Judge, rubric, and adjudication discipline

Treat every retained cooperation result scored by an evaluator as attached to a **declared adjudication stack**, not as though the judge were invisible.
For every retained result where an LLM judge, human rater pool, panel, committee, or hybrid escalation pipeline materially affects the score, add four short fields on the card or in the neighboring compact receipt:

1. **judge / rater provenance**;
2. **rubric / scoring protocol**;
3. **adjudication / debias rule**;
4. **calibration / escalation policy** (`docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_judge_provenance_rubric_and_adjudication_policy.md`).

Do not compare results scored by different judge models, rubric orders, pairwise / pointwise modes, or escalation paths as though they were the same cooperation object.
If the scoring stack uses order swaps, committees, abstentions, or human escalation, say so directly.
If the judging pipeline was validated only on a subset or only against one rater source, narrow the comparison license accordingly.

## Machine-checkable compact card artifact

Treat the cooperation benchmark card as one **machine-checkable publication object**, not only as prose scattered across notes, papers, or dashboards.
For any retained cooperation benchmark result, prefer one compact artifact that validates against `schemas/cooperation_benchmark_card.schema.json` and stays close to the worked example at `examples/snapshots/cooperation_benchmark_card_example.json`.

Operational rules:

1. keep the retained card in one compact JSON object rather than a bulky sidecar bundle;
2. prefer explicit `not applicable` strings to silent omission when one section does not apply in the scored lane;
3. keep descriptive convenience notes in `notes` or a neighboring compact receipt rather than widening the card with benchmark-specific payloads;
4. when the benchmark genuinely licenses only a descriptive summary, say so directly in `result_kind` or in the comparison-license fields.

This operationalizes the existing card disciplines into one diffable, validator-friendly object for future inheritors (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_machine_checkable_compact_card_schema_and_worked_example.md`).

## Scaffold and canonical render aid

Once the compact card exists as a schema-backed JSON object, keep one low-friction fill path and one stable review path next to it.

Operational rules:

1. use `./grpy ./scripts/tools/cooperation_benchmark_card.py scaffold --id <card-id> --benchmark-name <name>` to start new cards from a valid explicit scaffold rather than hand-writing required rows from memory;
2. use `./grpy ./scripts/tools/cooperation_benchmark_card.py render <path/to/card.json>` to review or diff any retained card in one canonical markdown surface;
3. keep the rendered view derivative and reproducible from the JSON card rather than editing a parallel prose summary by hand;
4. prefer one canonical rendered example at `examples/snapshots/cooperation_benchmark_card_example.md` rather than proliferating ad hoc display formats.

This keeps the compact card machine-checkable for validators and human-checkable for inheritors without widening the archive (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scaffold_and_canonical_renderer_for_compact_cards.md`).

## Draft-valid versus claim-ready compact cards

Once the compact cooperation card can be scaffolded and rendered locally, keep one further distinction explicit: **schema-valid draft** is not yet the same thing as **claim-ready card**.

For any retained cooperation benchmark card that will support an inheritor-facing result:

1. allow `scaffold` output to remain draft-valid while fields are still being filled;
2. before treating the card as publication-ready, run `./grpy ./scripts/tools/cooperation_benchmark_card.py lint <path/to/card.json>`;
3. fail claim-readiness if unresolved `TODO` placeholders remain or if `not applicable` rows do not include a short reason;
4. keep this lint narrow and local rather than widening the schema with heavyweight workflow state.

This preserves low-friction card creation while adding one explicit quality gate between a syntactically valid draft and a claim-bearing compact artifact (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_distinguish_draft_valid_cards_from_claim_ready_cards_via_readiness_lint.md`).

## Freeze receipt for claim-ready compact cards

Once a compact cooperation card is both schema-valid and claim-ready, keep one further step explicit: **freeze the exact reviewed JSON card to the exact canonical rendered markdown view**.

For any retained cooperation benchmark card that will be cited or handed off:

1. run `./grpy ./scripts/tools/cooperation_benchmark_card.py freeze <path/to/card.json> --render-output <path/to/card.md> --receipt-output <path/to/card.freeze_receipt.json>`;
2. when the intent is to mint the current citation head rather than merely freeze some older retained card, prefer `--require-current-operational-head` so freeze fails closed unless the input is still the unique latest claim-ready lineage head;
3. let `freeze` re-run schema validation and the claim-readiness lint before it writes anything;
4. keep the receipt compact but hash-bearing: card path + hash, rendered markdown path + hash, schema path + hash, and freeze-tool path + hash; if the guarded mode was used, also retain the matched lineage/head guard inside the receipt;
5. treat the markdown as derivative and the freeze receipt as the tiny provenance handle that binds the reviewed structured card to the rendered view inheritors read.

This keeps compact cooperation cards machine-checkable, human-checkable, provenance-bound, and stale-head-safe without turning them into bulky publication bundles (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_freeze_receipt_for_claim_ready_compact_cards.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_freezing_compact_cards_against_stale_operational_heads.md`).

## Canonical delta receipt between claim-ready compact cards

Once two claim-ready compact cooperation cards both exist, keep one further step explicit: **publish the delta as a tiny machine-checkable receipt instead of forcing inheritors to diff the two cards by hand**.

For any retained cooperation benchmark card update that future inheritors may need to interpret:

1. run `./grpy ./scripts/tools/cooperation_benchmark_card.py compare <old-card.json> <new-card.json> --receipt-output <path/to/card.delta_receipt.json>`;
2. let `compare` re-run schema validation and the claim-readiness lint on both cards before it writes anything;
3. keep the receipt compact by listing changed dotted field paths rather than copying full old/new payloads;
4. classify changed paths into **claim-surface** versus **metadata-only** changes so inheritors can quickly tell whether the benchmark claim moved or only the surrounding labeling / notes moved.

This gives the archive one small audit object that says what changed between two retained claim-ready cards without widening the cards themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_canonical_delta_receipt_for_compact_cards.md`).


## Current-basis discipline for retained delta receipts

Once compact-card deltas start carrying lineage meaning for citation and inheritance, treat a retained delta receipt as **current basis evidence** only while it still matches the exact predecessor and successor card bytes it names.

For any retained cooperation benchmark lineage that will be cited or handed off:

1. treat a retained delta receipt as stale if either the predecessor or successor card drifts in place after the receipt was issued;
2. fail citation / handoff surfaces closed on that drift rather than silently treating the old receipt as still current lineage basis;
3. repair the lineage with a fresh `./grpy ./scripts/tools/cooperation_benchmark_card.py compare <old-card.json> <new-card.json> --receipt-output <path/to/card.delta_receipt.json>` receipt bound to the current card bytes;
4. keep the repair local and compact rather than widening the archive with bespoke migration notes.

This preserves the compact-card lineage as a current machine-checkable basis rather than a remembered or narratively reconstructed ancestry (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_fail_closed_when_retained_delta_receipts_no_longer_match_current_card_bytes.md`).

## Compact inventory and lineage register for retained cards

Once the archive retains more than one cooperation card or more than one compact receipt, keep one further step explicit: **publish one tiny generated register that says what cards exist, which are claim-ready, which are latest, and which receipts still resolve**.

For any retained compact cooperation-card family:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_inventory.py --write`;
2. keep the generated inventory compact: card ids + paths, claim-ready status, freeze status, predecessor / successor links from retained delta receipts, latest-known claim-ready ids, and any orphan receipts;
3. treat the inventory as a searchable register over the retained compact artifacts rather than as a second benchmark summary;
4. refresh it whenever a claim-ready card, freeze receipt, or delta receipt is added or changed.

This keeps the card stack locally searchable and lineage-aware without widening individual cards or receipts (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_compact_inventory_and_lineage_register_for_cards_and_receipts.md`).

## Lineage-head register for compact cards

Once the archive retains more than one card version or more than one lineage, keep one further step explicit: **publish one tiny generated head register that says which tip is operationally current, which tip is frozen for citation, and whether branching or missing freeze state makes the answer ambiguous**.

For any retained compact cooperation-card family:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_heads.py --write`;
2. keep the generated register compact: lineage ids, roots, tips, unique operational heads, unique citation heads, and any branch / ambiguity / needs-freeze warnings;
3. treat the head register as the citation/navigation surface over retained lineages rather than as a second benchmark summary;
4. refresh it whenever a claim-ready card, freeze receipt, delta receipt, or inventory update changes lineage topology or head status.

This keeps “what should I cite right now?” explicit for each retained lineage without widening the cards, receipts, or inventory themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_head_register_for_compact_cards.md`).

## Actionable review queue for compact cards

Once the archive already has compact cards, retained freeze receipts, and lineage heads, keep one further step explicit: **publish one tiny actionable queue that says which cards still need freeze, which frozen surfaces drifted, and which lineages need topology review**.

For any retained compact cooperation-card family:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_review_queue.py --write`;
2. keep the queue compact and action-shaped: item kind, stable reason codes, summary, review command, optional apply command, and the minimal lineage/card paths needed for local repair;
3. treat the queue as an operational maintenance surface over compact artifacts rather than as a second benchmark narrative;
4. refresh it whenever card readiness, freeze receipts, rendered markdown, delta topology, or lineage heads change.

This keeps compact-card maintenance explicit and locally executable without widening the cards or receipts themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_actionable_review_queue_for_compact_cards.md`).

## Lineage-grouped macro review queue for compact cards

Once the archive already has a flat actionable review queue, keep one further step explicit: **publish one tiny lineage-grouped macro review queue so inheritors can see all live repair work for one compact-card lineage without reconstructing it from scattered queue rows**.

Operational rules:

1. build it from the flat review queue and the current heads / citation surfaces rather than inventing a second review semantics;
2. group by lineage and publish the union of live item ids, item kinds, reason codes, context paths, review commands, and repair commands for that lineage;
3. choose one deterministic primary review command per lineage so the next action is obvious even when multiple repair rows exist;
4. refresh it whenever the flat review queue changes so handoff and control-plane surfaces do not collapse multi-item repair state into one arbitrary command.

This keeps compact-card repair work lineage-scoped and inheritor-readable without widening the cards, receipts, or citation basis themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_lineage_grouped_macro_review_queue_for_compact_cards.md`).

## Fail-closed citation surface for compact cards

Once the archive already has lineage heads and guarded freeze receipts, keep one further step explicit: **publish one tiny fail-closed citation surface that names exactly which compact cards are admissible to cite right now**.

For any retained compact cooperation-card family:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_citation_surface.py --write`;
2. admit only lineages with one unique citation head and exactly one verified freeze receipt that still matches the current card + canonical render surface;
3. copy the exact hash-bearing bindings from that verified freeze receipt into the generated surface rather than asking inheritors to rediscover them piecemeal;
4. list every unresolved lineage with stable reason codes so missing freeze, drifted freeze, or topology ambiguity fails closed instead of silently widening the citation answer.

This gives future inheritors one compact citation surface over the retained card stack, analogous to a tiny stable public surface, without widening the cards or receipts themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fail_closed_citation_surface_for_compact_cards.md`).

## Minimal citation handoff pack for compact cards

Once the archive already has a fail-closed citation surface, keep one further step explicit: **publish one tiny handoff pack that carries the exact citation-ready basis an inheritor should read, verify, and refresh without reconstructing lineage ancestry by hand**.

For any retained compact cooperation-card family:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_handoff_pack.py --write`;
2. emit one pack only for a lineage with one unique current citation head and one unique current operational head, so stale or ambiguous basis fails closed instead of silently inheriting old approval;
3. include the exact citation card, canonical rendered markdown, verified freeze receipt, ordered root-to-head ancestry cards, and ordered delta receipts that explain how the citation head was reached;
4. bind that pack to a small file manifest with hashes plus local verify / refresh commands, so inheritors receive one typed reentry surface rather than a scavenger hunt across reports;
5. publish the exact `citation_head_card_path`, `operational_head_card_path`, and one lineage-local `primary_open_path`, so the pack itself answers which retained files an inheritor should open first;
6. also publish one small ordered `entry_targets` family with role codes over those same lineage-local retained paths, so the pack explains why each first-open file belongs in that local reentry set;
7. also publish one direct role-annotated `primary_open_target` witness so inheritors do not have to scan the target family just to recover the canonical first-open object;
8. publish one direct `primary_verify_command` and one direct `primary_refresh_command` witness so inheritors do not have to scan command arrays just to recover the canonical first local check or rebuild step;
9. also publish one direct role-annotated `primary_verify_target` and one direct role-annotated `primary_refresh_target` witness so inheritors can tell what those first commands are for without reverse-engineering script names;
10. also publish one direct `primary_verify_subject_role_code` and one direct `primary_refresh_subject_role_code` witness so inheritors do not have to scan target role arrays just to recover the main subject of those first commands;
11. also publish one direct `primary_verify_intent_summary` and one direct `primary_refresh_intent_summary` witness so inheritors do not have to reconstruct the one-line purpose of those first commands from script names plus role codes;
12. also publish one direct `primary_verify_outcome_summary` and one direct `primary_refresh_outcome_summary` witness so inheritors do not have to infer the expected immediate result of those first commands from validator names plus target types;
13. also publish one direct `primary_verify_target_bytes` and one direct `primary_refresh_target_bytes` witness so inheritors do not have to scan the retained file manifest just to tell the size of those first machine targets;
14. also publish one direct `primary_verify_target_sha256` and one direct `primary_refresh_target_sha256` witness so inheritors do not have to scan the retained file manifest just to confirm the exact identity of those first machine targets;
15. also publish one direct `primary_verify_target_citation_entry_count` and one direct `primary_refresh_target_card_count` witness so inheritors do not have to open the retained report JSON just to tell the logical scale of those first machine targets;
16. keep `must_read_paths` ordered with the program doctrine first and the lineage-local `primary_open_path` immediately after it;
15. keep unresolved lineages in the pack output as review-command-bearing exclusions rather than widening the pack with speculative or branch-ambiguous bases.

This gives future inheritors one minimal citation handoff manifest over the retained card stack—closer to a tiny repro pack or typed reentry context than to a second benchmark summary—without widening the cards, receipts, or citation surface themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_head_card_paths_and_a_primary_open_path_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_role_annotated_entry_targets_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_primary_open_targets_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_commands_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_primary_verify_and_refresh_targets_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_subject_role_codes_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_intent_summaries_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_outcome_summaries_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_effect_codes_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_bytes_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_sha256s_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_target_citation_entry_counts_and_primary_refresh_target_card_counts_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_remaining_primary_verify_and_refresh_target_semantic_counts_in_handoff_packs.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_scale_summaries_in_handoff_packs.md`).

## Fused control-plane surface for compact cards

Once the archive already has inventory, heads, review queue, citation surface, and handoff pack, keep one further step explicit: **publish one tiny fused control-plane surface so inheritors can answer “what is current, citable, repairable, and handoff-ready right now?” without stitching five reports together by memory**.

For any retained compact cooperation-card family:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`;
2. keep the generated surface compact and typed: overall verdict, lineage counts, review pressure, citation readiness, handoff readiness, exact bindings to the underlying reports, and one per-lineage summary of operational head / citation head / unresolved reason codes / review-item kinds;
3. treat that surface as the preferred inheritor reentry point over the compact-card stack rather than as a second benchmark narrative;
4. refresh it whenever any underlying compact-card report changes so its hashes continue to bind the current control-plane answer.

This keeps the compact-card control plane one-shot addressable for inheritors and private tooling without widening the cards, receipts, or handoff basis themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_fused_control_plane_surface_for_compact_cards.md`).

## Deterministic focus-lineage digest for compact-card reentry

Once the archive already has a fused compact-card control plane, keep one further step explicit: **publish one tiny deterministic focus-lineage digest so inheritors can tell which lineage to inspect first without mentally ranking review counts, warning pressure, and lexical tiebreaks by hand**.

Operational rules:

1. derive the focus lineage from the existing fused control-plane fields rather than inventing a second repair semantics;
2. keep the selector tiny and stable: grouped review-item count first, then warning pressure, then unresolved citation pressure, then lineage id as the last deterministic tiebreak;
3. publish the chosen focus lineage id plus its current operational/citation heads and one short human-readable summary of why that lineage is first;
4. publish one primary focus-open path derived from already-retained lineage artifacts, so the inheritor knows exactly which file to open first;
5. also publish one small ordered, deduplicated `focus_open_paths` sequence so the inheritor can step through the companion retained files without reconstructing them by hand;
6. publish the same tiny path family as role-annotated `focus_open_targets`, so the inheritor can tell why each retained file appears in that reentry ladder without guessing from suffixes alone;
7. also publish one direct role-annotated `focus_primary_open_target` witness so the inheritor does not have to scan the target family just to recover the canonical first-open object;
8. also publish one direct role-annotated `focus_primary_verify_target` and one direct role-annotated `focus_primary_refresh_target` witness so the inheritor can tell what the first focus commands act on without reverse-engineering script names;
9. also publish one direct `focus_primary_verify_subject_role_code` and one direct `focus_primary_refresh_subject_role_code` witness so the inheritor does not have to scan focus target role arrays just to recover the main subject of those first focus commands;
10. also publish one direct `focus_primary_verify_intent_summary` and one direct `focus_primary_refresh_intent_summary` witness so the inheritor does not have to reconstruct the one-line purpose of those first focus commands from script names plus role codes;
11. also publish one direct `focus_primary_verify_outcome_summary` and one direct `focus_primary_refresh_outcome_summary` witness so the inheritor does not have to infer the expected immediate result of those first focus commands from validator names plus target types;
12. also publish one direct `focus_primary_verify_target_bytes` and one direct `focus_primary_refresh_target_bytes` witness so the inheritor does not have to scan the focus-lineage pack manifest just to tell the size of those first machine targets;
13. also publish one direct `focus_primary_verify_target_sha256` and one direct `focus_primary_refresh_target_sha256` witness so the inheritor does not have to scan the focus-lineage pack manifest just to confirm the exact identity of those first machine targets;
14. also publish one direct `focus_primary_verify_target_citation_entry_count` and one direct `focus_primary_refresh_target_card_count` witness so the inheritor does not have to open the first focus-machine report JSON just to tell the logical scale of those targets;
15. thread that digest through the main reentry surfaces so a ready-stack inheritor still receives one concrete inspection target after the initial verification command.

This keeps first-pass inheritance legible and honest without widening the cards, receipts, or citation basis (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_a_deterministic_focus_lineage_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_a_primary_focus_open_path_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_ordered_focus_open_paths_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_role_annotated_focus_open_targets_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_primary_open_targets_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_focus_primary_verify_and_refresh_targets_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_subject_role_codes_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_intent_summaries_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_outcome_summaries_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_effect_codes_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_bytes_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_sha256s_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_target_citation_entry_counts_and_focus_primary_refresh_target_card_counts_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_remaining_focus_primary_verify_and_refresh_target_semantic_counts_for_compact_card_reentry.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_scale_summaries_for_compact_card_reentry.md`).

## Typed next-action surface for compact cards

Once the archive already has a fused compact-card control plane, keep one further step explicit: **publish one tiny typed next-action surface so inheritors receive one authoritative first command instead of mentally ranking repair counts and review commands by hand**.

Operational rules:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write`;
2. derive it from the current control-plane + grouped review state rather than inventing a second repair semantics;
3. emit one typed primary action with the exact first command, fallback commands, and any focused lineage / reason-code context needed for local reentry;
4. emit a typed `verify_ready_surface` action when the compact-card stack is already ready, rather than leaving “do nothing” as implicit control-plane interpretation;
5. also publish the selected action's direct target, subject role, intent summary, outcome summary, and effect code so inheritors can tell what the chosen command is for without reverse-engineering script names or re-deriving hidden command semantics.

This keeps first reentry machine-readable and inheritor-cheap without widening the cards, receipts, or grouped review basis themselves (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_typed_next_action_surface_for_compact_cards.md`).

## Arbitration witness for compact-card next-action selection

Once the archive emits one preferred next action, keep one further step explicit: **publish one tiny arbitration witness so the chosen first command does not silently inherit more authority than the candidate family that selected it**.

Operational rules:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action_witness.py --write`;
2. preserve the live candidate family, winning priority bucket, tie set, fallback baseline, and stable selector used to choose the final candidate;
3. keep the witness separate from the final next-action surface so inheritors can distinguish “what won” from “why it won” without reconstructing hidden tie-break logic;
4. refresh it whenever the compact-card control plane or grouped review queue changes;
5. also publish the winning command's direct target, subject role, intent summary, outcome summary, and effect code so inheritors can see what the selected next step acts on without re-deriving hidden command semantics from builder code;
6. also publish the winning command target's direct `bytes`, `sha256`, and one-line scale summary so inheritors can audit the selected machine step without reopening retained JSON or scanning report bindings;
7. also publish the winning command target's direct typed semantic counts behind that scale summary so inheritors and tools do not have to parse English or reopen retained report JSON just to recover the locally relevant selected-step counts;
8. also publish one direct first-fallback command with the same target / subject / intent / outcome / effect semantics so inheritors can recover immediately when the preferred step fails without scanning fallback arrays or builder code;
9. also publish that first fallback target's direct `bytes`, `sha256`, and one-line scale summary so inheritors can audit the recovery step locally instead of reopening retained JSON or scanning report bindings after the primary step fails;
10. also publish the first fallback target's direct typed semantic counts behind that scale summary so inheritors and tools do not have to parse English or reopen retained report JSON just to recover the locally relevant recovery-step counts;
11. also publish the selected next command's retained inspect target as one direct role-annotated object rather than only as a bare open-path string;
12. also publish the first fallback command's retained inspect target the same way so the recovery ladder stays typed and machine-checkable after the preferred step fails;
13. also publish that selected next inspect target's direct `bytes` and `sha256` witnesses so inheritors can confirm the exact post-command document locally without scanning manifests or unrelated report bindings;
14. also publish the first fallback inspect target's direct `bytes` and `sha256` witnesses for the same reason so the recovery ladder stays locally auditable after the preferred step fails; and
15. also publish direct typed semantic counts on each selected command ladder step so inheritors can compare escalation targets mechanically instead of parsing prose scale summaries.

This keeps the compact-card next-action layer auditable and honest without widening the cards, receipts, citation surface, or handoff pack (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_arbitration_witness_for_compact_card_next_action_selection.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_targets_and_semantics_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_target_audit_fields_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_next_command_target_semantic_counts_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_targets_and_semantics_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_target_audit_fields_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_fallback_command_target_semantic_counts_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_command_open_paths_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_role_annotated_selected_command_open_targets_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_command_open_target_audit_fields_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_command_ladder_target_semantic_counts_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_command_ladder_required_lane_fields_for_compact_card_next_action_surfaces.md`; `docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_direct_selected_command_required_lane_status_details_for_compact_card_next_action_surfaces.md`).

## Execution-lane surface for compact-card handoffs

Once the archive emits compact-card control-plane and next-action surfaces, keep one further step explicit: **publish one tiny execution-lane surface so inheritors can see which validation lane is honestly available now rather than reconstructing environment truth from session prose or stale setup folklore**.

Operational rules:

1. run `./grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write`;
2. keep the surface observational rather than aspirational: record what Python / native Rust / existing JuNest-backed Rust is actually available now, and fail closed on missing lanes instead of assuming setup will succeed later;
3. keep the lanes typed and small: one surface-integrity lane for compact-card report rebuild/check work, one engine-harness lane for deeper repo validation, plus exact blocking reason codes and recovery commands when the deeper lane is unavailable;
4. thread that surface into control-plane, handoff-pack, and next-action outputs so a recommended command does not silently outrun the current environment.

This keeps compact-card reentry session-honest and inheritor-cheap without widening the cards, receipts, or citation basis (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_an_execution_lane_surface_for_compact_card_handoffs.md`).

Whenever durable compact-card program docs publish a command surface, normalize those commands through `./grpy` rather than bare `python3` so the inherited doc instructions match the wrapper-aware handoff surfaces and keep adjacent bytecode policy explicit (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_publish_wrapper_normalized_compact_card_commands_in_durable_program_docs.md`).

## Taxonomy registry for compact-card reason codes, action kinds, and lanes

Once compact-card governance grows beyond one schema and one receipt, the archive starts relying on many small stable identifiers: warning reason codes, citation reason codes, review item kinds, first-reentry action kinds, selector outcomes, and execution-lane ids.

Those identifiers should not live only as scattered strings in builders or in the current happy-path reports.
A compact benchmark program should ship one generated taxonomy registry that:

- names the stable compact-card token families that inheritors are expected to read or preserve,
- documents what each token means,
- points to the report fields where those tokens appear,
- carries the next-action priority policy in machine-readable form, and
- fails closed when a live surface emits an unregistered token.

This keeps compact-card governance from drifting into archive-specific folklore: inheritors can see **which identifiers are stable, what they mean, and where they are authoritative** without reverse-engineering the current scripts.

## Scope surface for compact-card subsystem boundaries

Once the compact-card program has accumulated examples, schemas, builders, validators, control-plane reports, and doctrine notes, inheritors need one exact machine-readable answer to **which files actually belong to that subsystem**.

A compact benchmark program should therefore ship one generated scope surface that:

- names the exact compact-card files that belong to the subsystem,
- distinguishes source members from generated members,
- keeps generated peers path-addressable without creating recursive hash dependence,
- carries one stable boundary digest for the subsystem itself, and
- is threaded into control-plane and handoff surfaces so first reentry does not depend on repo-memory folklore.

This keeps compact-card maintenance exact and inheritor-cheap: future sessions can see the subsystem boundary directly rather than inferring it from filenames or prior agent prose (`docs/LIBRARY/topics/cooperation_benchmark_programs_should_ship_a_scope_surface_for_compact_card_subsystem_boundaries.md`).

## First endogenous rematch benchmark seed

1. Start from `examples/snapshots/rematch_world_benchmark_seed.json` or regenerate it with `scripts/report/build_rematch_world_benchmark_seed_example.py`.
2. The standing seed now already carries seven compact copied handoffs: `canonicalization_planner_contract`, copied from `examples/snapshots/rematch_world_benchmark_canonicalization_handoff.json`; `winner_triage_handoff`, copied from the compact proxy-era live-contender / certification / materiality triage handoff; `delta_shortlist_handoff`, copied from the strict proxy-era publishable-delta profile; `paired_ranking_interpretation_handoff`, copied from the proxy occupancy / tempo / rank-decomposition interpretation summary; `matching_state_interpretation_handoff`, copied from the proxy matching-friction / occupancy interpretation summary for `SQ-013`; `turnover_tempo_interpretation_handoff`, copied from the proxy turnover-tempo interpretation summary for `SQ-015`; and `world_semantics_interpretation_handoff`, copied from the standing `SQ-012` role/state-carry interpretation summary. Keep all seven copied handoff sections frozen and citation-first all the way through compilation until the engine can emit native rematch-world planner, world-semantics, winner-triage, SESOI-band, ranking-interpretation, matching-state, and turnover-tempo manifests.
3. Before any new world-dependent fill work begins, run `scripts/tools/audit_rematch_world_benchmark_frozen_handoffs.py` so the standing seed is proven to rebuild-match the current seed builder and each copied frozen handoff still hash-matches its standalone source artifact.
4. Regenerate `examples/snapshots/rematch_world_benchmark_evidence_packet.json` with `scripts/report/build_rematch_world_benchmark_evidence_packet_example.py` and use that as the smallest retained distillation surface after a real run; bulky traces and wide run tables can stay scratch-only once the packet is filled.
5. Hash the scratch-only source files behind that packet with `scripts/tools/build_rematch_world_benchmark_evidence_receipt.py` so the packet can keep a compact provenance trail after the wider traces leave the archive.
6. Compile the evidence packet into the standard fill patch with `scripts/tools/compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py` instead of hand-copying world facts into the patch.
7. Regenerate `examples/snapshots/rematch_world_benchmark_fill_patch.json` with `scripts/report/build_rematch_world_benchmark_fill_patch_example.py` only when you need the placeholder template; otherwise let the compiled evidence-packet output be the patch you review.
8. Compile the patch back onto the seed with `scripts/tools/apply_rematch_world_benchmark_fill_patch.py` so the final retained object stays one benchmark artifact rather than a sidecar chain.
9. Replace null world-dependent telemetry in place inside the compiled benchmark instead of emitting separate occupancy, tempo, or paired-ranking reports.
10. Keep `compact_decision_bundle` copied verbatim from the standing decision contract unless the compact decision contract itself has been intentionally revised.
11. Treat the packet-plus-receipt-plus-patch workflow as a one-artifact publication starter, not as a second planning layer.
12. Use `scripts/tools/rematch_world_benchmark_completion_gate.py` before publication: clear the world-dependent `TEMPLATE_*` strings, fill the world-dependent null telemetry fields, flip the five world-section statuses to `filled`, and preserve the copied open-ended `end_delay: null` intervals that belong to the standing decision contract.
13. Use `scripts/tools/rematch_world_benchmark_mutation_guard.py` before publication: mutate only the seed edit surface, keep the contract-pointer fields frozen, and leave all copied handoff sections (`canonicalization_planner_contract`, `world_semantics_interpretation_handoff`, `winner_triage_handoff`, `delta_shortlist_handoff`, `paired_ranking_interpretation_handoff`, `matching_state_interpretation_handoff`, `turnover_tempo_interpretation_handoff`, and `compact_decision_bundle`) unchanged while filling world-dependent sections.
14. Use `scripts/tools/rematch_world_benchmark_publication_preflight.py` as the final one-command gate: it can compile the fill patch, run the mutation/completion checks together, confirm copied-contract digest equality, and emit a compact receipt for the handoff log.
15. Run `scripts/tools/audit_rematch_world_benchmark_copy_forward.py` against the compiled artifact so the retained publication state carries one tiny proof that the seven copied handoffs plus the compact decision bundle survived unchanged from the rebuild-audited seed into the filled artifact.
16. When that preflight passes, use `scripts/tools/build_rematch_world_benchmark_publication_bundle_receipt.py` to bundle the packet, evidence receipt, and preflight-ready compile path into one handoff receipt; by default, let the compiled fill patch stay scratch-only unless a debugging need makes it worth retaining temporarily. Treat that bundle receipt as the compact proof that the retained benchmark really emits the copied phase-3 decision contract: it should say the copied bundle still matches the standing contract and explicitly list the emitted delay / winner / delta sections plus the ten covered `SQ-017`–`SQ-026` question ids.
17. Regenerate the concrete durable publication spine with `scripts/report/build_rematch_world_benchmark_publication_spine_examples.py`: retain the packet, evidence receipt, compiled benchmark artifact, and preflight receipt explicitly, then treat the bundle receipt as a compact index over those four retained objects.
18. Audit the retained artifact against the retained preflight receipt rather than against a retained fill patch; the patch should stay scratch-only unless debugging or diff review actually requires it.
19. After retaining the concrete publication spine, run `scripts/tools/audit_rematch_world_benchmark_publication_spine.py` so the packet, compiled artifact, preflight receipt, and bundle receipt are rebuild-audited rather than only visually inspected.
20. Finish the handoff with `scripts/tools/build_rematch_world_benchmark_retention_exit_receipt.py`: keep the durable publication objects, let the compiled patch plus hashed scratch sources exit only when the receipt says `retention_exit_ready=true`, and avoid retaining cleanup residue by memory.
21. After the retention-exit receipt is ready, run `scripts/tools/prune_rematch_world_benchmark_transients.py` in dry-run mode and then with `--execute` when appropriate so concrete scratch/intermediate files actually leave by rule instead of lingering in the worktree until the next zip.
22. Before cutting the next revision zip, run `scripts/tools/audit_rematch_world_benchmark_post_prune_state.py` against the retention-exit receipt and the execute-mode prune receipt so the cleaned tree is explicitly proven safe to package: the durable publication spine must still hash-match and every exit-ready transient must already be absent or unlinked.
23. After the post-prune audit passes, build `scripts/tools/build_rematch_world_benchmark_publication_chain_receipt.py` so the inheritor can cite one compact end-to-end chain receipt from frozen source handoffs through cleaned-tree zip readiness instead of remembering four separate checkpoint receipts by name.
24. After the chain receipt passes, build `scripts/tools/build_rematch_world_benchmark_package_receipt.py` so the final zip boundary also carries one compact package proof: the tree should still be chain-consistent, PDF-free, scratch-free, and size-profiled before the next revision zip is cut.
   When you want the whole first-native-emission ladder in one inheritor-facing surface instead of reopening the individual receipts, regenerate `docs/REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md` with `make update-rematch-world-benchmark-world-emission-card`; it condenses the five native fill targets, the eight copied frozen sections, the bundle/spine/prune/package ladder, and the durable-vs-transient retention split into one generated card.
   When you want the exact edit surface for that same first-native fill pass, regenerate `docs/REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md` with `make update-rematch-world-benchmark-native-fill-map`; it names the legal mutable prefixes, the 24 current blocker loci, the metadata/status transitions, and the minimum publishable edit count without reopening the seed plus two separate guard/gate tools.
   When you want one concrete mutation witness rather than only the abstract map, regenerate `docs/REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md` with `make update-rematch-world-benchmark-example-delta-ledger`; it diff-checks the synthetic compiled artifact against the standing seed, proves the live packet-to-artifact toolchain still reproduces that snapshot, and separates the 30-path publication floor from the 3 optional row insertions that merely widen the policy set.
   When you want one exact answer to what survives closeout versus what may leave, regenerate `docs/REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md` with `make update-rematch-world-benchmark-closeout-lifecycle-ledger`; it fuses the durable six-object publication set, the four explicit transient exit rows, and the seven surviving guard/cleanup/authority receipts into one small lifecycle ledger so package discipline stays evidence-backed rather than remembered.
   When you want the smallest citation set for a particular rematch-world claim instead of reopening the whole bridge stack, regenerate `docs/REMATCH_WORLD_BENCHMARK_CITATION_WITNESS_MATRIX.md` with `make update-rematch-world-benchmark-citation-witness-matrix`; it maps each claim family to the minimal existing docs/receipts that should be cited and keeps the unresolved role/state, occupancy, and paired-ranking questions explicit.
   When you want the implementation queue for those still-open rematch-world questions instead of only the citation caution surface, regenerate `docs/REMATCH_WORLD_BENCHMARK_OPEN_TOUCHPOINT_RESOLUTION_MAP.md` with `make update-rematch-world-benchmark-open-touchpoint-resolution-map`; it collapses the 11 open touchpoints into 6 actual closure targets and shows which ones are seed-local section fills versus the remaining cross-section engine gap.
   When you want one exact answer to “what claim becomes safe when?”, regenerate `docs/REMATCH_WORLD_BENCHMARK_CLAIM_FRONTIER.md` with `make update-rematch-world-benchmark-claim-frontier`; it classifies all 8 claim families into already-safe, 8/18/29-edit native frontiers, and the `SG-003` engine-gap residue so the next native pass can stop overshooting or understating what has really closed.
   When you want one exact answer to “what does each stage actually buy?”, regenerate `docs/REMATCH_WORLD_BENCHMARK_STAGE_YIELD_LEDGER.md` with `make update-rematch-world-benchmark-stage-yield-ledger`; it turns the 7-step native ladder into a per-stage payoff ledger showing which stages unlock claims, which only retire prerequisite touchpoints, and which final stage is metadata-only closeout rather than new evidence.
   When you want one exact answer to “how much proof do we really need to retain or cite?”, regenerate `docs/REMATCH_WORLD_BENCHMARK_PROOF_BUDGET_LEDGER.md` with `make update-rematch-world-benchmark-proof-budget-ledger`; it prices each claim family’s minimal citation bundle in bytes, identifies the 7-surface unique proof library, and keeps future archive growth tied to explicit evidence budgets instead of broad retained scratch.
25. If the package receipt still shows `artifacts/reports` as the main retained growth surface, build `scripts/tools/build_archive_report_hotspot_receipt.py` so the inheritor can cite one tiny ranking of the report families most worth compacting before adding more report fanout nearby.
26. Before compacting any one hotspot family or retaining new report fanout next to it, build `scripts/tools/build_archive_report_compaction_candidate_receipt.py` so the next move starts from citation-backed families with durable non-report handles rather than from byte counts alone.
27. Before deciding that a hotspot family needs a brand-new durable note, build `scripts/tools/build_archive_report_semantic_handle_receipt.py` so the archive first reuses existing semantic handles that literal family-name matching may have missed; treat that receipt as a buffered hotspot scan that should also cover the one-trim-ahead rehearsal frontier.
28. If the top hotspot table still has large families with zero durable non-report handles even after that semantic-handle pass, build `scripts/tools/build_archive_report_compaction_gap_receipt.py` so the next tiny retained addition can unlock future compaction there before another report pair lands nearby; if that gap receipt comes back empty, treat the current hotspot surface as fully handle-covered and reuse the standing citation handles instead of minting a new note.
29. Once the current hotspot surface is fully handle-covered and the archive actually needs bytes back, build `scripts/tools/build_archive_report_compaction_manifest_receipt.py` so the next trim pass acts on one cited exact-file frontier instead of rediscovering report paths family by family.
30. Before removing those manifest paths, build `scripts/tools/build_archive_report_compaction_rehearsal_receipt.py` so the first trim is previewed once: exact bytes reclaimed, projected leading remaining hotspot, and projected second-wave handle coverage should all be visible before any retained report files actually leave the tree; if that projected frontier is already handle-covered, the first cited trim can proceed without minting another note first.
31. Before any retained report path actually leaves the archive, build `scripts/tools/build_archive_report_compaction_stage_receipt.py` so the cited exact-file frontier is first mirrored under `examples/scratch/archive_report_compaction_stage`, validated on the trimmed tree, and only then deleted; the stage mirror is temporary and must be gone before the next revision zip.
32. After that canonical trim actually executes, build `scripts/tools/build_archive_report_compaction_execution_receipt.py` so the archive keeps one compact proof of which cited frontier really left `artifacts/reports`, how much net space the pass reclaimed after the new control surfaces landed, and which refreshed frontier replaced it; if the refreshed rehearsal stays fully handle-covered, generate the next manifest / stage plan directly on the smaller tree, and only mint another durable note when the refreshed gap or rehearsal receipts stop clearing the frontier.
