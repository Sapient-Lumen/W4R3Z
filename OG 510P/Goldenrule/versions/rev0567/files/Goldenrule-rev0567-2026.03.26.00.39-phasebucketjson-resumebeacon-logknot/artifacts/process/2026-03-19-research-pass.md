## 2026-03-19 — rev0296 post-adaptation transfer split + compact cooperation card

- Added one compact benchmark-publication note at `docs/LIBRARY/topics/cooperation_benchmarks_should_separate_same_partner_coadaptation_from_fresh_partner_transfer.md` so future inheritors do not mistake private same-pair co-adaptation for broader post-familiarization transfer.
- Tightened the source-backed benchmark-contract spine without widening the archive:
  - added principle `42` to `docs/RESEARCH_SOURCES.md`,
  - added a small implementor-facing "Minimum cooperation benchmark card" section to `docs/BENCHMARK_PROGRAM.md`,
  - and indexed the new note in `docs/LIBRARY/README.md`.
- Restored execute bits on shell scripts and hooks after zip hydration so local harness / hook paths are runnable again from the archive copy.
- Validation run in this cloudtainer:
  - `python3 -m unittest discover -s tests/control -p 'test_*.py'` ✅
  - `python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli` ✅
  - `python3 ./scripts/test/check_generated_docs_presence.py` ✅
  - `python3 ./scripts/test/check_research_docs.py` ✅
  - `python3 ./scripts/test/check_docs_index_core.py` ✅
  - `python3 ./scripts/test/check_readme_command_surface.py` ✅
  - `make test-quick` still stops at the Rust step because `tools/rust_exec.sh` requires `junest` / `cargo`, which are absent in this container.
- Research / inheritor insight:
  - after any warm-up or acclimation lane, always ask whether the reported score is **same-partner continuation** or **fresh-partner transfer**;
  - otherwise a benchmark can silently promote private protocol convergence into a generalization claim.

# 2026-03-19 research pass — counterpart grid + two cited trims + receipt reclosure

## What changed

- Preserved the earlier compact counterpart note and source-register addition already landed on this tree:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_counterpart_mix_as_a_first_class_evaluation_contract.md`
  - `docs/RESEARCH_SOURCES.md` with `RS-GR-049` (Akata et al., 2025).
- Added one additional compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_cards_should_publish_counterpart_class_x_novelty_axis_coverage.md`
- Reclosed the live and one-step-ahead archive compaction chain after the second executed trim:
  - repaired the semantic alias for the half-step uniform-prefix optimality family in `scripts/tools/build_archive_report_semantic_handle_receipt.py`,
  - rebuilt `examples/snapshots/archive_report_{semantic_handle,compaction_candidate,compaction_gap,compaction_manifest,compaction_rehearsal,compaction_stage,compaction_execution}_receipt.json`,
  - and kept the package receipt, hotspot receipt, and archive size profile aligned with the smaller tree.
- Updated the targeted validators so they check the **current** frontier rather than the pre-trim one:
  - `scripts/test/check_archive_report_semantic_handle_receipt.py`
  - `scripts/test/check_archive_report_compaction_candidate_receipt.py`
  - `scripts/test/check_archive_report_compaction_manifest_receipt.py`
  - `scripts/test/check_archive_report_compaction_rehearsal_receipt.py`
  - `scripts/test/check_archive_report_compaction_stage_receipt.py`

## Research / inheritor insight

The archive now has three mutually reinforcing benchmark-contract ideas that should probably travel together in future implementation work:

1. `benchmark_interoperability_should_separate_partner_environment_and_institution_generalization.md`
2. `cooperation_benchmarks_should_publish_counterpart_mix_as_a_first_class_evaluation_contract.md`
3. `cooperation_benchmark_cards_should_publish_counterpart_class_x_novelty_axis_coverage.md`

Together they imply a compact inheritor rule:

- do not publish one universal cooperation headline,
- publish **which counterpart classes** were tested,
- publish **which novelty axes** were tested,
- and expose the untested cells explicitly.

That gives future sessions a small benchmark card that is much harder to overclaim from than a single blended scalar.

## Executed trim state carried forward

This tree already executed two cited exact-file trims before packaging this revision:

- first trim: `56886` raw bytes removed across `6` report families / `12` report files,
- second trim: `54248` raw bytes removed across `6` report families / `12` report files.

The live post-trim receipt chain now closes again after the alias repair.

## Current live posture

- package receipt: ready
- semantic-handle receipt: ready (`8/8`)
- candidate receipt: ready (`7/7`)
- gap receipt: ready (`8/8`)
- manifest receipt: ready (`9/9`)
- rehearsal receipt: ready (`11/11`)
- stage receipt: ready (`15/15`)
- execution receipt: ready (`26/26`)

Current live size surface after the executed trims:

- retained files excluding receipt: `1385`
- raw bytes excluding receipt: `9559773`
- approx revision zip bytes excluding receipt: `2702609`
- report bucket: `89` files / `270444` raw bytes
- next cited manifest frontier: `51057` raw bytes across `6` families / `12` files

## Recommended next move

Do **not** reopen already executed trims.
Start from the currently cited `51057`-byte manifest frontier and keep adding only compact contract notes or semantic aliases that clearly collapse future report families rather than widening the archive.


## Additional pass: human disclosure protocol + twenty-eighth canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_counterpart_disclosure_and_belief_protocol.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-051` (Tanguy et al., 2025), and
  - `RS-GR-052` (Barak & Costa-Gomes, 2025).
- Intention for this pass: pair one compact research-contract addition with the currently cited exact-file trim frontier so the archive advances while shrinking.

### Research / inheritor insight

The archive now has a tighter real-human benchmark rule:

- `RS-GR-051` says people coordinate differently with LLMs than with humans in a cooperative language game, and partner beliefs modulate those effects.
- `RS-GR-052` says people also change strategic play against LLM opponents because they expect different reasoning / cooperation from them.

So a human-lane result is not fully interpretable unless the benchmark card also says what participants were told about the counterpart and whether their beliefs were measured.

### Executed trim state

- Executed frontier recorded in `examples/snapshots/archive_report_compaction_execution_receipt.json`:
  - `12` retained report files,
  - `6` families,
  - `51057` executed raw bytes.
- The current post-trim manifest is smaller again:
  - `47123` raw bytes across `6` families / `11` exact retained report files.

### Frontier reclosure

The trim exposed one real second-wave gap on `examples_validation`.
Rather than leave the frontier half-open, this pass added:

- `docs/LIBRARY/topics/examples_corpus_should_remain_validated_as_a_scientific_fixture_baseline.md`
- and one matching semantic alias in `scripts/tools/build_archive_report_semantic_handle_receipt.py`.

That restored the refreshed rehearsal to `0` projected next-frontier handle gaps.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with `4` semantic aliases / `30578` raw bytes recovered
- candidate receipt ready (`7/7`) with a `47123`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- retained tree: `1366` files / `9454280` raw bytes / `2673724` approximate zip bytes
- report bucket: `67` files / `148579` raw bytes

## Additional pass: communication-lane contract + thirtieth canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_communication_schedule_and_channel_rights.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-055` (Anwar & Georgalos, 2026), and
  - `RS-GR-056` (Niszczota et al., 2025).
- Executed the currently cited exact-file trim frontier recorded on the rev0287 tree:
  - `11` retained report files,
  - `6` families,
  - `33883` executed raw bytes.

### Research / inheritor insight

Human/AI cooperation results are not only about who the counterpart is; they are also about the communication lane.
The recent repeated-PD evidence says message timing can change the treatment interpretation itself, while the finite-game evidence says allowing communication can materially raise cooperation with both humans and LLMs even when the human-machine gap remains.
So benchmark cards should publish whether communication was disallowed, pre-play-only, repeated, free-form, templated, symmetric, or pooled across regimes.

### Frontier reclosure

This trim exposed two compact archive-shaping facts on the smaller tree:

- `artifacts/reports` is no longer the single largest retained artifact bucket once the fixed-point report receipts are excluded, so the hotspot receipt now treats the reports bucket as one of the top two retained artifact buckets rather than requiring it to remain #1 forever.
- the only real second-wave handle gap was `rematch_world_benchmark_evidence_flow`, and it is now recovered through one standing semantic alias to `docs/LIBRARY/topics/first_endogenous_rematch_benchmarks_should_distill_one_tiny_evidence_packet_before_compiling_the_fill_patch.md` instead of a new bulky report family.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with `1` semantic alias / `2623` raw bytes recovered
- candidate receipt ready (`7/7`) with a `17886`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- retained tree: `1346` files / `9391673` raw bytes / `2650584` approximate zip bytes
- report bucket: `45` files / `67573` raw bytes

## Additional pass: stakes/comprehension contract + thirty-first canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_material_stakes_and_comprehension_protocol.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-057` (Gächter et al., 2024), and
  - `RS-GR-058` (Koppel et al., 2025).
- Executed the currently cited exact-file trim frontier recorded on the rev0288 tree:
  - `12` retained report files,
  - `6` families,
  - `17886` executed raw bytes.

### Research / inheritor insight

Human-lane cooperation results are not only about counterpart identity, language, or communication rights.
They also depend on whether participants faced materially salient incentives and whether they actually understood the payoff structure.
So benchmark cards should publish the payoff matrix, stake mapping, compensation contingency, comprehension-check protocol, exclusion/retry rule, and whether headline results use the full sample or only comprehension-passing participants.

### Frontier reclosure

This trim exposed one real second-wave interpretability seam on the smaller tree:

- the projected `extortion_metric` family now compacts cleanly through the standing `anti_vampire_scorecard_spec.md` note once that durable note explicitly names the `extortion_metric` handle, so the refreshed rehearsal returns to `0` projected next-frontier handle gaps without retaining another paired extortion report family.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`)
- candidate receipt ready (`7/7`) with a `14667`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- report bucket: `33` files / `49687` raw bytes


## Additional pass: participant-pool provenance lane + thirty-second canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmark_human_lanes_should_publish_participant_pool_provenance_and_repeat_exposure_policy.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-059` (Karpus et al., 2025), and
  - `RS-GR-060` (Moon et al., 2026).
- Executed the cited rev0289 trim frontier:
  - `12` retained report files across `6` families removed from `artifacts/reports`, reclaiming `14667` raw bytes.
- Reclosed the refreshed next frontier without minting another durable note: the smaller tree stays fully handle-covered through the next rehearsal using standing library-topic and snapshot handles only.

### Research / inheritor insight

Human-lane cooperation results are not only about the evaluated policy or the counterpart disclosure condition.
They also depend on who the sampled humans are, where they were recruited, and whether they have already seen similar AI or game setups.
So benchmark cards should publish the recruitment platform, country/residence mix, key eligibility filters, repeat-participation rule, and whether headline results pool across distinct participant populations.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`)
- candidate receipt ready (`7/7`) with a `23371`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- retained tree: `1324` files / `9373999` raw bytes / `2633585` approximate zip bytes
- report bucket: `21` files / `35020` raw bytes


## Additional pass: horizon / stopping-rule contract + thirty-third canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_interaction_horizon_stopping_rule_and_termination_knowledge.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-061` (Smyth et al., 2023), and
  - `RS-GR-062` (Mengel, 2022).
- Executed the cited rev0290 trim frontier:
  - `9` retained report files across `6` families removed from `artifacts/reports`, reclaiming `23371` raw bytes.
- Reclosed the refreshed next frontier with three tiny semantic aliases instead of retaining more validation-summary fanout:
  - `risk_register_validation`
  - `claim_register_validation`
  - `claim_classes_validation`

### Research / inheritor insight

Repeated-interaction cooperation results are not only about partner identity, communication, or language.
They also depend on the shadow of the future:
- whether play is one-shot, finite, or indefinite,
- what the stopping rule is,
- and what participants know about termination while they are deciding.
So benchmark cards should publish the horizon regime, stopping-rule parameters, and participant knowledge of termination instead of laundering those choices into a policy-generalization claim.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with `3` semantic aliases / `838` raw bytes recovered
- candidate receipt ready (`7/7`) with an `8123`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier gaps
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- retained tree: `1319` files / `9359497` raw bytes / `2631241` approximate zip bytes
- report bucket: `12` files / `11649` raw bytes


## Additional pass: process-aware / common-ground contract + thirty-fourth canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_process_capture_and_common_ground_metrics_not_only_outcome_scores.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-063` (Xie et al., 2026), and
  - `RS-GR-064` (Poelitz et al., 2026).
- Executed the cited rev0291 trim frontier:
  - `6` retained report files across `6` families removed from `artifacts/reports`, reclaiming `8123` raw bytes.
- Reclosed the now much smaller archive surface by updating three stale nonterminal compaction assumptions:
  - the hotspot receipt now treats `artifacts/reports` as a top-three artifact bucket on this smaller tree,
  - the candidate receipt no longer requires a library-topic-backed pair once the frontier has collapsed to direct-handle single-file families,
  - and the rehearsal receipt now permits an empty projected next frontier when the next exact trim would fully empty `artifacts/reports`.

### Research / inheritor insight

Cooperation results are not only about final payoffs or cooperation rates.
They can also differ in whether interaction reaches stable shared understanding, whether misunderstanding is repaired cheaply, and whether the observed success hides inconsistent reasoning or brittle communication.
So benchmark cards should publish whether the evaluation is outcome-only or process-aware, which trace channels were captured, and any grounding / repair metrics used in the reported interpretation.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with `0` semantic aliases / `0` alias bytes recovered on the terminal live frontier
- candidate receipt ready (`7/7`) with a `3526`-byte next trim frontier
- rehearsal receipt ready (`11/11`) with a terminal projected next frontier of `0` families / `0` gaps after the next exact trim
- stage receipt ready (`15/15`)
- execution receipt ready (`26/26`)
- report bucket: `6` files / `3526` raw bytes

## Additional pass: intervention-rights contract + thirty-fifth canonical trim

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_intervention_rights_delegation_policy_and_final_action_authority.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-065` (Luo et al., 2026), and
  - `RS-GR-066` (Lai et al., 2022).
- Executed the cited rev0292 trim frontier:
  - `6` retained report files across `6` families removed from `artifacts/reports`, reclaiming `3526` raw bytes.
- Reclosed the terminal archive surface by updating stale nonterminal compaction assumptions so the hotspot, candidate, manifest, rehearsal, and stage receipts can all describe an empty measured report frontier without forcing placeholder report families to remain.

### Research / inheritor insight

Human-AI cooperation results are not only about the evaluated policy or even the counterpart identity.
They can also change when the collaboration contract changes:
- whether the model only advises,
- whether it can act within a delegated region,
- whether a human can override or interrupt,
- and who actually holds final action authority.
So benchmark cards should publish the intervention rights, delegation policy, and final-action authority instead of laundering interface-control differences into a claim about reciprocity or partner quality.

### Current live posture

- package receipt ready (`7/7`)
- semantic-handle receipt ready (`8/8`) with an empty measured frontier
- candidate receipt ready (`7/7`) with a terminal `0`-byte frontier
- rehearsal receipt ready (`11/11`) with `0` projected next-frontier families / `0` gaps
- stage receipt ready (`15/15`) on the empty-frontier regime
- execution receipt ready (`26/26`)
- retained tree: `1309` files / `9382465` raw bytes / `2631044` approximate zip bytes
- report bucket: `0` files / `0` raw bytes

## Additional pass: information-visibility / asymmetry contract + empty-frontier receipt refresh

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_information_visibility_and_asymmetry_regime.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-067` (Li et al., 2025), and
  - `RS-GR-068` (Poelitz et al., 2026).
- Kept `artifacts/reports` in its true empty-frontier state and refreshed the size/profile/package/receipt surface on the note-augmented tree rather than reintroducing any placeholder report fanout.

### Research / inheritor insight

The archive now carries a tighter warning about information structure.
A cooperation result is partly a result about the policy, but it is also a result about who could see which facts, whether hidden information had to be actively elicited, and how much shared history each side retained.
So benchmark cards should publish the shared/private state split, observability symmetry, history window, and whether asymmetry was explicit or latent.

### Current live posture

- `artifacts/reports` remains at `0` measured frontier files / `0` raw bytes
- the candidate / gap / manifest / rehearsal / stage receipts remain in true terminal-state mode with `0` current frontier bytes
- the package and execution receipts are refreshed against the note-augmented tree so future sessions inherit a real empty-frontier archive rather than a stale post-trim snapshot

### Recommended next move

Do not recreate report fanout just to preserve pass history.
Stay in the current terminal regime: add only compact durable notes or validator/contract repairs when they clearly improve the inheritor handoff, then refresh the package/receipt surface on the true final tree.



## Additional pass: familiarization / co-adaptation contract + terminal-state receipt refresh

### What changed

- Added one compact implementor-facing note:
  - `docs/LIBRARY/topics/cooperation_benchmarks_should_publish_familiarization_practice_and_coadaptation_protocol.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-069` (Jiang et al., 2025), and
  - `RS-GR-070` (Kang et al., 2025).
- Kept `artifacts/reports` in its true empty-frontier state and refreshed the size/profile/package/receipt surface on the note-augmented tree rather than reintroducing any placeholder report fanout.

### Research / inheritor insight

The archive now carries a tighter warning about acclimation.
A cooperation result is partly a result about the policy, but it can also be a result about whether the participants or the model were allowed to learn each other before the scored rounds began.
So benchmark cards should publish whether the lane is cold-start or post-familiarization, how many tutorial / practice rounds occurred, what feedback was shown during acclimation, and whether repeated exposure created partner-specific learning.

### Recommended next move

Stay in the current terminal regime.
Add only compact durable notes or validator/contract repairs when they clearly improve the inheritor handoff, then refresh the package/receipt surface on the true final tree rather than rebuilding report fanout.
