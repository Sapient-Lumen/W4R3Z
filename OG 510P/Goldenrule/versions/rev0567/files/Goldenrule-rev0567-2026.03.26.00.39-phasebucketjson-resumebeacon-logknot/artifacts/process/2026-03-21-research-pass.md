## 2026-03-22 — Research Pass (Release Gates + Residual-Risk Custody)

### What I added

- Added two compact topic notes:
  - `docs/LIBRARY/topics/assurance_release_timing_and_monitoring_windows_are_world_contracts_not_aftercare_fine_print.md`
  - `docs/LIBRARY/topics/residual_liability_transfer_and_orphan_backstops_are_world_contracts_not_bankruptcy_edge_cases.md`
- Extended `docs/RESEARCH_SOURCES.md` through `RS-GR-304` with:
  - `RS-GR-297` (jurisdictional differences in closure release timing, post-closure monitoring windows, and state default when perpetual care is absent),
  - `RS-GR-298` (post-remediation management can require different mixes of long-term monitoring and institutional controls),
  - `RS-GR-299` (five-year protectiveness review, land-use controls, and property-transfer controls as long-term stewardship machinery),
  - `RS-GR-300` (ring-fencing, clarified liability, and bankruptcy-priority design to keep decommissioning costs off taxpayers),
  - `RS-GR-301` (residual-risk sharing and transfer as an explicit governance problem tied to relinquishment),
  - `RS-GR-302` (perpetual operator liability versus state transfer under agreed financial regimes),
  - `RS-GR-303` (closure-acceptance and liability-apportionment uncertainty as a barrier to beneficial reuse), and
  - `RS-GR-304` (premature financial-assurance release before performance benchmarks are met as a design failure).
- Added one compact local receipt:
  - `artifacts/process/release_gates_and_residual_risk_custody_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`
- Repaired inherited absolute `/workspace/...` markdown links across the root README and core docs so link validation now fails only on the standing formula-parser false positives around `K_[a,b](h)`.

### New research / inheritor insight

The archive already knew to publish future accounting, standing, prefunding, and deferred-maintenance visibility.
These sources add two missing post-closure governance layers underneath them.

- `RS-GR-297`, `RS-GR-298`, `RS-GR-299`, and `RS-GR-304` warn that a world can look more successor-protective because it delayed release, added conditional closure, extended monitoring, or required periodic protectiveness review rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-297`, `RS-GR-300`, `RS-GR-301`, `RS-GR-302`, and `RS-GR-303` warn that a world can look safer because residual risk stayed with operators, moved to parents or pooled vehicles, or was quietly socialized to the state rather than because actors became more reciprocal toward successors.

So the next implementor should avoid two more easy mistakes:

1. treating delayed release and verification windows as interchangeable with deeper moral concern for successors;
2. treating orphan-risk assignment and residual-liability transfer as bankruptcy trivia when they often determine who actually inherits long-horizon burdens.

### Recommended next move

1. Keep one immediate-release or weak-aftercare baseline beside any conditional-closure or delayed-release lane.
2. Publish monitoring-window length, review cadence, institutional-control persistence, and failed-review consequences together with any headline claims about future protection.
3. Keep one operator-retains-risk baseline beside any pooled, transferred, or state-backstopped residual-liability lane.
4. Publish insolvency waterfall, orphan-risk assignment, and transfer preconditions before treating stewardship or decommissioning worlds as morally improved.

# 2026-03-21 Research Pass

## What changed

- Re-read the standing extortion / anti-extortion artifacts already retained in the archive and distilled one compact summary receipt:
  - `artifacts/process/extortion_frontier_reread_20260321.json`
- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/voluntary_repeated_pd_with_error_and_exit_can_replace_retaliation_with_leaving.md`
  - `docs/LIBRARY/topics/repeated_game_worlds_should_publish_move_order_and_action_visibility_contract.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-132` (Izquierdo, Izquierdo & Boyd, 2026), and
  - `RS-GR-133` (LaPorte, Pracher & Pal, 2026).
- Updated the core inheritor/planning docs so the next implementor sees these two new constraints without reopening external papers:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

## Main local result

The archive's own retained extortion artifacts now read more sharply as a **three-way warning**:

1. short-horizon payoff wins against extortion do not survive the 1000-round lane;
2. the current long-horizon memory-one defense frontier splits into at least two modes — one with more mutual cooperation but a larger extortion surplus, and one with harsher play that shrinks the surplus but lowers own payoff;
3. the current `memory_one_exit` top score is a 4-round artifact and should still be treated as fixed-dyad exit gaming rather than partner choice.

That compact reread strengthens the next-tranche recommendation already latent in the archive:

> do not spend the next serious tranche on broader search over the current dyadic world alone.

Spend it on **institutional expansion with explicit measurement contracts**.

## New research / inheritor insight

Two fresh external signals tighten the implementor handoff:

- In a voluntarily repeated Prisoner's Dilemma with substantial error and the option to leave, classical retaliatory winners can disappear and leave-based sanctioning can take over.
- In direct reciprocity, changing the lane from simultaneous play to leader-follower / disclosed-action play can preserve some simple memory-one equilibria but does not reliably preserve richer ones.

So the next implementor should treat both of these as first-class benchmark boundaries:

1. **noisy leave/rematch** is not just the old dyadic game plus a third action;
2. **move order / action visibility** is not just UI plumbing around the same strategy contest.

## Recommended next move

1. Build the first true leave/rematch world.
2. Before widening search, rerun TFT / WSLS / Grim plus one leave-based sanction baseline inside one noisy voluntary-repetition slice.
3. Add one simultaneous-vs-disclosed-action companion lane and keep those results institution-separated.
4. Keep payoff-only anti-extortion wins non-claim-bearing until the scorecard also carries fairness / recovery / repair semantics.

## Local validation

- `python3 scripts/test/check_research_docs.py`
- `python3 scripts/test/check_docs_index_core.py`
- `python3 scripts/test/check_markdown_links.py` still reports inherited false positives / environment-specific path expectations and was therefore treated as advisory only for this pass.


## Additional compact pass: observed reciprocity versus hidden care

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/partner_choice_can_reward_observable_reciprocity_while_eroding_hidden_care.md`
  - `docs/LIBRARY/topics/private_reputation_worlds_need_an_explicit_assessment_update_rule.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-134` (Barclay, 2025), and
  - `RS-GR-135` (Okada & De Silva, 2024).
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew that leave/rematch and reputation should become explicit institutions.
These two sources sharpen what the next implementor should *measure* once that happens.

- `RS-GR-134` warns that partner choice can reward **visible, reputation-relevant helping** while reducing **hidden partner-maintenance help**.
- `RS-GR-135` warns that private-reputation results depend materially on the **assessment-update rule**, not merely on whether reputation exists.

So the next benchmark tranche should avoid two easy mistakes:

1. treating all cooperation as one scalar once third-party observation exists;
2. treating `reputation = true` as a sufficient world contract.


## Additional compact pass: unknown-state reputation and gossip contract

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/reputation_fading_is_not_the_same_as_incomplete_observation.md`
  - `docs/LIBRARY/topics/gossip_rules_are_institutional_dials_not_background_plumbing.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-136` (Kim & Murase, 2026), and
  - `RS-GR-137` (Quan et al., 2026).
- Added one compact local receipt:
  - `artifacts/process/reputation_world_contract_gap_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew that private reputation needs an explicit assessment rule.
These two sources sharpen the next layer below that rule.

- `RS-GR-136` warns that **sparse observation** and **fading / Unknown reputations** are not interchangeable imperfect-information regimes.
- `RS-GR-137` warns that **gossip cadence, fan-in, and trust weighting** can change whether private reputations converge or deadlock.

So the next implementor should avoid two more easy mistakes:

1. collapsing all imperfect-information reputation lanes into one generic noisy-reputation toggle;
2. treating gossip as harmless communication plumbing instead of as part of the institution.

### Recommended next move

1. Build the first minimal reputation lane with public/private assessment and explicit update rule.
2. Keep sparse observation and fading / `Unknown` states as separate world knobs.
3. Compare at least one punishment-off / punishment-on pair before generalizing sanction claims.
4. If gossip is enabled, publish cadence / fan-in / trust-weight / merge semantics and keep a no-gossip baseline.


## Additional compact pass: rehabilitation contract and repair-signal semantics

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/apology_and_reintegration_channels_are_institutional_dials_not_soft_fluff.md`
  - `docs/LIBRARY/topics/repair_signals_are_error_correction_channels_not_just_style.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-138` (apology availability / trackability can change reintegration after exclusion),
  - `RS-GR-139` (apology opportunities can raise cooperation and public/common-knowledge apologies matter at the group level), and
  - `RS-GR-140` (expressive signals can act as error-correction channels in indirect reciprocity).
- Added one compact local receipt:
  - `artifacts/process/repair_signal_world_contract_gap_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to treat apology / repair as possible attack surfaces.
These sources sharpen the next layer below that warning.

- `RS-GR-138` warns that exclusion worlds can change materially once apology becomes available and legible at re-entry time.
- `RS-GR-139` warns that apology visibility and later amends behavior can change group cooperation.
- `RS-GR-140` warns that expressive signals can function as explicit error-correction bandwidth under noisy indirect reciprocity.

So the next implementor should avoid two more easy mistakes:

1. treating punishment worlds as fully specified without a rehabilitation / re-entry contract;
2. attributing improvements from expressive repair channels to bare policy quality without a no-signal comparison.

### Recommended next move

1. If a sanction / exclusion lane is built, publish exclusion duration, re-entry rule, apology availability, and signal visibility / trackability.
2. Add one no-signal companion lane before generalizing from apology / emotion-enabled worlds.
3. Track at least one follow-through or abuse metric so cheap repair signaling does not hide inside a cooperation gain.


## Additional compact pass: reputation granularity and record-expiry semantics

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/reputation_granularity_is_a_world_contract_not_just_score_resolution.md`
  - `docs/LIBRARY/topics/record_expiry_and_visible_rehabilitation_countdowns_are_institutional_dials.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-141` (graded / ternary reputation states can change cooperation and recovery dynamics), and
  - `RS-GR-142` (bounded-memory record expiry and visible proximity to rehabilitation can unravel temporary exclusion).
- Added one compact local receipt:
  - `artifacts/process/reputation_granularity_and_record_expiry_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to separate sparse observation, fading `Unknown` states, gossip, and repair.
The next missing layer is that reputation worlds still hide two more institutional choices too easily.

- `RS-GR-141` warns that binary versus graded reputation is not just display detail; it changes recovery paths and justified-defection handling.
- `RS-GR-142` warns that once bad records expire, visible proximity to rehabilitation can change incentives and can even undermine exclusion.

So the next implementor should avoid two more easy mistakes:

1. treating reputation granularity as cosmetic score resolution rather than as part of the institution;
2. treating record expiry and countdown-to-rehabilitation visibility as harmless archive hygiene rather than as incentive-shaping world semantics.

### Recommended next move

1. If Concord adds a richer reputation lane, keep one binary baseline and publish the reputation alphabet plus the exact transition rule.
2. If Concord adds bounded-memory exclusion or expiring records, compare one visible-countdown variant against one hidden- or stochastic-countdown variant.
3. Do not claim punishment or forgiveness robustness across those worlds unless the retention / rehabilitation semantics are published compactly.


## Additional compact pass: hybrid assessment symmetry and reputation scope

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/hybrid_reputation_worlds_need_explicit_agent_type_assessment_contracts.md`
  - `docs/LIBRARY/topics/reputation_scope_must_say_whether_failures_attach_to_agents_families_or_all_ais.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-143` (artificial agents can alter reputation consensus and mitigate the punishment dilemma in hybrid indirect reciprocity),
  - `RS-GR-144` (one AI's failure can spill over to perceptions of all AIs), and
  - `RS-GR-145` (reputation-based reciprocity can weaken in human–bot networks and alter judgments about humans who help bots).
- Added one compact local receipt:
  - `artifacts/process/hybrid_reputation_scope_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to separate exit, repair, gossip, granularity, and rehabilitation timing.
The next missing layer is that hybrid reciprocity worlds still hide two more institutional choices too easily.

- `RS-GR-143` and `RS-GR-145` warn that adding artificial agents can change cooperation through altered consensus and altered norms, not just through extra counterpart diversity.
- `RS-GR-144` warns that reputational harm can attach at category scope: one bad AI can taint all AIs.

So the next implementor should avoid two more easy mistakes:

1. treating human-only and hybrid reciprocity worlds as the same institution with a few extra counterpart types;
2. treating reputation as purely individual in hybrid worlds when the effective scope may be individual, family, provider, or all-AI.

### Recommended next move

1. If Concord adds a hybrid human/AI reciprocity lane, publish whether humans and artificial agents are judged by the same or different norm, and whether judgments are action-only or intention-aware.
2. Keep one human-only baseline before generalizing from hybrid reciprocity results.
3. If Concord adds hybrid reputation, publish the spillover scope explicitly and compare against at least one no-class-spillover baseline.


## Additional compact pass: collective reputation and intergroup-universalism contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/collective_reputation_and_stereotype_scope_are_world_contracts_not_just_cognitive_shortcuts.md`
  - `docs/LIBRARY/topics/universalistic_cooperation_across_group_boundaries_depends_on_competition_and_mobility_contracts.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-146` (collective reputation changes cooperation through group-assessment criteria),
  - `RS-GR-147` (stereotype fallback can help or hurt cooperation depending on information sharing and can become sticky),
  - `RS-GR-148` (universalistic cooperation can lose reputational reward under intergroup competition), and
  - `RS-GR-149` (limited cross-boundary mobility can let a minority enforce intergroup cooperation).
- Added one compact local receipt:
  - `artifacts/process/group_boundary_and_collective_reputation_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to separate exit, gossip, repair, hybrid spillover, and rehabilitation timing.
The next missing layer is that group-structured reciprocity worlds still hide two more institutional choices too easily.

- `RS-GR-146` and `RS-GR-147` warn that collective or stereotyped reputation is not just a cheaper encoding of individual reputation; it can change who gets blamed, how strict assessment is, and whether stereotype use becomes self-reinforcing.
- `RS-GR-148` and `RS-GR-149` warn that universalistic cooperation across boundaries depends on competition and on the right to enforce norms across those boundaries.

So the next implementor should avoid two more easy mistakes:

1. treating group-level or stereotype-enabled reputation as harmless aggregation of individual records;
2. treating universalistic cooperation as a pure policy trait when competition and mobility rights can flip its local incentives.

### Recommended next move

1. If Concord adds a group-structured reputation lane, keep one individual-only baseline and publish whether stereotype fallback is allowed.
2. If Concord adds any collective-reputation lane, publish the group-assessment rule for mixed-behavior groups.
3. If Concord adds an intergroup or universalisation lane, compare one no-cross-boundary-enforcement variant against one selective-mobility variant before claiming broad moral generality.

## Additional compact pass: reputation-governance topology and centralized-score caution

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/reputation_governance_topology_is_a_world_contract_not_just_an_implementation_choice.md`
  - `docs/LIBRARY/topics/centralized_social_credit_style_scores_are_not_innocent_reputation_baselines.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-150` (opinion synchronization / consensus correlation is critical for indirect reciprocity),
  - `RS-GR-151` (public-heavy source weighting can drive polarization and fragmentation), and
  - `RS-GR-152` (centralized social-credit-style scores can reduce trust and cooperation and harden bias).
- Added one compact local receipt:
  - `artifacts/process/reputation_governance_topology_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to separate exit, gossip, repair, hybrid spillover, group boundaries, and rehabilitation timing.
The next missing layer is that reputation worlds still hide governance topology too easily.

- `RS-GR-150` warns that cooperation in indirect reciprocity can require sufficient opinion synchronization; independent private views are not just a noisier version of public reputation.
- `RS-GR-151` warns that public-heavy reputation use, especially when enemy opinions are mixed in, can create polarization cycles and fragmentation rather than just better coordination.
- `RS-GR-152` warns that centralized scalar social-credit-style scores are not a neutral shortcut for richer reputation information; they can reduce trust, reduce cooperation, and keep bias sticky.

So the next implementor should avoid two more easy mistakes:

1. treating private, synchronized, and centralized reputation worlds as the same institution with different storage backends;
2. treating a centralized scalar score as a generic reputation baseline rather than as a stronger institution with crowding-out and stale-bias failure modes.

### Recommended next move

1. If Concord adds a richer reputation lane, publish governance topology explicitly and keep one mostly-private baseline before generalizing from synchronized worlds.
2. Compare at least one friend-focused source-weighting rule against one broader source-mixing rule before claiming robustness under public reputation.
3. If Concord adds a centralized score lane, publish direct-experience override and fresh-behavior repair semantics and compare against a revisable local-reputation baseline.



## Additional compact pass: monitoring economics and help-evaluation semantics

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/monitoring_and_evidence_transfer_costs_are_world_contracts_not_background_friction.md`
  - `docs/LIBRARY/topics/helping_worlds_should_separate_unwillingness_inability_and_need_burden.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-153` (trust can function as reduced monitoring under costly observation),
  - `RS-GR-154` (competition and transfer costs reduce information sharing needed for reputation),
  - `RS-GR-155` (partner choice depends on both willingness / warmth and ability / competence, modulated by task affordances), and
  - `RS-GR-156` (misfortune and help-seeking can trigger blame as a way to avoid costly helping).
- Added one compact local receipt:
  - `artifacts/process/monitoring_and_help_evaluation_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to separate exit, gossip, repair, hybrid spillover, group boundaries, governance topology, and centralized scoring.
The next missing layer is that future worlds can still hide the *economics of seeing and helping* too easily.

- `RS-GR-153` warns that trust gains can partly be reduced-monitoring gains when observation is costly.
- `RS-GR-154` warns that evidence-transfer frictions and competitive disadvantage can thin out reputation information even when sharing would improve trust and efficiency.
- `RS-GR-155` warns that partner evaluation tracks both willingness and ability, and task affordances change which one should matter.
- `RS-GR-156` warns that needy or misfortunate recipients can be devalued because helping them is costly, which can masquerade as principled selectivity.

So the next implementor should avoid two more easy mistakes:

1. treating monitoring and evidence transfer as free background plumbing instead of as institution-level cost dials;
2. treating all non-help and all help-seeking as morally legible, rather than publishing whether the world distinguishes refusal from inability and need from exploitation.

### Recommended next build

1. Add one trust / reputation lane with explicit observation cadence, monitoring cost, and evidence-transfer friction metadata plus a low-friction baseline.
2. Add one helping / partner-choice lane that separates willingness from ability and publishes recipient need / burden semantics before interpreting refusal, blame, or exclusion.


## Additional compact pass: identity persistence and disclosure contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/identity_persistence_and_reputation_reset_cost_are_world_contracts_not_account_hygiene.md`
  - `docs/LIBRARY/topics/actor_identifiability_and_action_visibility_should_be_separate_world_fields.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-157` (cheap identity reset lowers trust and trustworthiness in reputation systems),
  - `RS-GR-158` (whitewashing remains a standard trust-attack class in open dynamic trust systems),
  - `RS-GR-159` (revealing who is present can reduce cooperation even when actions stay private), and
  - `RS-GR-160` (identity cues can modulate the behavioral effect of the same reputation signal).
- Added one compact local receipt:
  - `artifacts/process/identity_policy_contracts_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to separate monitoring, reputation, group scope, repair, and burden semantics.
The next missing layer is that those institutions still presuppose a policy for **who stays the same agent over time** and **what sort of person-level disclosure the world gives away**.

- `RS-GR-157` and `RS-GR-158` warn that cheap identity reset can collapse trust and trustworthiness and turn accountability into a whitewashing problem.
- `RS-GR-159` warns that actor identifiability is not equivalent to action visibility; revealing who is present can lower cooperation even when actions remain private.
- `RS-GR-160` warns that identity cues can modulate how the same reputation signal is read.

So the next implementor should avoid two more easy mistakes:

1. treating identity persistence, reset cost, and newcomer priors as platform hygiene rather than as part of the institution;
2. treating actor identifiability and action visibility as one transparency knob rather than as separate world fields.

### Recommended next move

1. Add one reputation or leave/rematch lane with declared reset rights, newcomer priors, and history-carryover semantics.
2. Add one disclosure comparison that separates anonymous visible-action play from identifiable private-action play and identifiable public-history play.
3. Do not generalize from disclosure gains unless identity cues, cue strength, and cue timing are published compactly.



## Additional compact pass: inequality source and scarcity-allocation contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/inequality_source_and_capability_alignment_are_world_contracts_not_just_initial_conditions.md`
  - `docs/LIBRARY/topics/scarce_allocation_rules_and_planner_authority_are_world_contracts_not_posthoc_accounting.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-161` (cooperation under asymmetry depends on endowment, productivity, and return structure),
  - `RS-GR-162` (merit-framed versus luck-framed inequality changes fairness perceptions and cooperation),
  - `RS-GR-163` (limited-goods allocation jointly reflects merit, need, and equality),
  - `RS-GR-164` (planner allocation policy can sustain cooperation by conditioning generosity and sanctioning defectors), and
  - `RS-GR-165` (third-party allocators can improve efficiency, but inequality creates fairness conflicts that weaken them).
- Added one compact local receipt:
  - `artifacts/process/inequality_and_scarcity_contracts_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to separate identity policy, monitoring economics, repair, governance topology, and group scope.
The next missing layer is that even before reputation or sanctioning starts, a world can still smuggle in a *fairness theory of scarcity and inequality* through its initial conditions and allocation rules.

- `RS-GR-161` warns that inequality interacts with payoff technology: aligned advantage can help under linear returns and hurt under threshold returns.
- `RS-GR-162` warns that merit-framed inequality can legitimize lower cooperation by changing what richer agents perceive as fair.
- `RS-GR-163` warns that limited-goods allocation is pluralistic in practice: merit, need, and equality all matter, and perceived background inequality shifts the weighting.
- `RS-GR-164` and `RS-GR-165` warn that planner or allocator policy can create apparent cooperation gains that are really governance gains.

So the next implementor should avoid two more easy mistakes:

1. treating inequality source and capability alignment as innocuous initialization instead of as world-contract fields;
2. treating scarce-allocation rules and planner authority as downstream accounting instead of as part of the institution itself.

### Recommended next move

1. Add one unequal-resource companion lane that compares luck-framed versus merit-framed inequality with declared endowment/productivity alignment.
2. Add one scarce-allocation companion lane that compares automatic division against a third-party or planner-controlled allocation rule with published equality / need / merit semantics.
3. Do not generalize from cooperation changes in scarce or unequal worlds unless inequality source, capability structure, and allocation authority are declared compactly.


## Metanorm / enforcer-governance extension

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/metanorms_governing_punishment_are_world_contracts_not_background_culture.md`
  - `docs/LIBRARY/topics/sanction_worlds_should_publish_enforcer_incentives_retaliation_risk_and_oversight.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-166` through `RS-GR-171`.
- Updated the core inheritor/planning docs so the next implementor sees these two new sanction-governance constraints without reopening external papers:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

## New research / inheritor insight

The archive now states more clearly that a sanctioning world is at least **three institutions at once**:

1. a rule for how targets are judged,
2. a metanorm for what observers should do after a violation, and
3. a governance regime for the punishers themselves.

That means future Concord worlds should not publish merely that punishment exists.
They should publish whether non-enforcement is blameworthy, whether punishers can profit or be retaliated against, and whether fourth parties monitor or replace them.


## Speech-act governance extension

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/commitment_stages_and_breach_semantics_are_world_contracts_not_preplay_flavor.md`
  - `docs/LIBRARY/topics/cheap_self_signals_need_cost_and_scoring_semantics_not_just_more_communication.md`
- Extended `docs/RESEARCH_SOURCES.md` with `RS-GR-172` through `RS-GR-175`.
- Updated the core inheritor/planning docs so the next implementor sees these two new communication-governance constraints without reopening external papers:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

## New research / inheritor insight

The archive now states more clearly that a communication-enabled world is at least **three institutions at once**:

1. an action policy,
2. a commitment policy for what can be promised before acting, and
3. a self-signaling policy for what can be claimed after acting.

That means future Concord worlds should not publish merely that communication exists.
They should publish whether commitments create score-relevant obligations, whether self-signals are cheap or effortful, and whether reputation repair requires follow-through.

## Additional compact pass: stochastic risk structure + fallback-institution semantics

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/shared_shock_structure_and_risk_pooling_are_world_contracts_not_payoff_noise.md`
  - `docs/LIBRARY/topics/formal_insurance_and_informal_solidarity_are_separate_world_contracts_not_one_safety_net.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-176` (stochastic risk can raise cooperation without strong evidence that informal risk sharing is the operative mechanism),
  - `RS-GR-177` (collective versus individual shocks can change intra-community cooperation),
  - `RS-GR-178` (formal insurance availability can reduce private solidarity transfers), and
  - `RS-GR-179` (formal fallback can crowd out informal transfers only modestly on average in a large real transfer network).
- Added one compact local receipt:
  - `artifacts/process/risk_structure_and_fallback_contracts_receipt_20260321.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew that scarcity, inequality, monitoring cost, and helping semantics matter.
These sources sharpen a missing layer below all of them: **what keeps people afloat when bad luck hits**.

- `RS-GR-176` and `RS-GR-177` warn that stochastic and shared-risk worlds can change cooperation even when informal risk sharing is not clearly the mechanism, so shock structure and common-fate exposure should be published explicitly.
- `RS-GR-178` and `RS-GR-179` warn that formal protection can either reduce private solidarity or leave much of it intact, depending on the institution, so a future benchmark should not collapse formal fallback and informal aid into one generic safety-net toggle.

So the next implementor should avoid two more easy mistakes:

1. reading every cooperation gain under risk as evidence of better reciprocity rather than changed shock structure or pooling options;
2. reading every helping shift under protection as evidence of better or worse morality rather than changed fallback, deservingness, or substitution semantics.

### Recommended next move

1. Add one minimal stochastic-risk world that publishes whether shocks are individual, correlated, or collective.
2. Keep pooling / side-transfer rights separate from the shock process itself.
3. Add one no-formal-protection versus formal-fallback companion pair before generalizing helping or solidarity claims.
4. Record whether agents could have protected themselves ex ante and whether others know that when judging need.

## Additional compact pass: concurrent portfolios and cross-lane spillovers

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/concurrent_relationship_portfolios_are_world_contracts_not_background_complexity.md`
  - `docs/LIBRARY/topics/cross_game_linkage_and_crosstalk_are_world_contracts_not_memory_accidents.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-180` (Rossetti, Hauser & Hilbe, 2025),
  - `RS-GR-181` (Donahue et al., 2020), and
  - `RS-GR-182` (Reiter et al., 2018).
- Added one compact local receipt:
  - `artifacts/process/concurrent_portfolio_and_crosstalk_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated dyadic reciprocity from partner choice, reputation, sanctions, speech acts, scarcity, and risk.
These sources add the missing **concurrency layer** underneath them.

- `RS-GR-180` warns that once people manage concurrent games, cooperation can fall relative to a single-game control in both same-partner and different-partner settings.
- `RS-GR-181` warns that linked multichannel worlds can sustain a weaker lane by borrowing leverage from a stronger one.
- `RS-GR-182` warns that accidental crosstalk can impede direct reciprocity and make strict retaliators fragile.

So the next implementor should publish **concurrent portfolio structure** and **cross-lane linkage / crosstalk policy** before treating observed cooperation changes as Golden-Rule progress.

## Additional compact pass: encounter topology and tie-rewiring governance

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/encounter_topology_and_bridge_structure_are_world_contracts_not_background_graph_choice.md`
  - `docs/LIBRARY/topics/homophily_and_tie_rewiring_rules_are_world_contracts_not_harmless_social_noise.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-183` (Brask et al., 2024),
  - `RS-GR-184` (Redhead et al., 2024),
  - `RS-GR-185` (Samu et al., 2025), and
  - `RS-GR-186` (Cárdenas et al., 2026).
- Added one compact local receipt:
  - `artifacts/process/encounter_topology_and_tie_rewiring_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated dyads from partner choice, reputation, sanctions, risk, and concurrency.
These sources add the missing **network-encounter layer** underneath them.

- `RS-GR-183` warns that hubs, bridges, and assortativity can materially change whether cooperation spreads or survives.
- `RS-GR-184` warns that reciprocity and punishment are being expressed on actual community networks, not on a featureless well-mixed pool.
- `RS-GR-185` warns that dynamic network cooperation may come from selective separation rather than prosociality being positively rewarded.
- `RS-GR-186` warns that homophily and prior acquaintance can shape who meets whom more strongly than measured reciprocal trust.

So the next implementor should publish **encounter topology** and **tie-formation / rewiring policy** before treating observed cooperation changes as Golden-Rule progress.

## Additional compact pass: harm accounting and collective damage semantics

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/help_versus_harm_framing_and_gain_loss_sign_structure_are_world_contracts_not_semantic_garnish.md`
  - `docs/LIBRARY/topics/collective_harm_latency_and_threshold_semantics_are_world_contracts_not_payoff_timing_details.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-187` (Kuper-Smith & Korn, 2025),
  - `RS-GR-188` (Schuch, Nhim & Richter, 2025),
  - `RS-GR-189` (Egberts, Engel & Fairfield, 2026), and
  - `RS-GR-190` (Carlsson, Ek & Lange, 2025).
- Added one compact local receipt:
  - `artifacts/process/harm_accounting_and_collective_damage_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated risk, scarcity, concurrency, and encounter topology.
These sources add the missing **harm-accounting layer** underneath them.

- `RS-GR-187` warns that cooperation can move because people are avoiding losses, not because they value reciprocity more.
- `RS-GR-188` warns that the same threshold game can look more cooperative when framed as producing a good than when framed as preventing a bad.
- `RS-GR-189` warns that delayed public damage can hide the cost of selfish action until private pain finally arrives.
- `RS-GR-190` warns that threshold uncertainty is especially destructive under weakest-link aggregation, so uncertainty and aggregation technology should not be collapsed.

So the next implementor should publish **help-versus-harm framing plus gain/loss sign structure**, and also publish **harm latency plus threshold / aggregation semantics**, before treating observed cooperation changes as Golden-Rule progress.

## Additional compact pass: triadic structure and delegated coordination semantics

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/triadic_interdependence_and_third_player_position_are_world_contracts_not_small_group_scaleups.md`
  - `docs/LIBRARY/topics/delegated_coordination_and_coalition_stages_are_world_contracts_not_preplay_conveniences.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-191` (Du et al., 2025),
  - `RS-GR-192` (Kitakaji, Hizen & Ohnuma, 2025),
  - `RS-GR-193` (Ball, Sarangi & Upadhyay, 2025), and
  - `RS-GR-194` (Xu, Zhang & Zheng, 2025).
- Added one compact local receipt:
  - `artifacts/process/triadic_and_delegated_coordination_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated dyads from partner choice, networks, communication, and sanctions.
These sources add the missing **small-group architecture and delegation layer** underneath them.

- `RS-GR-191` warns that triadic reciprocity is not a simple dyadic scaleup: third-player position and information scope can alter which dyads stabilize.
- `RS-GR-192` warns that partial communication can raise cooperation even for nonparticipants, so voice rights and audience scope are institutional dials.
- `RS-GR-193` warns that a coalition-formation stage can sort agents and raise provision before the substantive move even begins.
- `RS-GR-194` warns that leadership effects depend on the representative-selection mechanism; “leader present” is not one institution.

So the next implementor should publish **small-group interdependence structure** and **delegated coordination / representative-selection policy** before treating observed cooperation changes as Golden-Rule progress.

## Additional compact pass: private solutions and outside-option semantics

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/private_solution_availability_is_a_world_contract_not_just_an_extra_action.md`
  - `docs/LIBRARY/topics/outside_options_should_publish_loner_externality_and_group_formation_flexibility.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-195` (Malthouse et al., 2026),
  - `RS-GR-196` (Lo Iacono et al., 2024),
  - `RS-GR-197` (Mori, Hanaki & Kameda, 2024), and
  - `RS-GR-198` (Gross et al., 2020).
- Added one compact local receipt:
  - `artifacts/process/private_solution_and_outside_option_contracts_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated leave/rematch, risk fallback, scarcity, and identity policy.
These sources add the missing **private-solution / outside-option layer** underneath them.

- `RS-GR-195` warns that once a private route exists beside the public one, higher-advantage agents can peel off into self-protection and leave the public route weaker and more unequal.
- `RS-GR-196` warns that trust context can shift investment between collective and individual solutions even when free-riding does not increase.
- `RS-GR-197` warns that an outside option can aid collaboration when groups form flexibly and loner externality is limited.
- `RS-GR-198` warns that self-reliance can instead crowd out cooperation and increase inequality when private escape really substitutes for shared provision.

So the next implementor should publish **private-solution availability / access asymmetry** and also publish **loner externality / group-formation flexibility** before treating observed cooperation changes as Golden-Rule progress.

## Additional compact pass: need revelation and request-visibility semantics

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/need_revelation_and_help_request_stages_are_world_contracts_not_missing_data.md`
  - `docs/LIBRARY/topics/request_visibility_and_help_seeking_recognition_are_world_contracts_not_ui_garnish.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-199` (Bénabou, Jaroszewicz & Loewenstein, 2025),
  - `RS-GR-200` (Jo, Xie & Carroll, 2024),
  - `RS-GR-201` (Jo, Xie & Carroll, 2025), and
  - `RS-GR-202` (Burke, Sommerfeldt & Wang, 2025).
- Added one compact local receipt:
  - `artifacts/process/need_revelation_and_request_visibility_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated helping evaluation, observation cost, speech acts, and identity disclosure.
These sources add the missing **need-revelation / request-audience layer** underneath them.

- `RS-GR-199` warns that unmet need is not pure action failure: asking itself can be costly, and greater need can reduce asking.
- `RS-GR-200` warns that request visibility has trade-offs; “more visible asking” is not automatically better support design.
- `RS-GR-201` warns that request visibility and recognition can materially change the perceived social costs of seeking help.
- `RS-GR-202` warns that asking norms depend on who adopts the recognition system; partial adoption can make asking feel less legitimate rather than more.

So the next implementor should publish **need observability / ask / unsolicited-offer semantics** and also publish **request audience / recognition / subgroup asymmetry** before treating observed help or non-help as Golden-Rule progress.

## Additional compact pass: institution choice and franchise scope

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/endogenous_rule_choice_and_democratic_selection_are_world_contracts_not_preplay_ceremony.md`
  - `docs/LIBRARY/topics/franchise_scope_and_binding_scope_are_world_contracts_not_constitutional_detail.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-203` (Dal Bó, Foster & Putterman, 2024),
  - `RS-GR-204` (Guan et al., 2026),
  - `RS-GR-205` (Bühren, Dannenberg & Händel, 2025), and
  - `RS-GR-206` (Zhou et al., 2026).
- Added one compact local receipt:
  - `artifacts/process/institution_choice_and_franchise_scope_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated sanctions, delegated coordination, and rule content.
These sources add the missing **institution-choice / franchise-scope layer** underneath them.

- `RS-GR-203` warns that democratic selection can directly change cooperative behavior beyond simple sorting.
- `RS-GR-204` warns that democratic sanction effects depend on voting scope and sanction design rather than on “punishment” alone.
- `RS-GR-205` warns that subgroup-binding institutions are not small variants of whole-group institutions; coordination between subgroups becomes part of the institution.
- `RS-GR-206` warns that endogeneity is not a universal premium, so chosen rules should not be presumed better than imposed ones.

So the next implementor should publish **whether rules are chosen or imposed** and also publish **who votes versus who is bound** before treating observed cooperation changes as Golden-Rule progress.

## Additional compact pass: successor binding and future-beneficiary representation

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/successor_binding_and_commitment_reversibility_are_world_contracts_not_intertemporal_fine_print.md`
  - `docs/LIBRARY/topics/future_beneficiary_representation_and_social_scope_are_world_contracts_not_story_flavor.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-207` (Halali & Perez, 2025),
  - `RS-GR-208` (Swinkels, de Vette & Toom, 2025),
  - `RS-GR-209` (Guida, Klaser & Mittone, 2025), and
  - `RS-GR-210` (Imada et al., 2025).
- Added one compact local receipt:
  - `artifacts/process/intergenerational_representation_and_successor_binding_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already separated governance choice, request stages, private solutions, and collective harm timing.
These sources add the missing **intergenerational beneficiary / successor-governance layer** underneath them.

- `RS-GR-207` warns that successor binding can itself raise sustainability, so future-minded results should not be read as pure reciprocity gains unless lock-in and escape semantics are published.
- `RS-GR-208` warns that future generations are absent stakeholders by default, and that future-design methods are one concrete way to give them present-time voice.
- `RS-GR-209` warns that institutionalized agencies offering soft intergenerational advice can materially matter even without hard enforcement.
- `RS-GR-210` warns that “future generations” is not a socially neutral target: intergenerational cooperation changes when future beneficiaries are framed as ingroup versus outgroup.

So the next implementor should publish **whether current cohorts can bind successors** and also publish **how absent future beneficiaries are represented and socially scoped** before treating observed sustainability as Golden-Rule progress.



## Additional compact pass: future-horizon depth and future-vividness contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/future_generation_depth_and_temporal_horizon_are_world_contracts_not_story_scale.md`
  - `docs/LIBRARY/topics/future_vividness_and_intertemporal_linkage_are_world_contracts_not_motivation_garnish.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-211` (future-beneficiary concern and obligation thin out across generational distance),
  - `RS-GR-212` (explicit intertemporal community links can improve intergenerational coordination),
  - `RS-GR-213` (reducing psychological distance can increase effortful climate action), and
  - `RS-GR-214` (future-self vividness can raise empathy yet produce mixed downstream action effects depending on agency/distress balance).
- Added one compact local receipt:
  - `artifacts/process/future_horizon_and_vividness_contracts_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to publish successor binding and future-beneficiary representation.
The next missing layer is that future-facing worlds can still hide two more design choices too easily.

- `RS-GR-211` warns that “future generations” is not one flat target; beneficiary horizon depth itself changes concern and obligation pressure.
- `RS-GR-212`, `RS-GR-213`, and `RS-GR-214` warn that intertemporal links, psychological proximity, and future-self vividness can change future-facing behavior, but not always in a simple monotone direction.

So the next implementor should avoid two more easy mistakes:

1. treating next-generation, seventh-generation, and far-future beneficiary worlds as one generic future-facing benchmark;
2. treating future-beneficiary vividness or cross-cohort linkage as harmless presentation detail instead of as part of the institution.

### Recommended next move

1. If Concord builds a future-facing lane, publish exact cohort-distance semantics beside any “future generations” headline.
2. Compare at least one near-horizon and one farther-horizon beneficiary variant before treating sustainability gains as norm progress.
3. Keep one low-link / low-vividness baseline beside any future-beneficiary world that uses continuity cues, future-self prompts, or psychologically proximal framing.

## Additional compact pass: future-duty framing, support visibility, and legacy-type contracts

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/future_responsibility_framing_and_support_visibility_are_world_contracts_not_just_messaging.md`
  - `docs/LIBRARY/topics/legacy_motive_type_and_action_visibility_are_world_contracts_not_one_future_care_knob.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-215` (future-generations responsibility can be widely endorsed and less tightly tied to ideology than rival climate-duty frames),
  - `RS-GR-216` (future-generations responsibility versus climate-responsibility framing in six European countries),
  - `RS-GR-217` (support for future-generations institutions can be widespread yet underestimated, and norm correction increases support),
  - `RS-GR-218` (impact legacy and reputation legacy are behaviorally distinct and visibility-sensitive), and
  - `RS-GR-219` (intergenerational letter framing can move immediate intentions and donations while decaying over time).
- Added one compact local receipt:
  - `artifacts/process/future_duty_frame_support_visibility_and_legacy_type_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to publish future-beneficiary representation, horizon depth, and vividness.
These sources add the missing **future-duty frame / support-visibility / legacy-type layer** underneath them.

- `RS-GR-215` and `RS-GR-216` warn that responsibility-to-future-generations framing is not equivalent to other climate-duty frames; it can travel differently across ideological and national contexts.
- `RS-GR-217` warns that uptake of future-facing institutions depends partly on what agents think everyone else supports; pluralistic ignorance can suppress action even when actual support is high.
- `RS-GR-218` warns that impact legacy and reputation legacy are distinct mechanisms, and that visibility changes what legacy prompts actually buy.
- `RS-GR-219` warns that intergenerational framing can move immediate intentions and giving without necessarily producing durable behavior change.

So the next implementor should avoid three more easy mistakes:

1. treating future-generations duty framing as harmless wording rather than as part of the institution;
2. treating hidden versus corrected support norms for future-facing institutions as political background rather than as a causal dial;
3. treating any immediate post-prompt legacy effect as if it were a durable Golden-Rule improvement.

### Recommended next move

1. If Concord builds a future-facing policy lane, keep one explicit future-generations-responsibility frame and one neutral or alternate-frame baseline side by side.
2. Add one support-visibility companion comparison that reports actual support, perceived support, and whether norm correction was shown.
3. For any legacy prompt, publish impact-versus-reputation target, action observability, and at least one delayed follow-up before generalizing from the immediate effect.



## Additional compact pass: positive-future imagination, efficacy, and distress-channeling contracts

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/positive_future_imaginability_collective_efficacy_and_emotional_valence_are_world_contracts_not_one_hope_dial.md`
  - `docs/LIBRARY/topics/distress_channeling_and_coping_scaffolds_are_world_contracts_not_emotional_side_effects.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-220` (positive future imagination and efficacy beliefs as distinct correlates of individual and collective conservation intentions),
  - `RS-GR-221` (the strongest climate-advocacy intervention pairing collective efficacy with emotional benefits),
  - `RS-GR-222` (utopian versus dystopian future visions working through different positive-emotion pathways),
  - `RS-GR-223` (future-facing distress suppressing or mobilizing behavior depending on meaning-focused coping), and
  - `RS-GR-224` (action plus efficacy-based hope being psychologically different from action without hope).
- Added one compact local receipt:
  - `artifacts/process/positive_future_and_distress_channeling_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to publish future-beneficiary representation, horizon depth, vividness, duty framing, support visibility, and legacy type.
These sources add the missing **imaginability / achievability / distress-channeling layer** underneath them.

- `RS-GR-220`, `RS-GR-221`, and `RS-GR-222` warn that a future-facing world can become more motivating because it makes a positive future imaginable, believable, emotionally rewarding, or collectively achievable — not because the reciprocity norm itself changed.
- `RS-GR-223` and `RS-GR-224` warn that future-facing worry is not a monotone motivator; distress can depress later action unless meaning-focused coping, agency, or efficacy-based hope changes how the burden is processed.

So the next implementor should avoid two more easy mistakes:

1. treating positive future imagination, collective efficacy, and emotional uplift as one generic hope cue;
2. treating worry or urgency as a standalone motivator without publishing the coping and agency scaffold that channels it.

### Recommended next move

1. Keep one no-vision / no-efficacy baseline beside any future-facing lane that uses utopian stories, positive scenarios, or explicit action-achievability cues.
2. Publish whether a future-facing lane changes desirability, perceived possibility, collective efficacy, emotional payoff, or some combination.
3. Keep one low-scaffold baseline beside any urgent or burden-heavy future-facing lane, and record whether behavior changes survive a delayed follow-up rather than only the immediate prompt window.


## Additional compact pass: present-day solidarity and burden-scale fairness contracts

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/present_day_solidarity_and_future_regard_are_world_contracts_not_a_fixed_moral_tradeoff.md`
  - `docs/LIBRARY/topics/burden_sharing_scale_and_fairness_reference_groups_are_world_contracts_not_one_justice_scalar.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-225` (future concern predicting costly present-day prosociality and extraordinary altruism),
  - `RS-GR-226` (intergenerational climate-justice awareness shaping support for deep decarbonisation through willingness to bear near-term losses),
  - `RS-GR-227` (net-zero policy support hinging on distributive fairness for future generations, low-income households, and rural communities), and
  - `RS-GR-228` (climate-policy support tracking household and local-community impacts more than abstract societal fairness in the Nordic region).
- Added one compact local receipt:
  - `artifacts/process/present_solidarity_and_burden_scale_fairness_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to publish future-beneficiary representation, horizon depth, vividness, duty framing, support visibility, legacy type, positive-future imagination, and distress scaffolds.
These sources add the missing **present-cost alignment / fairness-reference-group layer** underneath them.

- `RS-GR-225` warns that future concern need not crowd out present-day costly helping; future-facing morality can coexist with immediate solidarity.
- `RS-GR-226` warns that intergenerational-justice support is still partly a question of who accepts near-term losses, so future-duty worlds are also sacrifice-allocation worlds.
- `RS-GR-227` and `RS-GR-228` warn that fairness talk is underspecified unless the benchmark says fairness for whom and at what scale burdens are experienced.

So the next implementor should avoid two more easy mistakes:

1. treating future concern as if it automatically competes with present-day helping, without running a matched-cost present-beneficiary comparison;
2. treating fairness as one scalar label when household, local, subgroup, societal, and future-generation fairness can point in different directions.

### Recommended next move

1. Keep one matched-cost present-beneficiary companion lane beside any future-beneficiary costly-help or sacrifice lane.
2. Publish whether the main outcome is symbolic support, real costly helping, extraordinary altruism, or willingness to accept near-term losses.
3. Keep one same-payoff comparison where only the fairness reference group changes across household/local, vulnerable-subgroup, societal, and future-generation framings.



## Additional compact pass: descendant-specific framing and bidirectional intergenerational influence contracts

### What changed

- Added two compact inheritor-facing research notes:
  - `docs/LIBRARY/topics/descendant_specific_beneficiary_framing_and_kinship_scope_are_world_contracts_not_generic_future_regard.md`
  - `docs/LIBRARY/topics/intergenerational_dialogue_and_bidirectional_influence_are_world_contracts_not_one_way_moral_instruction.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-229` (children / grandchildren standpoint-taking shifting policy preferences away from burdening future generations),
  - `RS-GR-230` (parenthood heightening climate concern while also increasing present household frictions and emissions pressures),
  - `RS-GR-231` (youth-led dialogue surfacing silences, empathy, and collaboration across generations),
  - `RS-GR-232` (reverse environmental transmission from younger to older family members conditioned by communication quality and receptivity), and
  - `RS-GR-233` (intergenerational programs improving social inclusion, cohesion, wellbeing, and ageism reduction).
- Added one compact local receipt:
  - `artifacts/process/descendant_scope_and_intergenerational_dialogue_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to publish future-beneficiary representation, horizon depth, vividness, duty framing, support visibility, legacy type, positive-future imagination, distress scaffolds, present-cost alignment, and fairness reference groups.
These sources add the missing **kinship-scope / caregiver-role / bidirectional-voice layer** underneath them.

- `RS-GR-229` and `RS-GR-230` warn that care for one's children or grandchildren is not interchangeable with care for anonymous future people; descendant-linked framing and caregiver-role activation can change both moral salience and present-day burden structure.
- `RS-GR-231`, `RS-GR-232`, and `RS-GR-233` warn that intergenerational cooperation can rise because dialogue becomes reciprocal, younger people influence older people, or structured contact reduces ageism and increases cohesion — not necessarily because the core reciprocity norm improved.

So the next implementor should avoid two more easy mistakes:

1. treating child / grandchild / family-anchored future concern as if it were universal future regard;
2. treating intergenerational contact as neutral background rather than as a causal dial over voice symmetry, influence direction, and stereotype repair.

### Recommended next move

1. Keep one matched-cost abstract-future baseline beside any child / grandchild / caregiver-activated future-beneficiary lane.
2. Publish whether family-role activation also changes household costs, mobility, or other practical constraints.
3. Keep one one-way-instruction baseline beside any youth-led or reciprocal intergenerational dialogue lane, and record whether effects survive beyond first-contact empathy.

## Additional compact pass: future voice insertion and rolling stewardship burden contracts

Files touched:
- added:
  - `docs/LIBRARY/topics/future_voice_insertion_and_throughput_accountability_are_world_contracts_not_representation_theater.md`
  - `docs/LIBRARY/topics/problem_shifting_and_rolling_stewardship_burdens_are_world_contracts_not_green_aftercare.md`
  - `artifacts/process/future_voice_and_rolling_stewardship_receipt_20260322.json`
- updated:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

Sources added:
- `RS-GR-234` (future design as a practical way to voice future generations in policymaking),
- `RS-GR-235` (future-regarding institutions contributing through input, throughput, and output legitimacy),
- `RS-GR-236` (soft intergenerational advice from institutional actors improving sustainability without hard enforcement),
- `RS-GR-237` (many constitutions and policy documents recognizing future generations without thereby guaranteeing procedural voice),
- `RS-GR-238` (climate policies producing sectoral, geographical, and temporal problem shifts, including future burden intensification), and
- `RS-GR-239` (transgenerational projects differing in rolling-maintenance burden, passive safety, and dependency on successor agency).

Why this tranche matters:
- `RS-GR-234`, `RS-GR-235`, `RS-GR-236`, and `RS-GR-237` warn that a world can look future-regarding because future beneficiaries were procedurally inserted into the present, because long-horizon accountability improved, or because advisory institutions existed — not because the underlying reciprocity norm improved.
- `RS-GR-238` and `RS-GR-239` warn that sustainable-looking policies can still export burdens across sectors, regions, and time or rely on indefinite successor maintenance, so a green headline is not the same thing as a reduced intergenerational burden.

Concrete benchmark consequences:
1. Publish whether future beneficiaries are merely named, role-played, advisory-represented, or backed by stronger scrutiny / accountability machinery in the present decision process.
2. Publish what those institutions can actually do: narrate, advise, audit, trigger transparency, set agenda, vote, veto, or override.
3. Publish whether a sustainability lane reduces burden in place or shifts it across sectors, geographies, time, or rolling successor upkeep.
4. Keep one no-voice baseline and one low-maintenance / low-problem-shift baseline beside any stronger future-voice or open-ended stewardship world before attributing gains to Golden-Rule progress.



## Additional compact pass: deliberative-depth / institutional-teeth and value-pluralism / option-preserving-portfolio contracts

Added a compact future-governance tranche focused on two missing seams in the intergenerational program map:
- whether future-facing institutions merely add seats, actually deepen deliberation, or acquire formal leverage when ignored; and
- whether long-horizon governance optimizes one guessed future or preserves option value under uncertainty about future values.

New sources added:
- `RS-GR-240` (participatory governance helping long-term environmental problems mainly through intensive deliberation rather than simple interest representation),
- `RS-GR-241` (future-generation proxy institutions varying by type, access, and legal teeth, with many lacking watchdog capacity when ignored),
- `RS-GR-242` (long-term governance involving unknown unknowns, value uncertainty, and control-over-time problems), and
- `RS-GR-243` (value pluralism supporting portfolio, laddered, and inclusive approaches rather than one single optimized path).

Why this matters:
- `RS-GR-240` and `RS-GR-241` warn that a world can look more future-regarding because discussion became more intensive, because future-facing actors were seated at the table, or because an institution gained formal leverage — not because the base reciprocity norm improved.
- `RS-GR-242` and `RS-GR-243` warn that a world can look more future-protective because it locked in one assumed value system, because it preserved a diversified option set for successors, or because it explicitly allowed later reweighting under uncertainty.

Threaded follow-through in the archive:
1. Added a topic note on deliberative depth versus institutional teeth.
2. Added a topic note on value pluralism versus one locked future.
3. Extended the agenda/opinions/inheritor brief with compact implementor-facing implications.
4. Added a small machine-readable receipt for this tranche.

## Additional compact pass: lifespan-boundary timing and threshold-trigger contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/own_lifetime_payoff_boundaries_and_temporal_policy_discounting_are_world_contracts_not_generic_future_concern.md`
  - `docs/LIBRARY/topics/significant_harm_floors_and_triggered_revision_rights_are_world_contracts_not_smooth_future_management.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-244` (lifespan-structured policy discounting),
  - `RS-GR-245` (time horizons and policy support),
  - `RS-GR-246` (significant-harm thresholds / just boundaries),
  - `RS-GR-247` (adaptation tipping-point categories),
  - `RS-GR-248` (thresholds as decision points in resilience pathways), and
  - `RS-GR-249` (dynamic pathways with target points and critical decisions over time).
- Added one compact local receipt:
  - `artifacts/process/lifespan_boundary_and_threshold_trigger_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish beneficiary scope, horizon depth, vividness, proxy voice, institutional teeth, and value pluralism.
These sources add two more missing layers underneath them.

- `RS-GR-244` and `RS-GR-245` warn that a world can look more future-regarding because benefits moved inside the actor's own lifespan or because personal time horizons were lengthened before the same choice.
- `RS-GR-246`, `RS-GR-247`, `RS-GR-248`, and `RS-GR-249` warn that a world can look more protective because it imposes hard harm floors, threshold categories, and formal review / switching triggers rather than because the base reciprocity rule improved.

So the next implementor should avoid two more easy mistakes:

1. treating within-lifetime, edge-of-lifetime, and mainly posthumous payoffs as one generic future-benefit structure;
2. treating threshold protection and trigger-based revision as operational aftercare rather than as part of the institution itself.

### Recommended next move

1. Keep one matched-benefit within-lifetime baseline beside any beyond-lifetime future-beneficiary world.
2. Publish whether caregiver / descendant salience changed personal time horizons before the decision.
3. Keep one smooth-tradeoff / no-trigger baseline beside any hard-floor or trigger-driven stewardship lane.
4. Publish who owns threshold monitoring, who can reopen the path, and what switching authority exists once a trigger is hit.

## Additional compact pass: representative-source and cross-cycle-memory contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/representative_selection_route_and_cohort_composition_are_world_contracts_not_generic_future_voice.md`
  - `docs/LIBRARY/topics/permanence_institutional_anchor_and_cross_cycle_memory_are_world_contracts_not_administrative_aftercare.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-250` (democratic legitimacy of self-proclaimed / non-electoral future representation),
  - `RS-GR-251` (hypothetical-acceptance and representative-selection criteria for future generations),
  - `RS-GR-252` (youth under-representation in formal politics),
  - `RS-GR-253` (conditions for meaningful youth / proxy participation in intergenerational justice work),
  - `RS-GR-254` (pitfalls of anticipatory governance under fragmentation and resilience drift),
  - `RS-GR-255` (anticipatory-governance endurance, procedures, and cross-cycle continuity),
  - `RS-GR-256` (institutional anchors, permanence, and accountability loops in participation systems), and
  - `RS-GR-257` (reflexive long-term governance across sectors, institutions, and temporal scales).
- Added one compact local receipt:
  - `artifacts/process/representative_source_and_cross_cycle_memory_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish future voice, institutional teeth, value pluralism, lifespan boundaries, and threshold-trigger semantics.
These sources add two more missing layers underneath them.

- `RS-GR-250`, `RS-GR-251`, `RS-GR-252`, and `RS-GR-253` warn that a world can look more future-representative because the proxy class changed — toward youth, affected communities, better cohort balance, or a more contestable non-electoral representative device — rather than because the underlying reciprocity norm improved.
- `RS-GR-254`, `RS-GR-255`, `RS-GR-256`, and `RS-GR-257` warn that a world can look more future-protective because the institution became permanent, gained an anchor agency, closed an accountability loop, or preserved memory across political cycles rather than because present actors became more principled.

So the next implementor should avoid two more easy mistakes:

1. treating all future-beneficiary proxies as one generic representation mechanism;
2. treating one-off consultation and durable, memory-preserving long-term governance as the same institution.

### Recommended next move

1. Keep one same-power comparison where only proxy source or selection route changes.
2. Publish age composition, diversity, and challenge / replacement rules for future-facing representatives.
3. Keep one ad-hoc / no-anchor baseline beside any permanent or auto-renewing future-participation institution.
4. Publish how recommendations travel, who must answer them, and what learning survives across leadership turnover.

## Additional compact pass: future-impact accounting and valuation-rule contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/future_impact_accounting_and_public_reason_giving_are_world_contracts_not_generic_future_concern.md`
  - `docs/LIBRARY/topics/discount_schedule_and_valuation_rule_are_world_contracts_not_moral_progress.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-258` (EU intergenerational fairness strategy: youth check, foresight, index, progress reporting),
  - `RS-GR-259` (Futures Balance and explicit comparable long-term trade-offs),
  - `RS-GR-260` (Welsh monitoring / assessment / examination cadence),
  - `RS-GR-261` (Audit Wales on weak explicit consideration and weak impact understanding),
  - `RS-GR-262` (OECD future-facing regulatory impact assessment),
  - `RS-GR-263` (discount-guidance changes materially reweighting long-run harms),
  - `RS-GR-264` (demographic change altering social discounting), and
  - `RS-GR-265` (future bias altering the appropriate social discount rate for public investment).
- Added one compact local receipt:
  - `artifacts/process/future_impact_accounting_and_valuation_rule_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish future voice, deliberative depth, permanence, thresholds, and beneficiary scope.
These sources add two more missing layers underneath them.

- `RS-GR-258`, `RS-GR-259`, `RS-GR-260`, `RS-GR-261`, and `RS-GR-262` warn that a world can look more future-regarding because it forced future effects into templates, comparable trade-off surfaces, written-response routes, recurring examination, or progress-report cycles rather than because the underlying reciprocity norm improved.
- `RS-GR-263`, `RS-GR-264`, and `RS-GR-265` warn that a world can look more future-protective because the valuation rule placed more weight on the far future — via a lower or different discount schedule, altered capital treatment, or different demographic / future-bias assumptions — rather than because actors became more morally expansive.

So the next implementor should avoid two more easy mistakes:

1. treating generic future language and explicit future-impact accounting as the same institutional world;
2. treating a different long-horizon valuation rule as the same thing as deeper intergenerational virtue.

### Recommended next move

1. Keep one same-choice comparison where only future-impact accounting / public reason-giving is added or removed.
2. Publish which future-facing dimensions are scored, narrated, escalated, or revisited after the decision.
3. Keep one same-behavior comparison where only the discount / valuation rule changes.
4. Publish discount schedule, capital treatment, demographic assumptions, and any threshold overrides beside every long-horizon welfare claim.

## Additional compact pass: future-rights / remedy and precaution / proof-burden contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/future_generations_rights_standing_and_remedy_routes_are_world_contracts_not_symbolic_recognition.md`
  - `docs/LIBRARY/topics/precautionary_defaults_and_burden_of_proof_under_irreversible_risk_are_world_contracts_not_generic_future_care.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-266` (future generations as potential rights-holders under ICESCR),
  - `RS-GR-267` (implementation-forcing / target-setting / oversight / procedural-access remedy types),
  - `RS-GR-268` (global climate-litigation scale and governance role),
  - `RS-GR-269` (broad standing, evidentiary easing, and reparations in the IACtHR climate opinion),
  - `RS-GR-270` (ICJ due diligence, best-available science, precaution, enforceability, and reparations),
  - `RS-GR-271` (binding adaptation due diligence, best science, and forward-looking precaution),
  - `RS-GR-272` (precautionary pause under uncertainty and irreversible harm to future generations), and
  - `RS-GR-273` (proof-burden shift plus proactive prevention for long-latency contaminants).
- Added one compact local receipt:
  - `artifacts/process/future_rights_and_precaution_proof_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish future voice, deliberative depth, future-impact accounting, valuation rules, and threshold-trigger semantics.
These sources add two more missing layers underneath them.

- `RS-GR-266`, `RS-GR-267`, `RS-GR-268`, `RS-GR-269`, and `RS-GR-270` warn that a world can look more future-protective because future beneficiaries gained a stronger legal status, a representative route, broad standing, lower evidentiary barriers, or implementation-forcing remedies rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-270`, `RS-GR-271`, `RS-GR-272`, and `RS-GR-273` warn that a world can look more careful or farsighted because it changed the uncertainty default — toward best-available-science due diligence, precaution, or reversed proof burdens — rather than because actors suddenly cared more about posterity.

So the next implementor should avoid two more easy mistakes:

1. treating symbolic recognition of future generations as equivalent to enforceable future-protection pathways;
2. treating stricter precaution or shifted proof burdens as evidence of moral improvement rather than as a world-rule change under uncertainty.

### Recommended next move

1. Keep one declaration-only / no-standing baseline beside any lane with broad standing or implementation-forcing remedies.
2. Publish who may act for future beneficiaries, what proof barriers they face, and what remedies can actually compel follow-through.
3. Keep one wait-for-proof baseline beside any precautionary or shifted-proof-burden lane.
4. Publish irreversible-harm triggers, science thresholds, and the actor who must prove safety before risky long-horizon activity proceeds.

### Compact archive-integrity repair

- Restored 23 inherited missing `artifacts/reports/rematch_proxy_*_20260306.*` paths as explicit retained-path placeholders so risk/spec ledgers resolve again without reintroducing bulky historical snapshots.
- Added compact receipt:
  - `artifacts/process/rematch_proxy_placeholder_restoration_receipt_20260322.json`
- These placeholders are **not** substantive evidence; they preserve handoff continuity until a future session regenerates or replaces the original March 6 snapshot family with tighter modern equivalents.


## Additional compact pass: avoidance-first / substitutability and robust-no-regret contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/avoidance_first_substitutability_and_restoration_order_are_world_contracts_not_generic_future_protection.md`
  - `docs/LIBRARY/topics/robust_no_regret_and_option_keeping_under_deep_uncertainty_are_world_contracts_not_generic_prudence.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-274` (irreversibility and reversibility depend on scale and are often left undefined),
  - `RS-GR-275` (strengthening avoidance and proactive enhancement in SEA / EIA),
  - `RS-GR-276` (limited avoidance, weak remediation, and substitutability limits in real-world EIA practice),
  - `RS-GR-277` (full restoration at sufficient scale versus fragmented mitigation),
  - `RS-GR-278` (scenario-building and stress-testing for robust and adaptable public policy),
  - `RS-GR-279` (robust decision methods surfacing trade-offs and vulnerabilities under deep uncertainty),
  - `RS-GR-280` (catalogue of DMDU tools / resources with limited practical uptake), and
  - `RS-GR-281` (no-regret / low-regret / win-win versus high-regret adaptation classes and flexibility under uncertainty).
- Added one compact local receipt:
  - `artifacts/process/avoidance_order_and_robust_regret_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish future voice, valuation rules, threshold triggers, and precaution defaults.
These sources add two more missing layers underneath them.

- `RS-GR-274`, `RS-GR-275`, `RS-GR-276`, and `RS-GR-277` warn that a world can look more future-protective because it moved harm earlier in the hierarchy — toward upstream avoidance, stronger non-substitution rules, or larger-scale restoration — rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-278`, `RS-GR-279`, `RS-GR-280`, and `RS-GR-281` warn that a world can look more farsighted because it changed its uncertainty-management architecture toward robust, adaptive, no-regret, or option-preserving design rather than because actors suddenly cared more about posterity.

So the next implementor should avoid two more easy mistakes:

1. treating compensate-later repair worlds as equivalent to avoidance-first or non-substitutable-loss worlds;
2. treating robust / no-regret / adaptive-pathway design as evidence of moral improvement rather than as a change in planning architecture under uncertainty.

### Recommended next move

1. Keep one weak-avoidance / compensate-later baseline beside any avoidance-first or non-substitutable-loss lane.
2. Publish reversibility timescale, restoration order, ecological equivalence expectations, and what losses cannot be substituted away.
3. Keep one reference-scenario-optimal baseline beside any robust / no-regret / adaptive-pathway lane.
4. Publish stress-tested uncertainties, known vulnerabilities, and the exact devices used to preserve option value for successors.


## Additional compact pass: staged-commitment / reversibility and sunset / policy-stock-retirement contracts

### What changed

- Added two compact inheritor-facing notes:
  - `docs/LIBRARY/topics/staged_commitment_pilotability_and_reversibility_are_world_contracts_not_implementation_pacing.md`
  - `docs/LIBRARY/topics/sunset_reauthorization_and_policy_stock_retirement_are_world_contracts_not_housekeeping.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-282` (regulatory experimentation as deliberate adaptive-learning governance),
  - `RS-GR-283` (small-scale / temporary experimentation with scale-up or phase-out plus reflexive monitoring),
  - `RS-GR-284` (sandboxes, pilot regulation, policy labs, and experimentation clauses as anticipatory-governance tools),
  - `RS-GR-285` (temporary framing can raise approval and later extension of controversial measures),
  - `RS-GR-286` (policy accumulation and policy triage from overloaded implementation portfolios), and
  - `RS-GR-287` (ex post evaluation and assessment of alternatives as part of regulating for effectiveness).
- Added one compact local receipt:
  - `artifacts/process/staged_commitment_and_policy_stock_retirement_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish permanence, future voice, threshold triggers, and robustness / no-regret architecture.
These sources add two more missing layers underneath them.

- `RS-GR-282`, `RS-GR-283`, and `RS-GR-284` warn that a world can look more future-protective because it introduced staged commitment, reversible trialing, pilot regulation, or delayed lock-in rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-285`, `RS-GR-286`, and `RS-GR-287` warn that a world can look more careful because it used temporary framing, reauthorization discipline, or active retirement of policy stock — or can silently fail because obligations accumulated faster than implementation capacity — rather than because actors suddenly cared more about posterity.

So the next implementor should avoid two more easy mistakes:

1. treating pilotability, temporary experimentation, or delayed lock-in as equivalent to deeper reciprocity or future regard;
2. treating sunset labels as self-enforcing safeguards when extension incentives, stock accumulation, and implementation overload can still leave successors with durable burdens.

### Recommended next move

1. Keep one one-shot permanent baseline beside any piloted, reversible, or staged-commitment lane.
2. Publish scale-up, rollback, and phase-out criteria together with the real cost of reversal after deployment.
3. Keep one persist-until-repeal baseline beside any auto-expiring or affirmative-reauthorization lane.
4. Publish extension evidence standards and the implementation load added to the standing policy stock before calling a temporary world successor-friendly.


### 2026-03-22 research tranche - prefunding and deferred-maintenance visibility

Added the following source-backed materials:
- `RS-GR-288` (reserve-governance failure modes in public-segregated decommissioning funds),
- `RS-GR-289` (contingency, confidence, and correlation assumptions in long-horizon cost estimation),
- `RS-GR-290` (offshore financial-assurance architecture via credit thresholds, predecessor liability, and P-value choice),
- `RS-GR-291` (Australian decommissioning reforms linking liability responsibility to financial planning and assurance),
- `RS-GR-292` (deferred maintenance as accumulated liability when preservation falls below depreciation),
- `RS-GR-293` (asset inventories, condition assessments, and lifecycle costs as prerequisites for managing building backlogs),
- `RS-GR-294` (Asset Sustainability Index as a funding-adequacy metric that can stay below sufficiency even when trends improve),
- `RS-GR-295` (maintenance eligibility and contingent-liability transparency inside infrastructure-fund design), and
- `RS-GR-296` (deferred-maintenance backlogs as a first-class governance risk in federal real property).
- Added one compact local receipt:
  - `artifacts/process/prefunding_and_deferred_maintenance_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish successor binding, rolling stewardship burden, future accounting, and pilot / sunset semantics.
These sources add two more missing financial and condition-management layers underneath them.

- `RS-GR-288`, `RS-GR-289`, `RS-GR-290`, and `RS-GR-291` warn that a world can look more successor-friendly because it prefunded liabilities, ring-fenced reserves, raised assurance levels, or adopted more conservative cost-estimation assumptions rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-292`, `RS-GR-293`, `RS-GR-294`, `RS-GR-295`, and `RS-GR-296` warn that a world can look more prudent because it finally measured asset condition, depreciation, lifecycle cost, and backlog adequacy rather than because agents suddenly became more reciprocal toward the future.

So the next implementor should avoid two more easy mistakes:

1. treating prefunding or financial assurance architecture as interchangeable with deeper moral concern for successors;
2. treating hidden deterioration as neutral background wear when backlog visibility and condition ledgers often determine whether successor burdens are governable at all.

### Recommended next move

1. Keep one pay-as-you-go or weak-assurance baseline beside any prefunded, bonded, or reserve-segregated successor-liability lane.
2. Publish reserve governance, confidence level, update cadence, and explicit shortfall-bearer semantics together with any headline claims about future burden reduction.
3. Keep one opaque-condition baseline beside any asset-ledger-rich lane so maintenance visibility is not misread as virtue.
4. Publish depreciation / backlog logic and one funding-adequacy metric before treating infrastructure or stewardship worlds as sustainably cooperative.

### 2026-03-22 research tranche - verification contestability and renewable knowledge handoff

Added the following source-backed materials:
- `RS-GR-305` (community-based environmental monitoring as a condition of continuing acceptance),
- `RS-GR-306` (local monitoring access, inspection rights, independent annual audits, and dispute routes inside mining agreements),
- `RS-GR-307` (independent audit packets with evidence-linked rationales, stakeholder interviews, and continuity checks),
- `RS-GR-308` (EPA long-term-stewardship checklists as repeatable reassessment infrastructure),
- `RS-GR-309` (DOE Legacy Management record indexing and re-openability triggers for future custodians),
- `RS-GR-310` (Key Information File as an intelligible, renewable summary layer for future stewards),
- `RS-GR-311` (OECD NEA awareness preservation as an RK&M toolbox and stakeholder-dialogue strategy), and
- `RS-GR-312` (multi-media, multilingual, and periodically renewable deployment of a key-information package).
- Added one compact local receipt:
  - `artifacts/process/verification_contestability_and_renewable_handoff_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish future voice, standing, discounting, prefunding, and release semantics.
These sources add two more missing implementation layers beneath them.

- `RS-GR-305`, `RS-GR-306`, `RS-GR-307`, and `RS-GR-308` warn that a world can look more trustworthy or more successor-protective because evidence became independently verifiable, locally contestable, and periodically reassessed rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-309`, `RS-GR-310`, `RS-GR-311`, and `RS-GR-312` warn that a world can look more durable because future stewards received indexed records, intelligible key-information packages, renewal instructions, and dispersed awareness-preservation channels rather than because present actors became more reciprocal toward posterity.

So the next implementor should avoid two more easy mistakes:

1. treating independent verification and outsider challenge rights as interchangeable with deeper moral concern for successors;
2. treating searchable records or renewable key-information packages as neutral archival detail rather than as core world-contract machinery for deep-time stewardship.

### Recommended next move

1. Keep one self-report or weak-audit baseline beside any independently verified or publicly contestable stewardship lane.
2. Publish whether outsiders can inspect, comment, trigger review, and read the reasoning behind findings before attributing trust gains to reciprocity.
3. Keep one raw-records-only baseline beside any key-information or essential-records package so intelligibility is not misread as virtue.
4. Publish renewal cadence, media-migration duty, and re-openability triggers before treating successor stewardship as durably solved.

### 2026-03-22 research tranche - successor competence continuity and rehearsed roles

Added the following source-backed materials:
- `RS-GR-313` (DOE LM HCMP links long-term stewardship to succession planning, mission-critical knowledge preservation, staffing growth, and targeted training),
- `RS-GR-314` (DOE LM HPO plan treats staffing levels, technical capability, workforce planning, geographic distribution, and evaluation as core institutional architecture),
- `RS-GR-315` (DOE human-capital office treats succession planning, competency development, training, and retention as mission-supporting work),
- `RS-GR-316` (DOE strategic plan treats emergency-management exercises and drills as preparedness work),
- `RS-GR-317` (DOE/NNSA emergency-preparedness practice foregrounds exercised coordination, live-burn training, and FRMAC exercises), and
- `RS-GR-318` (DOE exercises-and-training program frames exercises as building preparedness and practicing defense and resilience).
- Added two compact inheritor-facing topic notes:
  - `docs/LIBRARY/topics/successor_competence_and_capability_continuity_are_world_contracts_not_record_retention.md`
  - `docs/LIBRARY/topics/rehearsed_roles_drills_and_exercised_interfaces_are_world_contracts_not_emergency_garnish.md`
- Added one compact local receipt:
  - `artifacts/process/successor_competence_and_rehearsed_roles_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to publish future voice, verification, renewable records, and prefunding semantics.
These sources add two more missing execution layers beneath them.

- `RS-GR-313`, `RS-GR-314`, and `RS-GR-315` warn that a world can look more durable because it preserved staffing depth, successor coverage, technical capability, training, and mission-critical knowledge continuity rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-316`, `RS-GR-317`, and `RS-GR-318` warn that a world can look more resilient because it trained, drilled, exercised, and corrected key roles and interfaces rather than because present actors suddenly cared more about posterity.

So the next implementor should avoid two more easy mistakes:

1. treating record retention as interchangeable with successor competence or live institutional capacity;
2. treating written procedures as sufficient when roles and interfaces have never been rehearsed under scenario pressure.

### Recommended next move

1. Keep one record-rich but thin-capability baseline beside any succession-planned, competency-rich stewardship lane.
2. Publish staffing depth, overlap, role redundancy, targeted training, and geographic coverage before calling a world successor-safe.
3. Keep one documented-playbook baseline beside any drilled or exercise-validated resilience lane.
4. Publish exercise type, cadence, interface coverage, and after-action correction duty before treating preparedness as durable stewardship.



### 2026-03-22 research tranche - interoperability portability and manual fallback

Added the following source-backed materials:
- `RS-GR-319` (DOE data strategy treats catalogs, metadata standards, APIs, persistent identifiers, and standardized retrieval protocols as prerequisites for interoperable long-horizon data use),
- `RS-GR-320` (current CISA guidance tells operators to prioritize open standards to avoid lock-in),
- `RS-GR-321` (OECD's El Co-Meta case uses common schemas, controlled vocabularies, persistent identifiers, and harvesting/synchronization to make repositories interoperable),
- `RS-GR-322` (FEMA's current planning guidance asks for alternate facilities, continuity communications, essential records, and human-capital continuity),
- `RS-GR-323` (NIST's GAI profile treats manual processing, tested fallback technologies, data redundancy, and vendor-termination contingencies as explicit controls),
- `RS-GR-324` (NIST contingency controls include orderly degradation, shutdown, manual mode fallback, alternate information flows, and alternate processing sites), and
- `RS-GR-325` (FEMA's federal response-and-recovery plan expects resilient communications and cross-jurisdictional backup capabilities).
- Added two compact inheritor-facing topic notes:
  - `docs/LIBRARY/topics/interoperability_open_standards_and_vendor_exit_are_world_contracts_not_data_plumbing.md`
  - `docs/LIBRARY/topics/manual_fallback_graceful_degradation_and_alternate_procedures_are_world_contracts_not_contingency_footnotes.md`
- Added one compact local receipt:
  - `artifacts/process/interoperability_and_manual_fallback_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve renewable records, successor competence, and rehearsed roles.
These sources add two more missing operating layers beneath them.

- `RS-GR-319`, `RS-GR-320`, `RS-GR-321`, and `RS-GR-325` warn that a world can look successor-safe because it became portable, standards-aligned, synchronizable, and practically escapable from vendor captivity rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-322`, `RS-GR-323`, `RS-GR-324`, and `RS-GR-325` warn that a world can look resilient because it preserved manual fallback, graceful degradation, alternate processing, and backup communications rather than because present actors suddenly cared more about posterity.

So the next implementor should avoid two more easy mistakes:

1. treating stored records as inheritable stewardship when semantics are trapped in bespoke or non-exportable systems;
2. treating documented continuity as sufficient when failure modes have no governable fallback or degraded-service promise.

### Recommended next move

1. Keep one captive-format / no-exit baseline beside any open-standard or interoperable stewardship lane.
2. Publish export fidelity, schema alignment, persistent identifiers, and practical vendor-exit rights before calling a world successor-safe.
3. Keep one hard-outage / automation-dependent baseline beside any manual-fallback or graceful-degradation lane.
4. Publish alternate facilities, alternate flows, essential-record survivability, and backup-communications assumptions before treating resilience as durable stewardship.


### 2026-03-22 research tranche - fixity migration and cryptographic agility

Added the following source-backed materials:
- `RS-GR-326` (NARA's digital preservation strategy treats fixity generation, annual fixity audits, file repair, preservation action plans, and format / media sustainability as core preservation architecture),
- `RS-GR-327` (NARA's quarterly framework updates show preservation action plans and format-risk intelligence are actively refreshed and republished),
- `RS-GR-328` (NARA's ISO 16363 self-assessment treats repository trustworthiness as a repeatedly audited maturity property rather than a one-time claim),
- `RS-GR-329` (NIST defines crypto agility as the ability to replace and adapt algorithms across protocols, applications, software, hardware, firmware, and infrastructure while preserving operations),
- `RS-GR-330` (NIST frames PQC migration as one instance of a broader recurring cryptographic-migration problem), and
- `RS-GR-331` (the NCCoE PQC FAQ organizes migration into awareness, planning, execution, and validation / monitoring stages and ties it to crypto agility).
- Added two compact inheritor-facing topic notes:
  - `docs/LIBRARY/topics/fixity_refresh_format_migration_and_preservation_action_plans_are_world_contracts_not_passive_retention.md`
  - `docs/LIBRARY/topics/cryptographic_agility_and_algorithm_transition_are_world_contracts_not_static_authenticity.md`
- Added one compact local receipt:
  - `artifacts/process/fixity_migration_and_crypto_agility_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve renewable records, interoperability, and manual fallback.
These sources add two more missing integrity layers beneath them.

- `RS-GR-326`, `RS-GR-327`, and `RS-GR-328` warn that a world can look durable because it refreshes fixity evidence, repairs corruption, revisits format risk, and updates preservation action plans rather than because the underlying Golden-Rule disposition improved.
- `RS-GR-329`, `RS-GR-330`, and `RS-GR-331` warn that a world can look trustworthy because it planned for algorithm transitions and recurring crypto migration rather than because present actors became more future-regarding.

So the next implementor should avoid two more easy mistakes:

1. treating stored bytes as preserved stewardship when integrity checking, repair duty, and format sustainability are absent after ingest;
2. treating present-day signatures or cryptographic envelopes as permanently trustworthy when successors inherit no migration-ready cryptographic plan.

### Recommended next move

1. Keep one ingest-only / passive-retention baseline beside any recurring-fixity or migration-planned stewardship lane.
2. Publish fixity-audit cadence, repair authority, format-risk review cycle, and action-plan refresh duty before calling a world archival-safe.
3. Keep one static-crypto baseline beside any crypto-agile or algorithm-transition-ready lane.
4. Publish cryptographic inventory, migration stages, validation / monitoring duty, and future-transition assumptions before treating authenticity as successor-safe.

### 2026-03-22 research tranche - trust-anchor rotation and delegated authority

Added the following source-backed materials:
- `RS-GR-332` (NIST key-management guidance treats trust anchors, inventory, cryptoperiods, backup, compromise, and recovery as part of core key management),
- `RS-GR-333` (ICANN's 2024 DNSSEC trust-anchor announcement uses prepublication, long standby windows, and vendor/package distribution coordination ahead of the 2026 rollover),
- `RS-GR-334` (RFC 5011 specifies automated authenticated trust-anchor updates, revocation, hold-down, and N-1 compromise protection, while still leaving some cases to manual or other out-of-band recovery), and
- `RS-GR-335` (the 2026 TUF specification keeps root keys offline, uses threshold trust and revocable delegation, and requires out-of-band recovery when a threshold of root keys is compromised).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/trust_anchor_rotation_delegated_authority_and_recovery_paths_are_world_contracts_not_static_provenance.md`
- Added one compact local receipt:
  - `artifacts/process/trust_anchor_rotation_and_delegated_authority_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve interoperability, fallback, fixity, and crypto agility.
These sources add one more missing authority layer beneath them.

- `RS-GR-332`, `RS-GR-333`, `RS-GR-334`, and `RS-GR-335` warn that a world can look more successor-safe because it published trust-anchor lifetimes, staged root rollover, thresholded delegation, and out-of-band recovery rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating current signatures or provenance roots as durable stewardship when the archive has no explicit trust-rotation, delegation, revocation, or emergency-recovery contract.

### Recommended next move

1. Keep one static-root / ad hoc recovery baseline beside any rotation-ready trust lane.
2. Publish cryptoperiod, propagation window, delegation thresholds, revocation rights, and out-of-band recovery owner before calling a world successor-safe.

### 2026-03-22 research tranche - transparency logs and monitor plurality

Added the following source-backed materials:
- `RS-GR-336` (RFC 9162 distinguishes inclusion proofs from consistency proofs and uses the latter to verify append-only log history),
- `RS-GR-337` (the Certificate Transparency deployment story shows that mandatory public logging changes incentives by making misissued records openly discoverable rather than relying on private audits alone),
- `RS-GR-338` (Certificate Transparency names monitors as a distinct actor that checks logged-record visibility and watches for suspicious entries),
- `RS-GR-339` (Sigstore treats signing events as recorded in an immutable append-only log, expects proof-of-inclusion verification, and expects auditors and identity owners to monitor that log), and
- `RS-GR-340` (the current SCITT architecture supports multiple independent transparency services and receipts, warns against trusting a single centralized service, and tells relying parties not to accept statements without discoverable receipts from a service they trust).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/transparency_logs_inclusion_proofs_and_monitor_plurality_are_world_contracts_not_static_provenance.md`
- Added one compact local receipt:
  - `artifacts/process/transparency_logs_and_monitor_plurality_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve trust-anchor rotation, crypto agility, and fixity.
These sources add one more missing publication-and-audit layer beneath them.

- `RS-GR-336`, `RS-GR-337`, `RS-GR-338`, `RS-GR-339`, and `RS-GR-340` warn that a world can look more successor-safe because it made provenance tamper-evident, inclusion-verifiable, monitored, and redundant across multiple transparency services rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a signed statement or one log receipt as durable provenance when the archive has no explicit append-only history check, monitor coverage, selective-submission rule, or multi-service trust policy.

### Recommended next move

1. Keep one signed-but-unlogged / single-service baseline beside any append-only monitored provenance lane.
2. Publish inclusion-proof, consistency-proof, receipt-discovery, monitor-cadence, and selective-submission semantics before calling a world successor-safe.
3. When practical, keep one multi-service or multi-receipt companion lane beside any single-log design.

### 2026-03-22 research tranche - witnessed checkpoints and split-view resistance

Added the following source-backed materials:
- `RS-GR-341` (the C2SP witness protocol requires logs to present checkpoints plus consistency proofs to witnesses, which only cosign append-only evolution from previously observed state),
- `RS-GR-342` (ArmoredWitness frames witness countersigning as split-view protection and emphasizes diverse custodianship across ecosystems),
- `RS-GR-343` (Sigsum publishes an explicit witness quorum rule in its trust policy rather than treating witness presence as enough),
- `RS-GR-344` (Witness Network shows that sustainable anti-equivocation also depends on community-governed witness discovery and onboarding), and
- `RS-GR-345` (Apple's Contact Key Verification has user devices verify inclusion and consistency, cross-check data across a user's own devices, and gossip log hashes to detect split views).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/witnessed_checkpoints_split_view_resistance_and_cross_perspective_consistency_are_world_contracts_not_just_append_only_logs.md`
- Added one compact local receipt:
  - `artifacts/process/witnessed_checkpoints_and_split_view_resistance_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve append-only logging, inclusion proofs, monitor plurality, and trust-anchor rotation.
These sources add one more missing anti-equivocation layer beneath them.

- `RS-GR-341`, `RS-GR-342`, `RS-GR-343`, `RS-GR-344`, and `RS-GR-345` warn that a world can look more successor-safe because it changed checkpoint witnessing, quorum thresholds, cross-device or peer consistency checks, gossip, and split-view escalation rules rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating one append-only log or one receipt as durable shared reality when the archive has no explicit witness quorum, cross-perspective consistency path, or equivocation response contract.

### Recommended next move

1. Keep one append-only-but-unwitnessed baseline beside any witness-quorum provenance lane.
2. Publish witness topology, onboarding / configuration path, quorum thresholds, and bundled-checkpoint verification semantics before calling a world successor-safe.
3. When practical, keep one client-self-audit or gossip companion lane beside any third-party-monitor-only design.

### 2026-03-22 research tranche - temporal validity and secure time

Added the following source-backed materials:
- `RS-GR-346` (RFC 3161 defines timestamps as proof that data existed before a particular time, requires a trustworthy source of time, and notes that two TSAs can help mitigate compromise risk),
- `RS-GR-347` (RFC 4998 defines renewable evidence records for long or undetermined periods of time and requires timestamp or hash-tree renewal when temporal evidence or hash assumptions weaken),
- `RS-GR-348` (Uptane requires clients to load the current or latest securely attested time and compare it against metadata expiration to detect freeze attacks),
- `RS-GR-349` (Uptane deployment guidance says devices need a secure time bootstrap at startup and explains that bad time can make good metadata look expired or stale metadata look current), and
- `RS-GR-350` (the current Roughtime draft provides authenticated rough time without an initial clock and gives clients cryptographic evidence when time servers disagree or misbehave).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/temporal_validity_secure_time_and_renewable_evidence_are_world_contracts_not_just_valid_signatures.md`
- Added one compact local receipt:
  - `artifacts/process/temporal_validity_and_secure_time_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve trust-anchor rotation, append-only logging, and witness-backed anti-equivocation.
These sources add one more missing temporal-validity layer beneath them.

- `RS-GR-336`, `RS-GR-346`, `RS-GR-347`, `RS-GR-348`, `RS-GR-349`, and `RS-GR-350` warn that a world can look more successor-safe because it changed freshness windows, publication latency, securely attested time, timestamp renewal, or renewable evidence maintenance rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a valid signature, receipt, or checkpoint as durable stewardship when the archive has no explicit freshness window, trusted time bootstrap, or renewable temporal-evidence contract.

### Recommended next move

1. Keep one timeless / weak-clock baseline beside any expiry-bounded or attested-time provenance lane.
2. Publish freshness windows, time-source bootstrap path, and stale-proof behavior before calling a world successor-safe.
3. When evidence must last across long dormancy or cryptographic turnover, publish the renewal trigger and renewable-evidence path instead of assuming one timestamp lasts forever.

### 2026-03-22 research tranche - portable evidence packets and offline verification

Added the following source-backed materials:
- `RS-GR-351` (RFC 9162 makes inclusion and consistency proofs verifiable against signed tree heads, so compact proof objects plus checkpoints can stand in for re-downloading whole logs),
- `RS-GR-352` (the current COSE receipts draft defines concise encodings for Merkle inclusion and consistency proofs, making portable proof packets a standardized object rather than a one-off export),
- `RS-GR-353` (the current SCITT architecture treats receipts as offline universally verifiable proofs of registration and allows already-transparent statements to be re-registered on another service),
- `RS-GR-354` (Sigstore defines a bundle as everything required to verify a signature on an artifact and lets it embed transparency-log entries, timestamps, proofs, and checkpoints),
- `RS-GR-355` (Sigstore keyless blob signing requires storing the bundle for later verification and is standardizing that bundle across clients), and
- `RS-GR-356` (the Sigstore Go client supports bundle verification, online and offline Rekor verification, TUF support, and custom trusted roots).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/portable_evidence_packets_offline_verification_and_dependency_survival_are_world_contracts_not_just_live_service_validation.md`
- Added one compact local receipt:
  - `artifacts/process/portable_evidence_packets_and_offline_verification_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve trust-anchor rotation, append-only logging, witnessed checkpoints, and secure time.
These sources add one more missing portability layer beneath them.

- `RS-GR-351`, `RS-GR-352`, `RS-GR-353`, `RS-GR-354`, `RS-GR-355`, and `RS-GR-356` warn that a world can look more successor-safe because it changed portable evidence packets, offline-verification coverage, retained trust roots, or service-loss survivability rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating currently successful live verification as durable stewardship when the archive does not actually retain the compact bytes and trust policy needed to verify after the original services disappear.

### Recommended next move

1. Keep one live-service-dependent baseline beside any self-contained bundle / receipt provenance lane.
2. Publish the exact retained verification bytes, offline-verification scope, and trust-root survival path before calling a world successor-safe.
3. When practical, keep one re-registration / re-anchoring companion lane beside any design that assumes one transparency or identity service will outlive the archive.

### 2026-03-22 research tranche - verifier policy snapshots and deterministic appraisal

Added the following source-backed materials:
- `RS-GR-357` (RFC 9334 separates Appraisal Policy for Evidence from Appraisal Policy for Attestation Results, so evidence does not interpret itself),
- `RS-GR-358` (the current SCITT architecture makes registration policies and trust anchors transparent, applies the policy committed at registration time, and requires enough information to reproduce historical checks),
- `RS-GR-359` (the current TUF specification makes clients ship configured trusted roots, evaluate thresholded roles and delegations, and revoke delegations via new metadata),
- `RS-GR-360` (Sigstore verification requires explicit identity / issuer constraints for keyless signatures and can verify signatures while skipping claims),
- `RS-GR-361` (Sigstore policy-controller validates signatures and attestations while applying cue / rego policies and configurable TrustRoots), and
- `RS-GR-362` (the current CoRIM draft specifies deterministic verifier reconciliation and requires profiles to describe expected verifier behavior at the relevant profile-dependent points).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/verifier_policy_snapshots_deterministic_appraisal_and_trust_profile_portability_are_world_contracts_not_just_portable_evidence.md`
- Added one compact local receipt:
  - `artifacts/process/verifier_policy_snapshots_and_deterministic_appraisal_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to retain portable receipts, trust roots, and offline-verification paths.
These sources add one more missing interpretation layer beneath them.

- `RS-GR-357`, `RS-GR-358`, `RS-GR-359`, `RS-GR-360`, `RS-GR-361`, and `RS-GR-362` warn that a world can look more successor-safe because it changed verifier-policy snapshots, accepted roots / identities, claim-check strictness, or deterministic appraisal semantics rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a retained proof packet as a complete historical verdict when the archive did not also retain the rulebook that turned that packet into "pass", "warn", or "reject".

### Recommended next move

1. Keep one evidence-retained-but-policy-implicit baseline beside any versioned-policy provenance lane.
2. Publish the exact retained verifier profile — trust roots, identities, claim checks, thresholds, and disposition rules — before calling a world successor-safe.
3. When possible, replay both the historical policy snapshot and the current policy so future stricter or looser verifier settings are visible instead of silently rewriting history.

### 2026-03-22 research tranche - status semantics and supersession history

Added the following source-backed materials:
- `RS-GR-363` (RFC 5280 makes CRLs time-stamped revoked-certificate lists, ties acceptance to a suitably recent CRL under local policy, and limits revocation visibility to issuance cadence),
- `RS-GR-364` (RFC 6960 distinguishes `good`, `revoked`, and `unknown` status, includes revocation time / reason, and bounds response validity with `thisUpdate` / `nextUpdate`),
- `RS-GR-365` (Bitstring Status List v1.0 makes revocation and suspension distinct status purposes and allows message-bearing status semantics with `statusReference`),
- `RS-GR-366` (the current SCITT architecture allows subject-correlated statements to indicate end of life, redirection to a newer version, or other lifecycle changes),
- `RS-GR-367` (Sigstore's security model avoids traditional revocation for Fulcio certificates by using short-lived certificates plus log timestamps), and
- `RS-GR-368` (Sigstore's threat model distinguishes issuer-side account revocation from Sigstore's own guarantees and notes compromise-time-aware revocation of trust material).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/status_semantics_supersession_history_and_negative_evidence_are_world_contracts_not_just_successful_verification.md`
- Added one compact local receipt:
  - `artifacts/process/status_semantics_and_supersession_history_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to retain portable evidence and the verifier rulebook used to interpret it.
These sources add one more missing status-transition layer beneath them.

- `RS-GR-363`, `RS-GR-364`, `RS-GR-365`, `RS-GR-366`, `RS-GR-367`, and `RS-GR-368` warn that a world can look more successor-safe because it changed revocation / suspension semantics, status freshness, unknown-handling, supersession routing, or compromise-time interpretation rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a historically successful verification event as the whole successor contract when the archive does not also preserve how later status changes could invalidate, suspend, supersede, or narrowly grandfather that success.

### Recommended next move

1. Keep one proof-rich-but-status-implicit baseline beside any lane with explicit revocation / suspension / supersession history.
2. Publish the exact status vocabulary, status-source freshness rule, and unknown-handling before calling a world successor-safe.
3. When possible, preserve both historical validity-at-signing and current acceptability-now so future inheritors can see whether a later status change rewrote trust, narrowed it to a pre-compromise interval, or simply redirected to a newer object.

### 2026-03-22 research tranche - subject binding and resolver independence

Added the following source-backed materials:
- `RS-GR-369` (RFC 6920 standardizes `ni` names that identify digital objects by hash and separate naming from later dereferencing),
- `RS-GR-370` (the current in-toto statement requires immutable subject digests and matches subjects purely by digest even when human-facing names are present),
- `RS-GR-371` (Docker's current guidance says digests are immutable while tags can be reused or changed, and that one tag can resolve to a manifest list plus platform-specific digests),
- `RS-GR-372` (the OCI distribution spec defines digests as unique identifiers, tags as human-readable pointers, and referrers as digest-keyed subject relationships),
- `RS-GR-373` (SWHIDs are stable identifiers rather than URLs, embed intrinsic object identifiers, and separate context qualifiers from the core identifier), and
- `RS-GR-374` (cosign signatures protect object digests and uses separate signed annotations when a specific tag-to-digest mapping matters).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/subject_binding_mutable_aliases_and_resolver_independence_are_world_contracts_not_just_signed_names.md`
- Added one compact local receipt:
  - `artifacts/process/subject_binding_and_resolver_independence_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to retain proof packets, rulebooks, and status history.
These sources add one more missing subject-identity layer beneath them.

- `RS-GR-369`, `RS-GR-370`, `RS-GR-371`, `RS-GR-372`, `RS-GR-373`, and `RS-GR-374` warn that a world can look more successor-safe because it changed immutable subject identifiers, alias mutability, digest pinning, referrer correlation, or resolver independence rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a signed name, tag, URL, or repository path as the stable thing that was proven when the durable contract actually depends on which immutable subject identifier those mutable handles pointed to at the time.

### Recommended next move

1. Keep one signed-name / mutable-alias baseline beside any digest- or intrinsic-ID-centered provenance lane.
2. Publish the exact core subject identifier, variant-resolution rule, and alias-to-subject binding before calling a world successor-safe.
3. When possible, archive signed alias history or resolver-independent subject IDs so future inheritors can reconstruct what a receipt or supersession event was actually about after names move.



### 2026-03-22 research tranche - canonicalization boundaries and representation drift

Added the following source-backed materials:
- `RS-GR-375` (RFC 8785 says JSON signatures need invariant data and defines canonical JSON using I-JSON constraints plus deterministic property sorting),
- `RS-GR-376` (RFC 8949 says deterministic CBOR is protocol-specific, requires preferred shortest encodings, forbids indefinite-length items, and sorts map keys deterministically),
- `RS-GR-377` (the DSSE protocol signs the exact serialized body plus payload type, avoids canonicalization, and requires applications to consume the same verified bytes),
- `RS-GR-378` (RDF Canonicalization defines a stable canonical serialization for RDF datasets and stable blank-node identifiers across different graph serializations),
- `RS-GR-379` (VC Data Integrity says canonicalization choice depends on whether plain JSON or JSON-LD semantics are being secured and warns that proof security depends on canonicalization correctness), and
- `RS-GR-380` (the current Python packaging attestation spec treats a JSON in-toto statement as an opaque binary blob on the wire and signs it with DSSE to avoid canonicalization).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/canonicalization_boundaries_representation_drift_and_transform_semantics_are_world_contracts_not_just_signed_bytes.md`
- Added compact local artifacts:
  - `artifacts/process/canonicalization_boundary_and_representation_drift_receipt_20260322.json`
  - `artifacts/process/canonicalization_boundary_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to retain proofs, rulebooks, status history, subject identity, and resolver-independent correlation.
These sources add one more missing representation layer beneath them.

- `RS-GR-375`, `RS-GR-376`, `RS-GR-377`, `RS-GR-378`, `RS-GR-379`, and `RS-GR-380` warn that a world can look more successor-safe because it changed canonicalization profile, payload-type binding, exact-byte versus semantic-signing boundary, or transform-validity semantics rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a verification success over one representation as if it automatically covered every semantically similar rewrite, reserialization, or format projection when the actual contract may protect only exact bytes or only one declared canonicalization layer.

### Recommended next move

1. Keep one raw-bytes / no-transform baseline beside any lane that claims canonical or semantic portability.
2. Publish the exact protected representation layer, payload type, and transform-validity table before calling a world successor-safe.
3. When possible, archive one tiny local demo showing which transformations preserve hashes / signatures and which create a new subject or receipt boundary.

### 2026-03-22 research tranche - semantic survival and schema pinning

Added the following source-backed materials:
- `RS-GR-381` (RFC 6838 defines media types as registered format identifiers for use across protocols),
- `RS-GR-382` (JSON Schema Core says a dialect is a set of vocabularies and semantics and that `$schema` declares which dialect is in force),
- `RS-GR-383` (JSON-LD 1.1 says `@context` defines term understanding, `@version` can block older processors from producing different output, and remote contexts may be followed automatically),
- `RS-GR-384` (the current in-toto statement layer says the Statement identifies predicate types and requires `predicateType`),
- `RS-GR-385` (the current SCITT architecture says statements should be tagged with a relevant media type to help interpretation), and
- `RS-GR-386` (SPDX 3.0.1 says `specVersion` is the reference needed to parse and interpret an element across future changes).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/semantic_survival_schema_pinning_and_vocabulary_continuity_are_world_contracts_not_just_verified_bytes.md`
- Added one compact local receipt:
  - `artifacts/process/semantic_survival_and_schema_pinning_receipt_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to retain bytes, subject identity, status history, and the exact protected representation layer.
These sources add one more missing interpretation layer beneath them.

- `RS-GR-381`, `RS-GR-382`, `RS-GR-383`, `RS-GR-384`, `RS-GR-385`, and `RS-GR-386` warn that a world can look more successor-safe because it changed media-type tagging, predicate/schema identity, context pinning, schema dialect, or vocabulary continuity rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a byte-perfect, signature-valid statement as self-explanatory when the archive does not also preserve the rulebook that says what the statement's fields, predicate, and vocabulary meant.

### Recommended next move

1. Keep one bytes-verifiable-but-semantic-live-lookup baseline beside any lane that claims long-horizon meaning portability.
2. Publish the exact interpretation bundle — media type, statement / predicate type, schema dialect, specVersion, context, profile, and unknown-term policy — before calling a world successor-safe.
3. When possible, preserve enough local interpretation material to replay meaning fully offline and surface any version mismatch or unknown extension as an explicit divergence rather than a silent success.

### 2026-03-22 research tranche - authority scope and designated speaker rules

Added the following source-backed materials:
- `RS-GR-387` (RFC 5280 says basic constraints, extended key usage, and name constraints separate identity from certification power, permitted purpose, and namespace scope),
- `RS-GR-388` (the current TUF specification says delegated roles are trusted by specific keys and thresholds, are limited to declared target paths, and may terminate further trust search),
- `RS-GR-389` (the current in-toto specification says layouts indicate which keys are authorized for each step and clients verify that each step was performed by the authorized functionary),
- `RS-GR-390` (the current SCITT architecture says registration policies and trust anchors must be transparent and enough information must survive to replay the registration checks in force at registration time),
- `RS-GR-391` (the current SPIFFE trust-domain specification says a trust domain is an identity namespace backed by an issuing authority and validators must choose the bundle for that trust domain),
- `RS-GR-392` (the current SPIRE documentation says workload registration maps identities to selectors and parent-SPIFFE relationships that must match before an identity is issued), and
- `RS-GR-393` (RFC 7519 says the `aud` claim identifies intended recipients and non-matching principals must reject the token).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/authority_scope_namespace_custody_and_designated_speaker_rules_are_world_contracts_not_just_verified_issuers.md`
- Added compact local artifacts:
  - `artifacts/process/authority_scope_and_designated_speaker_receipt_20260322.json`
  - `artifacts/process/authority_scope_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve subject identity, protected representation, meaning bundles, policy snapshots, and status history.
These sources add one more missing admissibility layer above them.

- `RS-GR-387`, `RS-GR-388`, `RS-GR-389`, `RS-GR-390`, `RS-GR-391`, `RS-GR-392`, and `RS-GR-393` warn that a world can look more successor-safe because it changed who had standing to speak for a namespace, step, workload, or relying-party audience rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating a recognized signer, valid receipt, and stable subject identifier as sufficient when the archive does not also preserve the delegation chain, trust-domain custody, registration entry, or audience rule that made that signer's statement admissible.

### Recommended next move

1. Keep one same-subject / same-signature baseline beside any lane that changes designated-speaker policy, role delegation, or namespace custody.
2. Publish the standing snapshot — issuer identity, delegated role or registration entry, namespace / path scope, purpose / step / predicate scope, and any audience restrictions — before calling a world successor-safe.
3. When possible, preserve one tiny local replay artifact showing that the same cryptographically valid statement can pass or fail solely because authority scope changed.



### 2026-03-22 research tranche - quorum semantics and signer independence

Added the following source-backed materials:
- `RS-GR-394` (NIST SP 800-57 Part 2 says distribution plans may require key components with dual control and split knowledge),
- `RS-GR-395` (the current TUF specification says roles use thresholds of signatures and the root threshold should make compromise of all offline keys extremely unlikely),
- `RS-GR-396` (the current in-toto specification says a step threshold is intended for higher-trust steps where multiple functionaries perform the operation and report the same results),
- `RS-GR-397` (current Sigsum documentation shows trust policy can require a declared witness quorum before a log is trusted),
- `RS-GR-398` (the current SCITT architecture says the same statement may be registered in multiple transparency services to produce multiple independent receipts and relying parties choose which services they trust), and
- `RS-GR-399` (the current TUF specification says the signatures list should contain only one signature per keyid so one key is not counted multiple times toward a threshold).
- Added one compact inheritor-facing topic note:
  - `docs/LIBRARY/topics/quorum_semantics_signer_independence_and_concurrence_profiles_are_world_contracts_not_just_threshold_counts.md`
- Added compact local artifacts:
  - `artifacts/process/quorum_semantics_and_signer_independence_receipt_20260322.json`
  - `artifacts/process/quorum_semantics_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_SOURCES.md`
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `CHANGELOG.md`
  - `docs/AGENT_LOG.md`

### New research / inheritor insight

The archive already knew to preserve who may speak for a subject.
These sources add one more missing collective-assurance layer above that.

- `RS-GR-394`, `RS-GR-395`, `RS-GR-396`, `RS-GR-397`, `RS-GR-398`, and `RS-GR-399` warn that a world can look more successor-safe because it changed quorum rules, distinctness classes, or separation-of-duty assumptions rather than because present actors became more future-regarding.

So the next implementor should avoid one more easy mistake:

1. treating any satisfied threshold as enough when the archive does not also preserve what counted as distinct and whether those counted approvals actually came from independent compromise domains.

### Recommended next move

1. Keep one same-statement / same-threshold-count baseline beside any lane that changes distinctness class, witness quorum, or multi-service concurrence semantics.
2. Publish the concurrence profile — threshold or quorum, unit of distinctness, separation-of-duty assumptions, and fail-open versus fail-closed behavior — before calling a world successor-safe.
3. When possible, preserve one tiny local replay artifact showing that the same numeric threshold can imply very different assurance once independence classes are made explicit.


## Additional compact pass: conflict resolution and precedence profiles

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/conflict_resolution_precedence_and_disagreement_profiles_are_world_contracts_not_just_quorum_counts.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-400` through `RS-GR-406` (TUF termination / ordering, precedence bug evidence, in-toto agreement semantics, SCITT issuer-conflict curation, and Sigstore policy-composition semantics).
- Added compact local artifacts:
  - `artifacts/process/conflict_resolution_and_precedence_receipt_20260322.json`
  - `artifacts/process/conflict_resolution_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve who may speak and how many independent speakers must concur.
This pass sharpens the next layer below that: **what happens when valid-looking support conflicts, overlaps, or partially matches**.

- `RS-GR-400`, `RS-GR-401`, and `RS-GR-402` warn that delegated-authority order and terminating precedence can decide which otherwise-valid trust statement is allowed to count.
- `RS-GR-403` warns that some threshold systems require agreement on the same underlying facts, not just enough signatures.
- `RS-GR-404`, `RS-GR-405`, and `RS-GR-406` warn that multi-issuer and multi-policy worlds can differ sharply depending on issuer-inclusion filters, `AND`/`OR` composition, and no-match fallback behavior.

So the next implementor should avoid two more easy mistakes:

1. treating all valid support as additive once designated speakers and thresholds have been published;
2. treating conflict resolution as harmless control-plane plumbing instead of as part of the institution.

### Recommended next move

1. Whenever multiple authorities, statements, or policies can overlap, publish the precedence order and whether any role is terminating or veto-capable.
2. Keep `AND`/`OR`/threshold / no-match behavior explicit in benchmark cards rather than burying it in verifier code.
3. Add one same-facts-disagreement lane where signatures remain valid but the reported materials / products or predicates diverge.
4. Add one same-evidence comparison where only precedence or conflict-resolution profile changes before generalizing any authenticity or successor-safety gain.


## Additional compact pass: decision traces and replay diagnostics

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/decision_traces_replay_diagnostics_and_explanation_receipts_are_world_contracts_not_just_final_verdicts.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-407` through `RS-GR-413` (RATS appraisal-result framing, XACML obligations / combining, OPA explanation / decision-log / provenance surfaces, and Cedar / Verified Permissions determining-policy diagnostics).
- Added compact local artifacts:
  - `artifacts/process/decision_traces_and_replay_diagnostics_receipt_20260322.json`
  - `artifacts/process/decision_trace_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve who may speak, how many independent speakers must concur, and how conflicts are resolved.
This pass adds the next missing layer below that: **why this exact verdict happened in practice**.

- `RS-GR-407` and `RS-GR-408` warn that attestation / authorization results are outputs of appraisal machinery and may also carry obligations or advice, so a bare final verdict can discard part of the decision contract.
- `RS-GR-409`, `RS-GR-410`, and `RS-GR-411` warn that practical verifiers can preserve explanation traces, decision correlation ids, bundle metadata, and build provenance, so a replayable decision receipt is smaller and more realistic than re-saving every raw execution environment.
- `RS-GR-412` and `RS-GR-413` warn that the same top-line `Deny` can arise from forbid-overrides-permit, default deny with no matches, or skip-on-error, and those routes lead to different remediation and trust conclusions.

So the next implementor should avoid two more easy mistakes:

1. treating a preserved policy snapshot as enough even when no one retained which rules actually determined the verdict;
2. treating final pass / fail results as stable when verifier build, bundle revision, fallback path, or skipped-error branches are missing.

### Recommended next move

1. Keep one final-verdict-only baseline beside any lane that adds determining-policy diagnostics or replay traces.
2. Preserve one compact explanation receipt for each material benchmark decision: request / decision id, determining policies, fallback path, errors, and verifier / bundle provenance.
3. When full traces are too large, retain at least determining policies, default / fallback route, and any obligations / advice so future sessions can distinguish “deny because forbid fired” from “deny because nothing matched” or “deny after error skip.”

## Additional compact pass: reference baselines and appraisal-input continuity

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/reference_baselines_endorsement_sets_and_appraisal_input_continuity_are_world_contracts_not_just_decision_traces.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-414` (RFC 9334 reference values / endorsements / attestation result roles),
  - `RS-GR-415` (CoRIM reconciliation needs reference values and endorsements),
  - `RS-GR-416` (endorsements / reference-state layering and timeliness),
  - `RS-GR-417` (verifier inputs and claim-selection scope),
  - `RS-GR-418` (Sigstore trust-root corpus),
  - `RS-GR-419` (remote-vs-air-gap trust-root refresh semantics), and
  - `RS-GR-420` (OPA bundles load policy and related data as live appraisal input).
- Added compact local artifacts:
  - `artifacts/process/reference_baselines_and_appraisal_inputs_receipt_20260322.json`
  - `artifacts/process/reference_baseline_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve proofs, rulebooks, and decision traces.
This pass sharpens the next hidden dependency below those layers.

- `RS-GR-414` through `RS-GR-417` warn that appraisal depends on **reference values, endorsements, and evidence-selection scope**, not only on the final decision procedure.
- `RS-GR-418` and `RS-GR-419` warn that **trust-root source and refresh path** can change outcomes even under the same nominal policy.
- `RS-GR-420` warns that **policy-related data bundles** can silently change verdicts even when policy language is unchanged.

So the next implementor should avoid two more easy mistakes:

1. treating a saved verdict plus trace as replay-complete when the known-good / endorsed baseline corpus was not also pinned;
2. attributing gains from better trust-root refresh or cleaner baseline curation to underlying Golden-Rule progress.

### Recommended next move

1. When a provenance lane emits a material verdict, pin one compact digest set for the exact reference-value, endorsement, trust-root, and policy-data inputs consulted.
2. Keep a same-evidence comparison where only the baseline corpus changes, so baseline drift does not masquerade as moral or institutional improvement.
3. Publish explicit missing / stale / unreachable-baseline fallback behavior.

## Additional compact pass: evidence acquisition topology, challenge binding, and observation scope

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/evidence_acquisition_topology_challenge_binding_and_observation_scope_are_world_contracts_not_just_retained_evidence.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-421` (RATS architecture and passport / background-check topology),
  - `RS-GR-422` (challenge / uni-directional / streaming acquisition plus claim-selection and broker semantics),
  - `RS-GR-423` (EAT freshness and nonce requirements),
  - `RS-GR-424` (nonce-quality requirements when attestation is embedded in CSRs),
  - `RS-GR-425` (`in-toto-run` observation-field capture),
  - `RS-GR-426` (`in-toto-verify` admissible evidence-form checks), and
  - `RS-GR-427` (`in_toto_record_start` / `in_toto_record_stop` staged-capture semantics).
- Added compact local artifacts:
  - `artifacts/process/evidence_acquisition_and_observation_scope_receipt_20260322.json`
  - `artifacts/process/evidence_acquisition_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve verdicts, rulebooks, baseline corpora, and portable proof packets.
This pass sharpens the next hidden dependency below those layers.

- `RS-GR-421` and `RS-GR-422` warn that **how Evidence reaches the verifier** — direct challenge/response, cached passport-style results, background-check relay, unsolicited push, or brokered stream — changes the trust contract even before appraisal begins.
- `RS-GR-423` and `RS-GR-424` warn that **freshness binding quality** is itself a replay-critical record: who generated the nonce or handle, how much entropy it had, and how it was bound to the subject and verifier.
- `RS-GR-425`, `RS-GR-426`, and `RS-GR-427` warn that **observation-field scope and capture staging** determine what future inheritors can actually inspect, because recorded materials / products / commands / byproducts / environment are design choices, not inevitable facts.

So the next implementor should avoid two more easy mistakes:

1. treating retained evidence bytes as replay-complete when acquisition topology, freshness binding, and claim-selection scope are missing;
2. attributing gains from better broker design, richer capture fields, or stricter freshness handling to underlying Golden-Rule progress.

### Recommended next move

1. Preserve one compact acquisition receipt beside each material verdict: collection topology, freshness handle origin, requested claim scope, intermediaries, and missing / stale / partial-evidence behavior.
2. Keep one same-subject comparison where only acquisition contract changes, so observation drift does not masquerade as moral or institutional improvement.
3. Treat captured fields (materials, products, command, environment, event logs, etc.) as a first-class benchmark surface rather than as invisible tooling detail.

## Additional compact pass: verifier targeting, session binding, and replay scope

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/verifier_targeting_session_binding_and_replay_scope_are_world_contracts_not_just_valid_presentations.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-441` (OpenID4VP `client_id` / `nonce` verifier-target and transaction binding),
  - `RS-GR-442` (OpenID4VP `wallet_nonce` and exact Request-Object retrieval binding),
  - `RS-GR-443` (OpenID4VP `expected_origins` for DC API replay detection),
  - `RS-GR-444` (OpenID4VP ISO mdoc `SessionTranscript` / handover binding),
  - `RS-GR-445` (RFC 9901 Key Binding JWT target / freshness / package binding),
  - `RS-GR-446` (VC Data Integrity `domain` / `challenge` replay semantics), and
  - `RS-GR-447` (RFC 9449 request-method / endpoint / nonce replay scope).
- Added compact local artifacts:
  - `artifacts/process/verifier_targeting_and_replay_scope_receipt_20260322.json`
  - `artifacts/process/verifier_targeting_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve what exact request was made and how a returned presentation satisfied it.
This pass sharpens the next hidden dependency below those layers.

- `RS-GR-441` through `RS-GR-444` warn that **who a proof was for and which session / origin / response channel it belonged to** can be an authenticated part of the contract, not just surrounding protocol trivia.
- `RS-GR-445` and `RS-GR-446` warn that **holder proofs and proof options can be bound to verifier audience, nonce, domain, and selected disclosures**, so “valid proof” is weaker than “valid proof for this verifier in this session”.
- `RS-GR-447` warns that **route-level replay scope** can depend on endpoint, method, time window, and nonce handling, not merely on whether a signature verifies.

So the next implementor should avoid two more easy mistakes:

1. treating a cryptographically valid presentation as replay-complete when verifier target, origin, route, or session transcript were not preserved;
2. attributing gains from tighter anti-replay or anti-misbinding architecture to underlying Golden-Rule progress.

### Recommended next move

1. Preserve one compact targeting receipt beside each material verdict: intended verifier / audience / origin, nonce family, route or response binding, transcript fields, and stale-or-mismatch fallback.
2. Keep one same-payload comparison where only target / session-binding architecture changes, so replay hardening does not masquerade as moral or institutional improvement.
3. Treat verifier-targeting and replay-scope drift as a first-class benchmark surface rather than as hidden protocol plumbing.

## Additional compact pass: metadata resolution, federation chains, and capability continuity

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/metadata_resolution_federation_chains_and_capability_continuity_are_world_contracts_not_just_known_participants.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-448` (OpenID Federation resolved metadata after Trust Chain policy application),
  - `RS-GR-449` (OpenID Federation evaluation-time Trust Chain and `jwks` linkage),
  - `RS-GR-450` (OpenID4VP `openid_federation` trust-chain-derived verifier metadata),
  - `RS-GR-451` (OpenID4VP DID / verifier-attestation / X.509 / redirect-uri resolution modes),
  - `RS-GR-452` (DID Resolution outputs and historical-state auditability),
  - `RS-GR-453` (OpenID Connect Discovery fail-closed validation),
  - `RS-GR-454` (RFC 8414 endpoint / capability metadata and `signed_metadata`), and
  - `RS-GR-455` (RFC 9700 metadata for misconfiguration reduction and crypto agility).
- Added compact local artifacts:
  - `artifacts/process/metadata_resolution_and_capability_continuity_receipt_20260322.json`
  - `artifacts/process/metadata_resolution_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve what request was made, who it targeted, and which session it belonged to.
This pass sharpens the next hidden dependency below those layers.

- `RS-GR-448` through `RS-GR-451` warn that **participant metadata can be resolved through materially different trust paths** — local request parameters, federation trust chains, DID resolution, verifier attestations, X.509 paths, or unsigned redirect-uri flows.
- `RS-GR-452` and `RS-GR-453` warn that **resolution outputs and validation outcomes are part of replayability**, not just optional fetch-time details.
- `RS-GR-454` and `RS-GR-455` warn that **capability surfaces, endpoint choices, and key material can drift with metadata snapshots**, and that metadata continuity itself is a security control.

So the next implementor should avoid two more easy mistakes:

1. treating a participant identifier as replay-complete when the resolved metadata snapshot, trust chain, or discovery-validation result was not preserved;
2. attributing gains from metadata-policy hardening, resolver changes, or better endpoint/key discovery to underlying Golden-Rule progress.

### Recommended next move

1. Preserve one compact metadata-resolution receipt beside each material verdict: resolution mode, sources fetched, trust-chain / signed-metadata inputs, policy application result, final capability surface, and validation outcome.
2. Keep one same-request comparison where only the metadata-resolution path changes, so federation or resolver hardening does not masquerade as moral or institutional improvement.
3. Treat metadata-resolution drift as a first-class benchmark surface rather than as invisible discovery plumbing.



## Additional compact pass: capability negotiation, downgrade resistance, and chosen-profile continuity

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/capability_negotiation_downgrade_resistance_and_chosen_profile_continuity_are_world_contracts_not_just_supported_features.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-456` (OpenID4VP `vp_formats_supported` and Client Identifier Prefix negotiation surface),
  - `RS-GR-457` (OpenID4VP request-object signing / encryption support and `wallet_nonce` continuity),
  - `RS-GR-458` (OpenID4VP fail-closed handling for unsupported origins / transaction-data types),
  - `RS-GR-459` (RFC 8414 response-type / response-mode / grant capability metadata),
  - `RS-GR-460` (RFC 8725 algorithm allowlists and explicit typing),
  - `RS-GR-461` (RFC 9101 explicitly typed request objects and distinct key-regime guidance),
  - `RS-GR-462` (OpenID4VCI credential configurations, proof types, and encryption requirements), and
  - `RS-GR-463` (OpenID4VCI fail-closed mismatch errors and substitution-resistant encryption requirements).
- Added compact local artifacts:
  - `artifacts/process/capability_negotiation_and_downgrade_receipt_20260322.json`
  - `artifacts/process/capability_negotiation_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve who the participants were and how their metadata became trusted.
This pass sharpens the next hidden dependency below those layers.

- `RS-GR-456` through `RS-GR-459` warn that **participants can advertise a whole lattice of supported formats, proof types, response modes, and grant paths**, so one observed message is only one selected point inside a wider capability surface.
- `RS-GR-460` and `RS-GR-461` warn that **algorithm choice, token typing, and protected-request profile are application-level admissibility decisions**, not attacker-controlled header suggestions.
- `RS-GR-462` and `RS-GR-463` warn that **issuance and presentation can differ because stronger encryption / proof / binding profiles were required, preferred, downgraded, or hard-failed**, not because the underlying institution changed.

So the next implementor should avoid two more easy mistakes:

1. treating an observed format or transport path as replay-complete when the advertised capability set, chosen profile, and downgrade posture were not preserved;
2. attributing gains from stricter negotiation defaults or fail-closed mismatch handling to underlying Golden-Rule progress.

### Recommended next move

1. Preserve one compact negotiation receipt beside each material verdict: advertised capabilities, exact chosen format / proof / algorithm / response-mode / encryption profile, and downgrade / unsupported-capability behavior.
2. Keep one same-request comparison where only capability-negotiation or downgrade posture changes, so safer defaults or stricter rejections do not masquerade as moral or institutional improvement.
3. Treat chosen-profile continuity as a first-class benchmark surface rather than as invisible interoperability plumbing.

## Additional compact pass: authenticator assurance and device-binding semantics

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/authenticator_assurance_user_presence_and_device_binding_are_world_contracts_not_just_valid_keys.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-464` through `RS-GR-470` (WebAuthn UP / UV / backup bits, AAGUID versus attestation, NIST authenticator-assurance guidance, OpenID4VCI key attestation, HAIP high-assurance key-attestation interoperability, and OpenID4VP holder-binding waiver semantics).
- Added compact local artifacts:
  - `artifacts/process/authenticator_assurance_and_device_binding_receipt_20260322.json`
  - `artifacts/process/authenticator_assurance_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve request contracts, verifier targeting, metadata resolution, and chosen capability profiles.
The next missing layer is that a future inheritor can still keep all of that and yet not know what kind of authenticator actually stood behind the proof.

- `RS-GR-464` and `RS-GR-466` warn that user presence, user verification, and syncability are not cosmetic bits; they change the assurance story of the same proof format.
- `RS-GR-465`, `RS-GR-468`, and `RS-GR-469` warn that authenticator-class inference is not the same as attested authenticator or key-container proof.
- `RS-GR-467` and `RS-GR-470` warn that high-assurance non-exportable / holder-bound paths and lower-assurance waived-holder-binding paths can both look “cryptographically valid” if the archive keeps only the final proof.

So the next implementor should avoid two more easy mistakes:

1. treating key possession as replay-complete without preserving user-control, exportability, and attestation posture;
2. attributing gains from device-bound or strongly attested authenticators to generic Golden-Rule progress.

### Recommended next move

1. Publish one compact authenticator-assurance receipt beside each material issuance or presentation verdict.
2. Keep at least one same-behavior companion lane where only UV / holder-binding / syncability / attestation posture changes.
3. Reject archive summaries that say only “the right key signed” when the underlying authenticator class is materially policy-relevant.

## Additional compact pass: transaction-intent binding and approval continuity

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/transaction_intent_binding_approval_surfaces_and_consent_continuity_are_world_contracts_not_just_authenticated_sessions.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-471` through `RS-GR-477` (OpenID4VP transaction data and transaction-data hashes, OAuth rich authorization details and subset semantics, JAR request-object protection, PAR request tamper resistance, and NIST authentication-intent guidance).
- Added compact local artifacts:
  - `artifacts/process/transaction_intent_binding_and_approval_continuity_receipt_20260322.json`
  - `artifacts/process/transaction_intent_binding_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve request contracts, verifier targeting, capability choices, and authenticator assurance.
The next missing layer is that a future inheritor can still keep all of that and yet not know what exact transaction, document set, or authorization outcome the user actually approved.

- `RS-GR-471` and `RS-GR-472` warn that the same presentation proof can either be generic identification or a transaction-specific authorization, depending on whether transaction data and its proof linkage were preserved.
- `RS-GR-473` and `RS-GR-474` warn that the granted subset and same-versus-different approval semantics are type-specific and cannot be reconstructed safely from naive object comparison alone.
- `RS-GR-475` and `RS-GR-476` warn that an approval object can be integrity-protected end to end or remain vulnerable to front-channel tampering, including payment-context swaps.
- `RS-GR-477` warns that even a real user gesture is weaker than a preserved proof of what that user gesture authorized.

So the next implementor should avoid two more easy mistakes:

1. treating authenticated presence plus a valid proof as replay-complete when the exact approved object was not preserved;
2. attributing gains from stronger transaction binding or request tamper resistance to generic Golden-Rule progress.

### Recommended next move

1. Preserve one compact approval-intent receipt beside each material authorization or presentation verdict.
2. Keep at least one same-behavior companion lane where only transaction binding, granted-subset semantics, or approval-object integrity changes.
3. Reject archive summaries that say only “the user approved the request” when the archive no longer preserves what exact request or subset was approved.


## Additional compact pass: correlation scope, pairwise pseudonyms, and linkability boundaries

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/correlation_scope_pairwise_pseudonyms_and_linkability_boundaries_are_world_contracts_not_just_selective_disclosure.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-478` through `RS-GR-485` (OpenID Connect pairwise subject identifiers and sector identifiers, BBS unlinkable derived proofs, ECDSA non-unlinkable disclosure, SD-JWT decoy / issuer-type privacy tradeoffs, Bitstring Status List privacy-preserving status publication, and the W3C decentralized-credentials threat model's unlinkability framing).
- Added compact local artifacts:
  - `artifacts/process/correlation_scope_and_linkability_receipt_20260322.json`
  - `artifacts/process/correlation_scope_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve disclosure profiles, request contracts, verifier targeting, authenticator assurance, and transaction intent.
The next missing layer is that a future inheritor can still keep all of that and yet not know whether repeated presentations were intentionally linkable.

- `RS-GR-478` and `RS-GR-479` warn that “pairwise” identifiers still have a scope and can intentionally remain stable across a verifier cluster or sector.
- `RS-GR-480` and `RS-GR-481` warn that proof-family choice changes whether repeated presentations are unlinkable or naturally correlatable even when revealed facts look the same.
- `RS-GR-482` and `RS-GR-483` warn that hidden-structure padding and issuer / type specialization can leak correlation or category information even under selective disclosure.
- `RS-GR-484` warns that status publication itself can widen or narrow the observer surface.
- `RS-GR-485` warns that valid and minimal are not the same privacy property as unlinkable.

So the next implementor should avoid two more easy mistakes:

1. treating selective disclosure as replay-complete when identifier scope, proof-family linkability, and status-check privacy were not preserved;
2. attributing gains from narrower correlation boundaries or stronger unlinkability to generic Golden-Rule progress.

### Recommended next move

1. Preserve one compact correlation-scope receipt beside each material presentation or authorization verdict.
2. Keep at least one same-behavior companion lane where only identifier stability, proof-family unlinkability, or status-check observer surface changes.
3. Reject archive summaries that say only “the presentation was privacy-preserving” when the archive no longer preserves who could still correlate it.


## Additional compact pass: delivery paths, transport confidentiality, and intermediary visibility

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/delivery_paths_transport_confidentiality_and_intermediary_visibility_are_world_contracts_not_just_valid_presentations.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-486` through `RS-GR-492` (OpenID4VP `direct_post` / `direct_post.jwt` delivery-path and leakage constraints, HAIP's JAR-plus-encrypted-response requirement, JAR request confidentiality, PAR backchannel request transport, and OAuth BCP browser-history / query exposure warnings).
- Added compact local artifacts:
  - `artifacts/process/delivery_path_and_intermediary_visibility_receipt_20260322.json`
  - `artifacts/process/delivery_path_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve disclosure profiles, request contracts, verifier targeting, authenticator assurance, transaction intent, and correlation scope.
The next missing layer is that a future inheritor can still keep all of that and yet not know **which transport path actually exposed the ask or the answer to browsers, relays, logs, or backends in plaintext**.

- `RS-GR-486` shows that OpenID4VP deliberately separates redirect-only flows from `direct_post` / `direct_post.jwt`, which means the response path itself is a protocol choice with different observer surfaces.
- `RS-GR-487` shows that plain `direct_post` introduces an out-of-band session-fixation risk and that Wallets must prevent leakage through Response URIs, which means not every valid cross-device delivery path has the same replay or observer properties.
- `RS-GR-488` shows that HAIP treats signed requests and encrypted responses as mandatory high-assurance transport choices, which means delivery-path confidentiality is part of the assurance contract, not just an implementation detail.
- `RS-GR-489` and `RS-GR-490` show that JAR and PAR exist specifically to move the authoritative request off of tamperable or overexposed front-channel URLs and into protected channels or references.
- `RS-GR-491` and `RS-GR-492` show that redirect URLs and query parameters can leak codes or tokens into browser history, and that the modern OAuth security baseline treats some old URL-carried modes as less secure or insecure.

So the next implementor should avoid two more easy mistakes:

1. treating “the presentation was valid for this verifier” as replay-complete when the archive no longer preserves which surfaces saw the request or response in plaintext;
2. attributing gains from encrypted responses, request-by-reference, or backchannel transport to generic Golden-Rule progress instead of narrower observer exposure.

### Recommended next move

1. Preserve one compact delivery-path receipt beside each material presentation or authorization verdict.
2. Keep at least one same-behavior companion lane where only request transport, response mode, response encryption, or intermediary plaintext visibility changes.
3. Reject archive summaries that say only “the verifier received a valid presentation” when the archive no longer preserves how the verifier received it.


## Additional compact pass: approval rendering, locale, and trusted display

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/approval_rendering_locale_and_trusted_display_are_world_contracts_not_just_bound_transaction_data.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-493` through `RS-GR-500` (OpenID4VP consent-before-error semantics, OpenID4VCI display-label / locale / order semantics, Secure Payment Confirmation transaction-confirmation and spoofing constraints, NIST authentication-intent requirements, and OAuth UI-redressing defenses).
- Added compact local artifacts:
  - `artifacts/process/approval_rendering_and_trusted_display_receipt_20260322.json`
  - `artifacts/process/approval_rendering_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`

### New research / inheritor insight

The archive already knew to preserve delivery paths, request contracts, verifier targeting, authenticator assurance, and transaction-intent bindings.
The next missing layer is that a future inheritor can still keep all of that and yet not know **what the human actually saw, in what order and locale, and under which trusted UI surface when approval happened**.

- `RS-GR-493` shows that OpenID4VP treats consent timing itself as a privacy and replay concern, which means the archive should preserve what the wallet was allowed to reveal before consent.
- `RS-GR-494` and `RS-GR-495` show that OpenID4VCI already models localized claim labels and display order for end-user rendering, which means approval meaning depends on more than raw claim paths.
- `RS-GR-496` and `RS-GR-497` show that SPC is built around the user confirming transaction details, but also warns that merchant-supplied details shown to the user can diverge from backend truth unless the relying party checks alignment.
- `RS-GR-498` shows that explicit user action is a separate part of assurance from merely having a valid authenticator result.
- `RS-GR-499` shows that approval UIs can be redressed or clickjacked, so preserving only the approved machine object without the trust posture of the rendering surface is incomplete.
- `RS-GR-500` shows that locale and formatting choices are explicit protocol inputs and that user agents retain rendering control for some visual elements, which means one machine ask does not guarantee one human-visible ceremony.

So the next implementor should avoid two more easy mistakes:

1. treating “the user approved the bound transaction” as replay-complete when the archive no longer preserves what the human-facing renderer actually showed;
2. attributing gains from trusted browser or wallet chrome, better labels, or anti-clickjacking posture to generic Golden-Rule progress instead of narrower approval-surface integrity.

### Recommended next move

1. Preserve one compact approval-rendering receipt beside each material authorization or presentation verdict.
2. Keep at least one same-behavior companion lane where only locale, label-source, trusted-renderer, or anti-redressing posture changes.
3. Reject archive summaries that say only “the user consented” when the archive no longer preserves what the user was shown.



## Additional compact pass: ceremony topology, device split, and invocation routes

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/ceremony_topology_device_split_and_invocation_routes_are_world_contracts_not_just_app_launch_plumbing.md`
- Extended `docs/RESEARCH_SOURCES.md` with:
  - `RS-GR-501` through `RS-GR-508` (OpenID4VP cross-device QR/request-by-reference guidance, SIOPv2 same-device versus cross-device invocation models, claimed-HTTPS versus custom-scheme dispatch posture from RFC 8252, CTAP hybrid proximity semantics, and NIST out-of-band participation rules).
- Added compact local artifacts:
  - `artifacts/process/ceremony_topology_and_device_split_receipt_20260322.json`
  - `artifacts/process/ceremony_topology_demo_20260322.json`
- Threaded those constraints into:
  - `docs/RESEARCH_AGENDA.md`
  - `docs/RESEARCH_OPINIONS.md`
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
- Repaired bundle usability for the next inheritor by restoring executable bits on `scripts/**/*.sh`, `scripts/**/*.py`, `.githooks/*`, `grpy`, `tools/rust_exec.sh`, `afk_concord.sh`, and `loop.sh` before repackaging.

### New research / inheritor insight

The archive already knew to preserve delivery paths, approval rendering, verifier targeting, transaction intent, and authenticator assurance.
The next missing layer is that a future inheritor can still keep all of that and yet not know **which device was supposed to act, how the wallet or authenticator was invoked, whether app dispatch was strongly bound, and what explicit co-presence evidence linked the displayed request to the responding device**.

- `RS-GR-501` shows that OpenID4VP explicitly treats cross-device QR transfer as a first-class case and recommends `request_uri` plus `direct_post`, which means device split is already protocol-visible.
- `RS-GR-502` and `RS-GR-503` show that SIOPv2 separates same-device from cross-device models and distinguishes untargeted scan flows from targeted `authorization_endpoint` launches, which means manual wallet selection versus pre-targeted invocation is part of the world contract.
- `RS-GR-504` and `RS-GR-505` show that claimed HTTPS links and private custom schemes are not dispatch-equivalent, which means future inheritors need the invocation route itself instead of a generic “wallet opened” statement.
- `RS-GR-506` and `RS-GR-507` show that CTAP hybrid transport separates network carriage from physical-proximity proof and requires explicit proximity evidence for QR-initiated flows, which means not all cross-device ceremonies provide the same co-presence assurance.
- `RS-GR-508` shows that NIST treats out-of-band or cross-channel assurance as valid only when claimant participation actually bridges the channels, which means a multi-device ceremony is incomplete unless the archive preserves how the human linked the channels.

So the next implementor should avoid two more easy mistakes:

1. treating “the wallet returned a valid response” as replay-complete when the archive no longer preserves whether the ceremony was same-device, cross-device, or hybrid, and how the wallet was actually reached;
2. attributing gains from claimed-link dispatch, targeted wallet selection, or proximity-proven hybrid handoff to generic Golden-Rule progress instead of narrower ceremony-topology hardening.

### Recommended next move

1. Preserve one compact ceremony-topology receipt beside each material presentation or authorization verdict.
2. Keep at least one same-behavior companion lane where only device split, invocation route, dispatch assurance, or co-presence proof changes.
3. Reject archive summaries that say only “the wallet answered” when the archive no longer preserves how the answering device was selected and bound to the displayed request.


## Additional compact implementation pass: machine-checkable successor-safe ceremony receipts

### What changed

- Added one compact inheritor-facing note:
  - `docs/LIBRARY/topics/golden_rule_archives_should_ship_a_machine_checkable_successor_safe_ceremony_receipt_schema_and_worked_example.md`
- Added one compact schema and tiny local tool:
  - `schemas/successor_safe_ceremony_receipt.schema.json`
  - `scripts/tools/successor_safe_ceremony_receipt.py`
- Added one compact validator and one worked example snapshot:
  - `scripts/test/check_successor_safe_ceremony_receipt.py`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.json`
  - `examples/snapshots/successor_safe_ceremony_receipt_example.md`
- Added one compact process receipt:
  - `artifacts/process/successor_safe_ceremony_receipt_tooling_receipt_20260322.json`
- Threaded the implementation move into:
  - `docs/LIBRARY/topics/golden_rule_inheritor_brief.md`
  - `docs/LIBRARY/README.md`
  - `docs/AGENT_LOG.md`
  - `CHANGELOG.md`

### New research / inheritor insight

The archive already learned that successor-safe ceremony retention depends on at least six distinct contracts: the structured request, verifier targeting and replay scope, delivery path, approval rendering, ceremony topology, and linkability or retention posture.

The next implementor risk is no longer conceptual ignorance.
It is **scattering**: preserving all the right facts across several notes and ad hoc local receipts, then forcing a future session to reassemble them before deciding whether two ceremonies were materially the same.

A tighter handoff is now available: one machine-checkable successor-safe ceremony receipt that keeps those decisive facts in one compact object.

- `RS-GR-434` through `RS-GR-437` justify preserving structured request shape and satisfaction route rather than inferring them from returned disclosures.
- `RS-GR-441` through `RS-GR-447` justify preserving verifier, origin, route, and replay binding rather than generic proof validity.
- `RS-GR-486` through `RS-GR-492` justify preserving request and response carriage plus plaintext observer surface rather than saying only that a proof was delivered.
- `RS-GR-493` through `RS-GR-500` justify preserving what the human actually saw and approved rather than saying only that consent occurred.
- `RS-GR-501` through `RS-GR-508` justify preserving device split, invocation route, dispatch assurance, and cross-channel participation rather than saying only that a wallet or authenticator answered.

So the next implementor should avoid one more easy mistake:

1. treating the current protocol-world map as complete while still storing it in too many scattered prose fragments for a future inheritor to validate cheaply.

### Recommended next move

1. Prefer one compact successor-safe ceremony receipt per material ceremony over several local prose summaries.
2. Keep the receipt schema narrow and diffable; cite large payloads rather than retaining them.
3. Reject archive summaries that say only “the request was valid and the user approved” when no single retained object still states *how* that ceremony was targeted, carried, shown, and completed.
4. Once a package becomes claim-ready, keep one compact review watch with a reviewed-on date, a no-later-than review interval, explicit reopen-trigger codes, and the exact regeneration sequence, so future sessions know when freshness rather than structure has failed.

## Additional compact implementation pass: review verdicts over freshness watches

### What changed

- Added one more tiny successor-safe ceremony artifact: `schemas/successor_safe_ceremony_receipt_review_verdict.schema.json`.
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with `review`, which evaluates a review watch at one as-of date plus optional observed trigger codes.
- Committed the worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.review_verdict.json`.

### New research / inheritor insight

A review watch is necessary but not sufficient. It says when a package should reopen, but it still leaves one decisive stewarding question implicit: **as of today, may this package still be cited?**

The archive now has a tiny machine-checkable answer to that question. A review verdict binds one watched locator, one as-of date, any matched trigger codes, one timeliness state, and one explicit keep-citing versus reopen-now decision. That means freshness evaluation no longer has to live in chat memory or operator inference.

## Additional compact implementation pass: citation advisories over review verdicts

### What changed

- Added one more tiny successor-safe ceremony artifact: `schemas/successor_safe_ceremony_receipt_citation_advisory.schema.json`.
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with `advise`, which collapses a review verdict into one downstream citation-handling object.
- Committed the worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.citation_advisory.json`.

### New research / inheritor insight

A review verdict is necessary but not sufficient. It says whether a watched locator stayed claim-ready at one as-of date, but it still leaves one stewarding question implicit: **what should future notes do with that locator now?**

The archive now has a tiny machine-checkable answer to that question. A citation advisory binds one reviewed locator, one source review verdict, one keep-versus-withdraw decision, one action for existing citations, and one action for new citations. That means downstream citation handling no longer has to live in chat memory or operator folklore.



## Additional compact implementation pass: package lineage over package supersession

### What changed

- Added one more tiny successor-safe ceremony artifact: `schemas/successor_safe_ceremony_receipt_package_lineage.schema.json`.
- Extended `scripts/tools/successor_safe_ceremony_receipt.py` with `lineage`, which collapses one or more package manifests plus their supersession records into one authoritative ordered chain.
- Committed the worked snapshot `examples/snapshots/successor_safe_ceremony_receipt_example.package_lineage.json`.

### New research / inheritor insight

A package supersession record is necessary but not sufficient once there is more than one package refresh. It says which one package replaced one older package, but it still leaves one stewarding question too expensive: **which package head is authoritative right now, across the whole local chain?**

The archive now has a tiny machine-checkable answer to that question. A package lineage record binds the authoritative manifest head, the ordered manifest chain, the ordered supersession chain, the locator-continuity result, and the current review/advisory basis that keeps the head authoritative. That means package authority no longer has to live in filename-reading or changelog reconstruction.
