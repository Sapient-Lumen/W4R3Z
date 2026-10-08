## 2026-03-24 evidence-gap / closure additions

This family now also needs to prove:
- which exact gate is still blocked after profile/stage evaluation,
- what smallest bounded campaign would close that gap,
- and what changed when only one gap moved.

### New first-class artifacts

- `evidence-gap.report.json`
- `evidence-campaign.plan.json`
- `gap-closure.receipt.json`

### `enterprise_offline_stage_turns_open_gaps_into_campaign_without_rewriting_basis`
Proves that a worthy front-door crate should extract open enterprise-offline gaps from an inherited basis, turn them into a bounded plan, and close one gap without pretending the whole stage passed.

## 2026-03-24 decision-program / stage-progression additions

This family now also needs to prove:
- which staged adoption program a packet bundle belongs to,
- what evidence gates control progression from explore to team-default or enterprise-offline,
- and which exit posture follows without rewriting the earlier basis.

### New first-class artifacts

- `decision-program.runbook.json`
- `profile-progression.report.json`

### `explore_packet_graduates_to_enterprise_offline_without_rewriting_basis`
Proves that a worthy front-door crate should let a team progress to a stronger operating stage by inheriting the old basis, adding new evidence, keeping bounded exceptions visible, and ending in `conditional_keep` if offline/source-parity gaps remain.

# Crate Ecosystem Pathfinder Kit fixtures

This fixture family exists to make **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** concrete.

The goal is to standardize a very small, reviewable decision bundle for task-oriented crate choice:

- what problem is being solved,
- which roles and hard constraints matter,
- which candidates were imported,
- where interop/runtime/target lock-in lives,
- how popularity and imported health/trust signals were weighed,
- why one starter set was chosen or why review must stay manual,
- and what changed when the team revisits the decision later.

## Intended first scenarios

1. `async_http_service_tokio_lockin_tradeoff`
2. `cli_baseline_newcomer_vs_power_stack`
3. `embedded_no_std_alloc_split`
4. `manual_review_required_conflicting_signals`
5. `pubtime_cooldown_prevents_fresh_release_overpromotion`
6. `docsrs_default_target_shift_changes_visible_support_story`
7. `trusted_publishing_and_security_tab_do_not_equal_task_fit`
8. `starter_candidate_hides_required_companion_crate_and_blocks_freeze`
9. `teaching_default_and_production_default_diverge_but_both_are_legitimate`
10. `low_lockin_stack_loses_short_term_onboarding_but_wins_escape_cost`
11. `rustsec_or_malicious_crate_signal_invalidates_frozen_decision`
12. `docs_surface_shift_triggers_review_without_forcing_auto_replacement`
13. `cargo_add_best_effort_source_selection_is_not_decision_authority`
14. `visible_support_surfaces_do_not_settle_task_fit`
15. `portable_bundle_keeps_basis_visibility_and_choice_separate`
16. `pubtime_cooldown_and_as_of_replay_keep_new_release_out_of_frozen_basis`
17. `docsrs_target_shift_changes_current_visibility_without_rewriting_freeze_time_basis`
18. `portable_bundle_keeps_freeze_timebox_replay_and_current_choice_separate`
19. `msrv_breach_is_exclusion_not_runner_up_and_reentry_requires_floor_shift_or_new_release`
20. `search_order_and_popularity_do_not_revive_explicitly_excluded_candidate`
21. `docs_surface_or_sloc_improvement_do_not_override_target_gap_without_new_evidence`
22. `portable_bundle_keeps_choice_exclusion_and_reentry_separate`
23. `comparator_packet_keeps_runner_up_and_recheck_trigger_visible`

## Minimal bundle for 0.1

- `task-profile.json`
- `candidate-import.report.json`
- `role-coverage.report.json`
- `interop-surface.report.json`
- `decision-axis.report.json`
- `decision-pack.report.json`
- `starter-set.lock.json`
- `revisit-trigger.policy.json`
- `freeze-horizon.policy.json`
- `decision-watch.report.json`
- `candidate-basis.receipt.json`
- `candidate-elimination.receipt.json`
- `candidate-reentry.policy.json`
- `support-visibility.report.json`
- `pathfinder-bundle.manifest.json`
- `decision-timebox.receipt.json`
- `as-of-replay.report.json`
- `evidence-weight.policy.json`
- `evidence-origin.report.json`
- `freshness-window.policy.json`
- `starter-set-scope.report.json`
- `starter-set-readiness.report.json`
- `lockin-cost.report.json`
- `scope-split.receipt.json`
- `notes.md`

Later overlays may add:
- migration notes
- policy override files
- downstream benchmark or incident imports

## Current planning stance

This family should now be read as a **freezeable decision-pack lane**, not just ranking/candidate import.
The hard questions are no longer only “what could win?” but also:

- when is a starter set mature enough to freeze,
- where does the stack buy lock-in,
- when should teaching and production defaults intentionally diverge,
- and which later events force review of an already-frozen answer?

## Design rule

This family should optimize for **small decision artifacts**, not giant mirrors of crates.io metadata.
If the crate cannot justify a confident recommendation, the fixture should say `manual_review_required` instead of inventing ecosystem consensus.

## Scope boundary

This family is **not** trying to replace crates.io, docs.rs, crate-health metadata, trust scoring, or façade crates.
It is trying to standardize the receiver-facing artifact those surfaces still do not hand people by default.


## Import-basis addendum

This family now also needs to prove three additional questions:

- which source surface actually supplied a fact about a candidate,
- which public surfaces only make support posture more visible,
- and how another team can receive one compact review bundle later.

That is why the fixture family now includes `candidate-basis.receipt`, `support-visibility.report`, and `pathfinder-bundle.manifest` alongside the older ranking/freeze/watch artifacts.


## Replay-timebox addendum

This family now also needs to prove three more questions:

- what exactly was in-bounds when a starter set was frozen,
- what changed only in later public visibility or release timing,
- and how replay can reopen review without silently replacing the historical choice.


## Exclusion / re-entry addendum

This family now also needs to prove three more questions:

- why a plausible candidate was excluded in a way that survives later review,
- what exact evidence would let that candidate re-enter consideration,
- and which later public-surface changes are only advisory.

## 2026-03-23 revalidation addendum

This family now also needs to prove:
- whether the same task and policy still hold later,
- whether the original starter set still stands,
- and which triggers reopen review without automatically reopening the whole comparison.

### New first-class schema
- `decision-revalidation.report.json`

### `comparator_packet_keeps_runner_up_and_recheck_trigger_visible`
Proves that runner-ups and exclusions must survive into later revalidation instead of disappearing behind a fresh ranking pass.


## 2026-03-23 trigger / ticket addendum

This family now also needs to prove:
- which later facts actually opened review,
- how those facts become one compact shared recheck ticket,
- and how the ticket preserves the frozen basis instead of replacing it.

### New first-class schema
- `recheck-ticket.manifest.json`

### `advisory_pubtime_and_docs_build_drift_generate_recheck_ticket`
Proves that a worthy front-door crate should open one typed recheck ticket when advisory, release-timing, and hosted-support facts change together.


## 2026-03-24 adjudication / carry-forward additions

This family now also needs to prove:
- how conflicting packet facts are shown without losing route identity,
- how a reviewed adjudication is recorded,
- and how a later packet carries a prior decision forward without rewriting it.

### New first-class artifacts

- `adjudication-session.report.json`
- `decision-carryforward.receipt.json`

### `conflicting_docs_registry_and_policy_signals_require_adjudication_not_overwrite`
Proves that stronger public support or trust posture may justify recheck while still failing to displace a frozen winner for the original task profile.


## 2026-03-24 exception / expiry additions

This family now also needs to prove:
- how temporary relief is recorded without rewriting the frozen decision,
- how tool-local exceptions become one portable packet,
- and how expiry/removal is reopened later without exception amnesia.

### New first-class artifacts

- `policy-exception.receipt.json`
- `exception-expiry.ticket.json`

### `cargo_vet_exemption_and_cargo_deny_ignore_need_one_reviewable_exception_packet`
Proves that local audit/advisory exceptions may justify a bounded keep posture while still requiring owner, scope, support ceiling, and expiry.


## 2026-03-24 profile / evidence-floor additions

This family now also needs to prove:
- which adopter profile is asking,
- which evidence floors that profile requires,
- and whether the current packet bundle honestly satisfies those floors or still needs manual review.

### New first-class artifacts

- `policy-profile.pack.json`
- `profile-satisfaction.report.json`

### `same_task_under_explore_enterprise_and_safety_profiles_yields_different_gates`
Proves that one frozen starter set can legitimately pass for exploration, stay conditional for enterprise-offline, and remain manual-review-required for safety-onramp without the archive contradicting itself.
