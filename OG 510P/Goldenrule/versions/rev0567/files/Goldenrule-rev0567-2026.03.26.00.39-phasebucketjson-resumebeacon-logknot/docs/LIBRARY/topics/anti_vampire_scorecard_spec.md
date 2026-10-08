# Anti-Vampire Scorecard Specification

## Status

**Screening proxy + declared contract spec implemented.** `grlab certify` now emits all five current anti-vampire scorecard fields for memory-one pairs: `own_payoff`, `payoff_gap`, `recovery_rounds`, `repair_abuse_rate`, and `ecology_gap_noisy`, plus a compact `screening_contract` surface that makes the current gate explicit, a `screening_spec_ref` that points at the declared proxy contract used for the run by both `spec_id` and an immutable `spec_fingerprint_sha256` of the effective normalized screening spec, a declared `stage_game_ref` plus explicit `state_order` so the reported payoffs and occupancy vectors stay attached to the actual game contract and vector basis used for the run, compact uncertainty summaries for the rollout-derived ecology and repair proxy fields so those estimates are not mistaken for exact invariants, an uncertainty-aware binding overlay (`binding_gate_status`, `gate_stability`, per-check `threshold_decision_state`) so a future inheritor can tell whether a binding pass/fail is sharp or borderline under the current interval summary, compact `ecology_sampling_ref` / `repair_sampling_ref` objects so the actual Monte Carlo seed schedule is part of the declared result surface rather than a hidden implementation detail, an explicit `uncertainty_contract_ref` so the interval semantics used to interpret those noisy estimates are declared rather than silently living in Python, an explicit `proxy_measurement_contract_ref` so the sign conventions, pool aggregation rule, shock-recovery semantics, and repair-offer / repair-abuse event semantics for the proxy fields are also declared rather than silently living in Python, an explicit `steady_state_contract_ref` so the exact-stationary solve semantics, cleanup tolerances, and singularity fallback rule behind the top-level payoff / occupancy surface are also declared rather than silently living in Python, and an explicit `opening_distribution_contract_ref` so the construction rule behind the declared opening distribution is also declared rather than silently living in Python, and an explicit `transition_kernel_contract_ref` plus top-level `transition_matrix`, and compact `transition_graph_diagnostics` describing communicating classes / closed classes / absorbing states / initial-support reachability plus exact `closed_class_entry_probabilities_from_initial_distribution`, `conditional_expected_entry_steps_from_initial_distribution`, `expected_steps_to_any_closed_class_from_initial_distribution`, and `closed_class_asymptotic_decomposition_from_initial_distribution`, so the actual 4×4 Markov kernel used for steady-state, recovery, payoff, and transient-horizon calculations is also declared rather than silently reconstructed from code and multi-basin results can be read as explicit weighted mixtures of basin-conditioned asymptotic outcomes with explicit entry timing rather than only graph possibilities, plus a top-level exact `asymptotic_distribution_from_initial_distribution` / asymptotic-payoff surface and a compact `steady_state_distribution_l1_distance_to_asymptotic_distribution` witness so reducible runs no longer require manual reconstruction to distinguish exact long-run mixtures from finite Cesàro fallback vectors. The graph diagnostics now also expose exact pre-closure cumulative payoff burden overall and conditional on each recurrent basin, exact pre-closure state-visit counts overall and conditional on each recurrent basin, and exact pre-closure transition counts overall and conditional on each recurrent basin, so reducible runs with the same long-run mixture no longer look behaviorally identical when the transient incentive cost is carried by different sides, by different off-diagonal states, or by different edge-level repair / exploitation mechanisms. The command still returns `status = screening_proxy` rather than a final certificate because the recovery threshold, repair threshold, and repair-channel semantics still need an explicit world contract. This document specifies the fuller artifact structure and scoring semantics called for in:
- `golden_rule_inheritor_brief.md` (build item 1)
- `RESEARCH_OPINIONS.md` (build item 4)
- `docs/BUCKET.md` (highest-priority item)

The current search infrastructure uses `avg_a` (own average payoff) as its primary
metric. This document defines the replacement scorecard and the currently implemented proxy subset.
It is also the standing durable handle that should subsume the `extortion_metric` report family when archive compaction needs to retire another paired extortion snapshot.

## Why avg_a alone is wrong

From `search_and_extortion.md` and the existing search artifacts:

- Short-horizon search finds candidates that maximize `avg_a` against an extortioner
  by maximizing their own score.
- But maximizing `avg_a` while facing an extortioner can still leave the extortioner
  with a *larger* payoff — meaning the vampire wins even when the "best" strategy is
  found.
- Hill climbing reduces the payoff gap but at the cost of own payoff.
- No memory-one candidate simultaneously achieves nonnegative fairness, high self-play,
  and low exploitation of Always-Cooperate. (`memory_one_tradeoff_against_extortion.md`)

"Maximize my score against the vampire" is not the same as "resist vampirism."
The scorecard operationalizes the second goal.

## The core fields

### 1. `own_payoff`

Average payoff per round to the focal agent across all replications.

- Retain this field. It is necessary but not sufficient.
- A high `own_payoff` against an extortioner is only good if the vampire is not
  receiving a proportionally larger payoff (see `payoff_gap`).

### 2. `payoff_gap`

`(vampire_avg_payoff - own_avg_payoff)` per round.

- Nonnegative fairness criterion: `payoff_gap <= 0` is required for a strategy
  to pass the anti-vampire threshold.
- A strategy that achieves positive `own_payoff` but positive `payoff_gap` is
  feeding the vampire, not resisting it.
- This is the field that catches the metric trap. Include it in every extortion-world
  result artifact.

### 3. `recovery_rounds`

After a defection shock (either noise-induced or intentional), the number of rounds
until the focal agent's rolling average payoff returns to within `epsilon` of the
mutual-cooperation baseline.

- Measures forgiveness and repair capability.
- A strategy that never recovers (pure retaliation) fails this field.
- A strategy that recovers instantly may be exploiting a repair channel (see
  `repair_abuse_rate`).
- `epsilon` and the shock protocol should be fixed in the world spec and logged
  in the result artifact.

### 4. `repair_abuse_rate`

Proportion of repair-channel invocations (apology signals, cooperation offers after
defection) that are followed by a subsequent defection within `k` rounds by the
opponent.

- Measures whether repair channels are being weaponized by a vampire.
- A high `repair_abuse_rate` means the focal agent's forgiveness is being exploited
  as a cycle: defect → apologize → defect.
- This field requires a world that supports a repair-channel signal. In worlds
  without an explicit signal, a proxy can be used: proportion of C-after-D rounds
  from the opponent that are followed by D within `k` rounds.

## Proposed artifact schema addition

```json
{
  "screening_spec_ref": {
    "schema_version": 1,
    "kind": "certify_memory_one_screening_spec",
    "spec_id": "canonical_proxy_v1",
    "spec_fingerprint_sha256": "<sha256 of effective normalized screening spec>"
  },
  "anti_vampire_scorecard": {
    "screening_spec_ref": {
      "schema_version": 1,
      "kind": "certify_memory_one_screening_spec",
      "spec_id": "canonical_proxy_v1",
      "spec_fingerprint_sha256": "<same sha256>"
    },
    "own_payoff": <float>,
    "payoff_gap": <float>,
    "recovery_rounds": <int>,
    "shock_protocol": "<string ref to declared shock protocol>",
    "repair_abuse_rate": <float>,
    "repair_proxy_k": <int>,
    "notes": "<string>"
  }
}
```

The current proxy fields are now non-null in the memory-one lane, but they remain **proxy semantics** until a world contract, repair channel, and final thresholds are declared at the world level rather than only in a proxy spec.

## Current proxy implementation status

The current `grlab certify` screening proxy now computes these fields for memory-one strategies:
- `own_payoff`
- `payoff_gap`
- `recovery_rounds`
- `repair_abuse_rate`
- `ecology_gap_noisy`

The last two repair-oriented fields remain **proxy semantics**, not final world-certified semantics:
- `recovery_rounds` currently means the first post-shock round where the focal side's exact expected one-step payoff returns within `epsilon = 0.25` of the mutual-cooperation baseline **and** the exact `CC` mass is at least `0.8`, under the canonical shock protocol `opponent_single_defection_from_mutual_cooperation_then_zero_noise_expected_payoff_recovery`.
- `repair_abuse_rate` currently means the share of opponent `D -> C` repair offers that are followed by another opponent `D` within `k = 3` rounds in the noisy pair rollout proxy used by `grlab certify`.

So the current command should still be treated as a **screening scorecard**, not as the final full anti-vampire certificate.
It is already strong enough to catch the old payoff-only trap, distinguish repairable reciprocity from non-recovering extraction in the current proxy lane, and preserve the noisy-ecology ZD extraction failure mode without pretending the repair-contract problem is fully solved.

For the pair-level occupancy/payoff summary above the scorecard, `grlab certify` now prefers the exact stationary solve when that four-state chain is well-conditioned and otherwise falls back to a long-run Cesàro occupancy average from the declared `p0` opening distribution. The JSON payload exposes that choice via `steady_state_method` plus `initial_distribution`, so reducible/multi-basin memory-one pairs remain certifiable without hiding their path dependence.

The result payload is now also schema-backed at `schemas/certify_memory_one_result.schema.json`, and the proxy contract itself is now declared separately at `schemas/certify_memory_one_screening_spec.schema.json` with a shipped canonical example in `examples/certify/canonical_proxy_v1.json`. That pair of schemas deliberately keeps the current anti-vampire lane narrow: it records one typed memory-one certify result, the anti-vampire scorecard, the current screening contract, and the declared proxy contract used to produce them, but it does **not** pretend the archive has already fixed the final world-certified recovery / repair thresholds.

The current `screening_contract` is intentionally split into:
- **binding checks**: `pairwise_fairness` and `noisy_ecology`
- **advisory checks**: `recovery_proxy` and `repair_proxy`

So the command can answer two inheritor questions cleanly without archive bloat:
1. does this pair fail the current anti-extraction screen right now?
2. which remaining recovery/repair pieces are still proxy-only rather than world-declared?
3. which declared proxy contract produced this answer, and can a future session rerun or replace that contract without editing Python?

The canonical proxy lane is now shipped as a first-class example spec, so future sessions can tighten or relax thresholds, swap the ecology pool, or change rollout budgets declaratively via `--screening-spec` rather than by patching hardcoded module constants.

The current `screening_contract.gate_pass` still means **the declared point-estimate binding gate passed**. That field is now deliberately paired with `binding_gate_status` and `gate_stability`, because a point estimate can pass while the current noisy-ecology CI still crosses the active threshold. Future triage should therefore treat `(gate_pass, binding_gate_status, gate_stability)` as the minimal honest decision surface until the archive either adopts adaptive rerun rules for borderline cases or declares a world-level uncertainty contract.

The result payload now also records `screening_spec_ref.spec_fingerprint_sha256`, defined over the **effective normalized screening spec** after any CLI/runtime overrides are applied. This matters because two runs can still share `spec_id = canonical_proxy_v1` while differing in ecology rollout budgets or other declared knobs. Future comparisons should therefore treat `(spec_id, spec_fingerprint_sha256)` as the compact contract identity, not `spec_id` alone.

The result payload now also records immutable `strategy_a_ref` / `strategy_b_ref` objects and ordered `pairing_ref.pairing_fingerprint_sha256`. This closes the next silent comparison failure mode: two certify runs can share the same visible strategy ids while differing in the underlying memory-one probabilities, and `A vs B` is not interchangeable with `B vs A`. Future comparisons should therefore treat the full ordered pairing fingerprint as the compact certify-object identity whenever the scientific question is about one concrete run surface rather than only about the declared screening contract.

The result payload now additionally declares `stage_game_ref` plus `state_order = [CC, CD, DC, DD]`. This closes another quiet comparison trap: a future session can keep the same strategies and the same screening contract while changing the stage-game payoffs or misreading the meaning of the steady-state vector coordinates. Future comparisons should therefore treat the certify object as living under **three** compact declared identities at once: the effective screening contract, the concrete ordered strategy pair, and the declared stage-game / state-order basis that made the reported payoffs and occupancy numbers true.

The current proxy lane now also exposes compact uncertainty summaries for the rollout-derived fields instead of presenting them as exact facts. `ecology_gap_noisy` and `ecology_own_payoff` now travel with stderr and 95% half-width summaries plus per-opponent stderr maps, while `repair_abuse_rate` now travels with its observed abuse count and a Wilson-style 95% interval. This still does **not** make the screening gate uncertainty-aware; it makes the payload honest about where the noisy numbers came from so future sessions can decide whether a threshold crossing is robust or borderline before tightening the contract.

The result payload now additionally records compact `ecology_sampling_ref` and `repair_sampling_ref` objects. These refs keep the actual seed schedule (`arithmetic_progression` with a declared base and stride) attached to the retained result without storing every replicate seed or every replicate trace.

The result payload now also records an explicit `uncertainty_contract_ref`. This keeps the current interval semantics compact but declared: the ecology uncertainty surface is currently a two-sided normal-approximation band around the replicated-rollout mean, and the repair uncertainty surface is currently a Wilson interval around the repair-offer abuse rate. Future comparisons should therefore treat the certify object as depending on **five** compact declared identities rather than four: the effective screening contract, the ordered strategy pair, the stage-game/state-order basis, the rollout sampling plan that generated the noisy proxy estimates, and the interval-semantics contract used to interpret those estimates.

The result payload now also records an explicit `steady_state_contract_ref`. This keeps the pair-level payoff / occupancy semantics compact but declared: the current lane first attempts an exact stationary solve via partial-pivot Gaussian elimination on the normalized four-state system, treats singular or ill-conditioned systems according to a declared pivot tolerance, cleans tiny masses with a declared absolute tolerance, and otherwise falls back to a Cesàro average from the declared opening distribution for `screening_spec.steady_state.cesaro_fallback_steps` steps.

The result payload now also records an explicit `opening_distribution_contract_ref`. This keeps the opening-state semantics compact but declared: the current lane constructs the initial state distribution by treating `strategy_a.p0` and `strategy_b.p0` as independent Bernoulli cooperation probabilities and then mapping those probabilities into the declared `state_order = [CC, CD, DC, DD]` via the product formulas `CC = p0_a*p0_b`, `CD = p0_a*(1-p0_b)`, `DC = (1-p0_a)*p0_b`, and `DD = (1-p0_a)*(1-p0_b)`. Future comparisons should therefore treat the certify object as depending on **eight** compact declared identities rather than seven: the effective screening contract, the ordered strategy pair, the stage-game/state-order basis, the rollout sampling plans, the interval-semantics contract, the proxy-measurement semantics contract, the steady-state solver/fallback contract, and the opening-distribution semantics contract.

## Pass/fail threshold proposal

A strategy **passes** anti-vampire certification if:

1. `payoff_gap <= 0` (nonnegative fairness: vampire does not win)
2. `recovery_rounds <= R_max` (recovers within world-specified horizon)
3. `repair_abuse_rate <= tau` (forgiveness is not a feeding loop)

where `R_max` and `tau` are declared in the world spec and logged in the scorecard.

These thresholds should be set conservatively at first and tightened as the
strategy space expands.

## What this enables

With this scorecard, the search objective changes from:

> Find the strategy with highest `avg_a` against the vampire.

to:

> Find the set of strategies that pass anti-vampire certification, then rank by
> `own_payoff` within that set.

This correctly operationalizes "resist vampirism" rather than "score well while
being exploited."

## Build order dependency

This scorecard requires:
1. A world with a defined shock protocol (already partially available in noisy worlds).
2. A world with a repair channel or a proxy for it (the `mem1_courteous_firm` and
   `mem1_exit_after_break` examples are early prototypes).
3. Schema additions to the result artifact format (above).
4. A `grlab certify` command or equivalent that evaluates the four fields and
   emits a scorecard artifact.

Step 3 is a spec change. Step 4 is a Python orchestration task. Neither requires
Rust engine changes for the proxy implementation.

## Claim policy implication

Per `RESEARCH_OPINIONS.md` item 6 and this spec:

**Forbid payoff-only claims in extortion settings.**

Any result artifact from an extortion-world experiment that does not include
`payoff_gap` should be flagged as incomplete. This should be enforced at the
schema validation level, not left to convention.

## Related library topics

- `search_and_extortion.md`: the metric trap this scorecard corrects
- `memory_one_tradeoff_against_extortion.md`: empirical context
- `virtue_vs_strategy.md`: why `payoff_gap` is morally necessary, not just
  technically useful
- `golden_rule_inheritor_brief.md`: this scorecard is build item 1
