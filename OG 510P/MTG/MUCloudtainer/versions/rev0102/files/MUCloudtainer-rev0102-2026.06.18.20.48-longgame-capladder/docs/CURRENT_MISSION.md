# MUCloudtainer — current mission

**Revision:** rev0101 (`transferstress-oodpanel`)  
**Status:** current synthesis. rev0090 remains the historical deep diagnosis; rev0091 and rev0092 close its two most urgent executable blockers; rev0093 adds reduced equilibrium calibration; rev0094 stress-tests the first PSRO expansion; rev0095 turns the next generative-oracle branch into runnable code, rev0096-rev0098 reactivate and audit neural/learned oracle branches, and rev0099 refreshes the expanded empirical matrix with shared balanced evaluation design, rev0100 separates fixed-incumbent confidence floors from self-diagonal conventions, and rev0101 runs an out-of-distribution transfer-stress panel against the admitted response.

## The heart of the mission

MUCloudtainer is a closed-world, reproducible imperfect-information laboratory whose most valuable behavior is not producing a flattering win rate. It is:

> propose a strategic answer, reproduce it, expose what caused it, construct an adversarial response, and retract or narrow the answer when it fails.

The five-card game is the substrate. The durable product is a **claim-autopsy and answer-generation loop**. The original numerical, evolutionary, neural, and game-theoretic methods still belong, but they should now serve that loop rather than operate as isolated demonstrations.

## Where the project stands now

The two immediate blockers identified in rev0090 are no longer merely documented.

### Information semantics are executable

rev0091 added a durable policy-facing information state: ordered public/private events, persistent known-top-card facts, public exile identities, and replay-bound information fingerprints. Legacy agents may still use the compact observation, but learning or recurrent agents now have a correct place to receive remembered information.

### Stateful policy lifecycle is executable

rev0092 adds a seat-scoped episode contract. Reused policy wrappers are reset before every game and may receive public terminal feedback afterward. One mutable wrapper cannot occupy both seats. Payoff caches and the PSRO evaluator maintain distinct seat objects, and their cache identity includes the full strategy signature rather than trusting a recycled human-readable name.

This closes the immediate cross-game and cross-seat memory-leak risk for recurrent, neural, and search policies.

### The adversarial bootstrap is now code

rev0092 turns the cube's manual “invent a response, test it, add it” habit into its first executable finite-oracle PSRO round:

```text
current empirical population
        ↓
solve restricted zero-sum game
        ↓
score candidate responses to the opponent mixture
        ↓
seed-disjoint screening, holdout, and confirmation
        ↓
add a confirmed response to an exploratory population
        ↓
rebuild and re-solve the expanded game
```

This is not yet an autonomous learning system. The candidate oracle is finite: eight policy upgrades plus eight diverse proposals from the old MAP-Elites descriptor archive. But the outer loop is real and reusable.

## What rev0092 learned

The original eight-strategy restricted game produced an exact 0.5 value and an opponent mixture supported on:

- `pub_threat60_closure`: 0.20
- `pub_threat60_surge`: 0.80

A proposal from the rev0014 descriptor archive survived three seed-disjoint stages. Its deck is:

```text
60 cards
25 Island
21 Counterspell
4 Force of Will
5 Jace, the Mind Sculptor
5 Overlord of the Floodpits
```

Against the restricted mixture's support, the final confirmation score was **0.735**, with a normal-approximation 95% interval of **[0.654, 0.816]** over 160 balanced game rows and zero truncations. It was therefore added to the **exploratory empirical-game population**, not promoted as a general strategic answer.

The expanded nine-strategy matrix placed nearly all approximate equilibrium mass on that candidate. This is a strong reason to continue attacking it, not a reason to declare victory: each expanded off-diagonal cell currently has only 16 balanced game rows.

## The important negative result

The confirmed candidate used the new information-state-aware `counter_guard` wrapper. A paired ablation then replayed the same deck, mulligan policy, opponents, and 96 seeds with and without the information-state adjustment.

The paired outcome delta was exactly **0.0** in all 96 pairs.

Therefore the observed response gain belongs to the **deck/population search**, not to the hand-written information-state bonus. The wrapper remains useful as a contract test because controlled frames prove that information can change its action, but rev0092 supplies no strategic evidence that the wrapper is better.

This attribution is the mission working correctly: keep the result, remove the wrong explanation.

## The original methods, reassembled

The project should no longer ask which method becomes “the champion.” The useful architecture is:

```text
PSRO / double-oracle outer loop
        ├── exact numerical probes and meta-solver
        ├── enumerative constructor oracle
        ├── gameplay-driven evolutionary / MAP-Elites oracle
        ├── readable code-policy oracle
        ├── neural response oracle
        └── reduced CFR/search calibration oracle

replay, holdout, mechanism analysis, and claim demotion under all of them
```

`docs/CURRENT_METHODS.md` records what each historical branch actually accomplished, what it did not accomplish, and the implementation order from here.

## What rev0093 adds

rev0093 implements the reduced equilibrium reference that rev0092 identified as the highest-risk method gap. `src/muc5/reduced_cfr.py` defines a tiny independent extensive-form game preserving Jace private known-top knowledge, public leave/bottom events, Force pitch visibility, and closure. `scripts/run_rev0093_reduced_cfr.py` solves it with deterministic tabular CFR and measures exploitability with an information-set-grouped best response, not a hidden-state-peeking shortcut.

The audit converges from exploitability **0.0297473171** at iteration 1 to **0.00000618837** at iteration 5,000 over **33 information sets**. This is not a full MUC-5 solve. It is the first executable calibration object for CFR/search and neural/evolutionary information-state learners.

rev0093 also refactors PSRO support pruning into a centralized `positive_mixture_support()` helper so exact-zero opponent omission is shared, tested, and auditable instead of being inline runner logic.


## What rev0094 adds

rev0094 does not invent another hand policy. It attacks the most fragile consequence of rev0092: the admitted MAP-Elites response dominated the low-resolution expanded matrix, but had not yet been treated as the sole target of a second response oracle. The expanded solver also left tiny fictitious-play residue on the old eight strategies, which could cause a future oracle to spend most of its budget on weights that can change the estimand by less than one ten-thousandth.

`src/muc5/psro.py` now records effective mixture-support pruning with an explicit payoff-error bound. With tolerance `0.001`, the rev0092 expanded-game mixture reduces to the admitted response alone:

```text
included weight: 0.999920007199352
omitted weight / maximum score error from pruning: 0.00007999280064796555
```

`src/muc5/psro_catalog.py` lifts the response population, finite oracle catalog, and incumbent pure-response controls out of one-off runner code. Future PSRO, evolutionary, and neural experiments now share one catalog constructor instead of copying strategy-order literals.

`scripts/run_rev0094_psro_stress.py` runs a second-oracle stress panel against the admitted response. It evaluates 23 challenge candidates, holds out the top four nonduplicate proposals on disjoint seeds, and separately stress-tests all eight incumbents as pure responses. No second response passes the confirmation-style holdout screen. The admitted response scores above 0.5 in mean against every incumbent in the pure-response stress panel; the lowest mean is **0.5833** against `pub_threat60_pressure` over 48 balanced rows. This is encouraging but still not a strategic promotion because the weakest confidence lower bound is only **0.4424**.

The current interpretation is therefore: the first PSRO expansion is not immediately refuted by the available finite catalog or incumbents, but the next scientific step should be a genuinely generative oracle, not declaring victory.


## What rev0095 adds

rev0095 implements the first **gameplay-driven generative MAP-Elites oracle**. Earlier MAP-Elites work illuminated deck descriptors with static construction quality; rev0095 uses actual rollout value against the current effective PSRO support as cell quality.

The target is the rev0092 admitted response isolated by rev0094 effective-support pruning. The generator remeasures seed/static proposals, mutates elite decks, samples random plausible decks, assigns bounded pilot templates, and holds out the strongest cells on seed-disjoint rows. It evaluates 44 nonduplicate candidates, fills 26 gameplay archive cells, produces 592 balanced game rows, and records zero truncations and zero seed overlap.

The strongest holdout point estimate is a 40-card pressure/business challenger:

```text
16 Island
12 Counterspell
0 Force of Will
7 Jace
5 Overlord
mean vs admitted response: 0.5625 over 48 rows
95% interval: [0.4207, 0.7043]
```

That candidate does not clear the challenge threshold, so rev0095 admits no response and promotes no strategy. The substantive progress is method capability: PSRO now has a bounded generative oracle whose outputs are gameplay-scored, auditable, and repeatable.



## What rev0096 adds

rev0096 brings back the neural branch as a bounded, falsifiable response oracle instead of a black-box aspiration. The dormant rev0023 frozen MLP action-ranker is audited, wrapped into a 40-candidate response catalog, and evaluated against the current effective PSRO support with the same support-pruning, duplicate guard, seed-disjoint holdout, and nonpromotion discipline used by the MAP-Elites oracle.

The result is negative and useful: the best holdout neural candidate scores only **0.1458** against `oracle_map_08_60_mixed_threats_counter_wall` over 48 balanced rows. No confirmation stage is triggered and no strategy is promoted. The old MLP plumbing is intact, but historical imitation does not translate into a current best response.

rev0096 also factors shared oracle-runner evidence helpers into `src/muc5/oracle_reporting.py` and makes the rev0095 MAP-Elites runner consume those helpers, reducing copy-pasted audit plumbing.


## What rev0099 adds

rev0099 attacks the measurement risk behind the current PSRO target. The rev0092 admitted response had dominated a low-resolution expanded matrix, and subsequent oracle work mostly challenged that response as a one-target support. The missing hardening step was to refresh the full nine-strategy matrix with more balanced rows and make the seat/start design reusable.

`src/muc5/evaluation_design.py` now centralizes the canonical focal-pair design: configured life totals, repetitions, both physical seats, and both starting-player roles. `EmpiricalGameEvaluator.evaluate_focal_pair()` uses that helper instead of carrying a local loop, and `tests/test_rev0099_evaluation_design.py` verifies both complete designs and malformed-row detection.

`scripts/run_rev0099_matrix_refresh.py` rebuilds the nine-strategy empirical matrix with 36 off-diagonal pairs and 80 balanced game rows per pair, for **2,880** game rows total and zero truncations. The matrix is exactly constant-sum (`max |M + Mᵀ - 1| = 0.0`) with a 0.5 diagonal. The solved empirical game still puts effective 1e-3 support only on `oracle_map_08_60_mixed_threats_counter_wall`, with row mixture weight **0.9996001799** and refreshed pure floor **0.5** against the nine-strategy population.

This strengthens the current target for future response oracles. It is still not a strategic promotion: the claim is only that the expanded fixed-population target is less under-sampled and that future runners share an audited seat/start design.

## Highest-risk unfinished work

### 1. Train or search directly against the refreshed PSRO target

rev0095-rev0098 tried finite-catalog, gameplay MAP-Elites, frozen MLP, learned-response, and cross-oracle frontier probes without confirming a challenger. rev0099 refreshes the nine-strategy matrix and keeps the admitted response as the effective support target. The highest-risk unfinished work is now active response generation with better sample efficiency: either a larger preregistered gameplay-MAP-Elites budget, a fresh neural learner trained against the fixed mixture, or a PSRO round that compares several oracle families under equal rollout budgets.

### 2. Extend the reduced equilibrium reference only when needed

The first reduced CFR reference now exists. Do not inflate it into a parallel simulator by default. Expand it only for a named missing mechanism, such as explicit deck-size axes, starting-life regimes, or a second closure route that materially affects PSRO oracle comparisons.

### 3. Neural work after the frozen-MLP negative control

The rev0096 frozen-MLP oracle establishes that the old imitation model is not a useful current response oracle. A new neural branch should optimize response value against a fixed opponent mixture using the rev0091 information state and rev0092 lifecycle. Its scientific question remains whether training discovers a profitable deviation missed by enumeration, evolution, and readable policies.

### 4. Repeated expansion and stopping

One PSRO expansion is a bootstrap. Repeat with fresh oracle proposals and untouched confirmation seeds. A practical stopping rule is two consecutive rounds in which no oracle family produces a confirmed gain larger than a declared utility margin.

## Refactor lesson from rev0092

Response evaluation originally played every candidate against every population member, including strategies assigned exact zero probability by the solved opponent mixture. Those games cannot affect the weighted response estimate.

rev0092 now evaluates only the positive-weight support. In this round that reduced response-stage work from a counterfactual 3,200 rows to 800 rows, avoiding 2,400 irrelevant games. Across the complete round, including restricted and expanded matrices, it reduced the counterfactual total from 4,224 to 1,824 game rows: **56.8% less simulation without changing the estimand**.

This is the kind of audit/refactor the cube needs: remove work that cannot change the answer.

## Scope discipline

- A confirmed response may enter an exploratory PSRO population without becoming a promoted strategic claim.
- Screening, holdout, and final confirmation use disjoint seed namespaces.
- Exact-zero mixture opponents may be omitted from response evaluation; tiny numerical solver residue may also be omitted only when the omitted mass and payoff-error bound are recorded. Full matrices must still evaluate all off-diagonal pairs.
- Information-state policy effects require direct ablation; they may not inherit credit from a deck change.
- The next revision should add an oracle capability, a reduced-game reference, or a materially stronger falsifier—not another narrative quartet.

## Current authorities

- `docs/CURRENT_SPEC.md` — executable information, lifecycle, and empirical-oracle rules.
- `docs/CURRENT_METHODS.md` — method history, present architecture, and implementation order.
- `data/rev0092_psro_round.json` — complete first round, confirmation, ablation, expansion, and efficiency accounting.
- `data/rev0092_psro_bootstrap_audit.json` — first PSRO-round executable checks.
- `data/rev0093_reduced_cfr_summary.json` — reduced CFR calibration result.
- `data/rev0093_reduced_cfr_audit.json` — reduced-game information projection and exploitability checks.
- `data/rev0094_psro_stress_summary.json` — second-oracle stress panel against the first admitted PSRO response.
- `data/rev0094_psro_stress_audit.json` — effective-support, seed-disjointness, truncation, and incumbent-stress checks.
- `data/rev0095_gameplay_map_elites_summary.json` — gameplay-driven MAP-Elites oracle run.
- `data/rev0096_neural_oracle_summary.json` — frozen-MLP neural oracle negative-control run.
- `data/rev0096_neural_oracle_audit.json` — neural model audit, candidate count, seed-disjointness, truncation, and nonpromotion checks.


## rev0097 learned response oracle

The riskiest unfinished method branch was a learned policy trained for the current opponent mixture rather than reused from old imitation data. rev0097 implements the smallest auditable version: a 47-feature information-state linear scorer loaded through the normal public-agent factory, trained by rollout search, and tested against the current effective PSRO support.

The outcome is a nonpromotion result. The learner found strong training and selection point estimates, but seed-disjoint holdout did not support admission. This is valuable because it exposes rollout overfitting before a learned policy can enter the population. The next priority is a shared oracle-selection audit that quantifies selection-to-holdout optimism across finite catalog, MAP-Elites, frozen neural, and learned-response branches.

## rev0098 selection-bias audit and frontier retest

rev0098 targets the risk exposed by rev0097: oracle screens can produce attractive winners that shrink or reverse on seed-disjoint holdout. Instead of adding another method family, rev0098 adds a shared selection-bias audit across rev0094 finite-catalog stress, rev0095 gameplay MAP-Elites, rev0096 frozen MLP, and rev0097 learned-response branches.

The audit reads 190 compact score rows and finds 19 candidates with both screen and holdout evidence. No branch clears the declared holdout confidence threshold. The largest within-candidate selection-to-holdout drop is a learned-response candidate that falls from 0.7500 on selection to 0.28125 on holdout. The largest branch-level screen-to-best-holdout gap is also learned response: 0.8750 screen versus 0.4375 holdout.

rev0098 also retests each branch's best holdout challenger against the rev0092 admitted response under one common configuration: 96 games per candidate, 480 total rows, zero truncations, and zero seed overlap. The best challenger is the learned-response holdout winner at 0.4479 with CI [0.3479, 0.5479]. The MAP-Elites challenger falls to 0.3854 with CI [0.2875, 0.4833]. No challenger clears 0.5 by confidence lower bound, no population admission occurs, and no strategic policy is promoted.

The next priority is not more branch proliferation. It is better oracle sample efficiency: larger declared budgets, sequentially valid screening, or common-target retests before confirmation.

- `data/rev0099_expanded_matrix_refresh_summary.json` — refreshed nine-strategy empirical matrix and solver result.
- `data/rev0099_expanded_matrix_refresh_audit.json` — balanced-row, antisymmetry, truncation, and evidence-catalog checks.

## What rev0100 adds

rev0100 fixes the most important measurement ambiguity left by rev0099. The expanded matrix reported the admitted response's `pure_floor_vs_population` as `0.5`, but that was the self diagonal used by the constant-sum matrix convention, not an incumbent opponent result.

`src/muc5/confidence_floor.py` now separates matrix self floors from non-self opponent floors. `scripts/run_rev0100_confidence_floor.py` remeasures the admitted PSRO response against each of the original eight incumbents at 240 balanced game rows per pair, plus a separate self-control diagnostic.

The rev0100 result is:

```text
rev0099 floor including self diagonal: 0.5
rev0099 floor excluding self:          0.6625
rev0100 weakest incumbent mean:        0.6625
rev0100 weakest incumbent CI lower:    0.6025503087483217
weakest incumbent:                     pub_threat60_closure
self-control mean:                     0.4875
truncations:                           0
```

This materially strengthens the current PSRO target against the fixed incumbent population. It remains scoped evidence, not a final answer or strategic promotion. The next risky move is to continue treating `oracle_map_08_60_mixed_threats_counter_wall` as the target to beat with stronger generative/search oracles.


## What rev0101 adds

rev0101 takes the next risky step after the rev0100 fixed-incumbent confidence floor: it asks whether the admitted PSRO response transfers outside the original eight-strategy ecology. The new `src/muc5/transfer_stress.py` module builds a 13-opponent OOD panel containing branch-frontier challengers, degenerate threat-density decks, Force-heavy pressure, and counter-control/Jace-control shapes. `scripts/run_rev0101_transfer_stress.py` evaluates the admitted response as the focal strategy with balanced life/seat/start rows, a separate self-control diagnostic, and a truncation-rescue check.

The result is deliberately not promotional. The admitted response beats every OOD opponent in mean, but it does not clear a confidence floor: the weakest OOD mean is 0.528125, the weakest lower bound is 0.4507726356760219, and one counter-control/Jace seed remains unresolved after a 1,600-decision rescue cap. The weakest opponent is `ood_counter_jace40`, not a pure threat-rush deck.

That changes the next attack surface. The branch-frontier challengers from rev0094-rev0098 are no longer the highest-risk immediate area. Counter-control mirrors, no-Overlord Jace-control, and long-game adjudication are the risky axes that future oracles should target.

## What rev0102 adds

rev0102 attacks the long-game debt exposed by rev0101 instead of broadening the opponent panel again. The original `ood_counter_jace40` cap row now has a deterministic cap ladder at 1,400, 1,600, 2,400, 3,200, and 5,000 decisions, plus counts-only terminal snapshots. The cell remains nonterminal even at 5,000 decisions, so the issue is a persistent counter/Jace control loop rather than a simple too-low cap.

A high-cap refresh of the `ood_counter_jace40` axis gives the admitted PSRO response a mean of 0.5859375 with a 95% interval of [0.5162701255397072, 0.6556048744602928] across 192 games, but one cap row remains. The confidence floor is therefore still open by the truncation gate even though the lower interval now exceeds 0.5.

The next risky decision is semantic rather than statistical: MUC-5 must either keep cap rows as half-point draws, add an explicit repetition/draw rule, or change pilot objectives to avoid pathological Jace-control loops. No strategy is promoted.
