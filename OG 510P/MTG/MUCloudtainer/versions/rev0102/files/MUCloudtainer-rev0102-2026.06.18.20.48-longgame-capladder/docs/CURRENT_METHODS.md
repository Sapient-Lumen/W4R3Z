# MUCloudtainer current methods architecture

**Revision:** rev0096 (`neuraloracle-evalspine`)  
**Purpose:** explain what the original method families meant, how far each actually went, and how they now fit one adversarial answer-generating program.

## The organizing decision

The original cube kept four broad branches alive:

1. numerical/enumerative;
2. evolutionary/quality-diversity;
3. neural policy/value learning;
4. imperfect-information search and CFR-like methods.

The later project added a population-and-response workflow without naming it as the central architecture. rev0092 makes that architecture explicit:

> **PSRO/double oracle is the outer loop. The original method families are competing response oracles and calibration tools inside it.**

This avoids a false choice between “keep investigating the answer” and “go back to machine-learning methods.” The investigation becomes the falsification layer around the methods.

## What “numerical” means here

It does not mean a neural network. It means obtaining answers by explicit calculation or finite optimization rather than by learning a black-box policy.

The cube has already used numerical methods to:

- enumerate all **771,127** legal raw deck-count vectors;
- compute exact hypergeometric opening-hand probabilities;
- rank decks with cheap static probes;
- construct empirical payoff matrices;
- solve small zero-sum matrices exactly by support enumeration;
- approximate larger matrix equilibria by deterministic fictitious play.

### Proper role now

Numerical work is the control system:

- exact deck-space coverage where enumeration is affordable;
- sanity checks for learned constructors;
- opponent-mixture calculation;
- exploitability and best-response bounds on reduced games;
- transparent baselines against which more expensive methods must justify themselves.

### What not to do

Do not attempt to enumerate the complete sequential policy space of hidden hands, ordered libraries, histories, and contingent actions. The raw deck vector space is small; the extensive-form strategy space is not.

## Evolutionary and MAP-Elites methods

### What was built

rev0014 created a 154-cell MAP-Elites-style descriptor archive spanning deck size, land density, Force density, counter density, threat composition, and life bias. It preserved diverse construction niches instead of retaining only one static-score winner.

### What was not built

It was not a gameplay evolutionary loop. Its quality was a static prior. There was no repeated cycle of gameplay fitness, parent selection, mutation, descendant evaluation, and archive replacement.

### rev0092 result

rev0092 reused eight interpretable archive cells as a finite proposal oracle. One of those proposals—not the highest static-quality cell—survived seed-disjoint response confirmation and entered the exploratory population.

This is the first evidence that the archive's diversity can matter strategically. It is not evidence that the original static quality measure was correct.

### Proper next experiment

Implement a gameplay-driven quality-diversity oracle over:

```text
deck counts
+ pilot parameters
+ mulligan parameters
+ information-use behavior
```

Fitness should be expected score against the current PSRO opponent mixture. Descriptors should preserve useful strategic niches such as size, threat/counter balance, closure mechanism, and information dependence. Every generation should use a separate evaluation seed pool from final confirmation.

## Neural methods

### What was built

The cube established substantial neural plumbing:

- an 81-feature public action representation;
- legal-action ranking;
- frozen JSON model artifacts;
- a one-hidden-layer MLP;
- learned mulligan models;
- outcome-weighted imitation variants;
- replay and C++ transition checks.

The rev0023 MLP achieved about **91.46% top-one imitation accuracy** on its held-out decision data. That showed the interface could support nonlinear action scoring.

### What was not built

The neural branch did not learn a best response through self-play or direct outcome optimization. High imitation accuracy mostly means that it reproduced the behavior in its training distribution. It also used the old snapshot observation rather than the durable rev0091 information state.

### Proper next experiment

Use a small masked policy-gradient or actor-critic response learner against a frozen PSRO opponent mixture. The policy must:

- receive `DecisionFrame.information_state` or a documented encoding of it;
- use separate recurrent state per seat;
- reset through the rev0092 episode lifecycle;
- train on one seed namespace and confirm on another;
- enter the same finite-oracle admission path as every other method.

The question is not whether “neural wins.” It is whether the neural oracle discovers a confirmed response that the enumerative, evolutionary, or readable-policy oracles miss under comparable simulation budgets.

## CFR and imperfect-information search

### What was built

The cube has public decision frames, hidden-information-safe observations, information-state fingerprints, replay, payoff matrices, and maximin solvers. These are prerequisites.

### rev0093 result

rev0093 adds the first genuine tabular CFR implementation in `src/muc5/reduced_cfr.py`. It is not a full-game export. It is an independent reduced extensive-form game designed to preserve the risky semantics: Jace private known-top memory, public leave/bottom events, Force pitch visibility, and closure.

`data/rev0093_reduced_cfr_audit.json` reports 33 information sets, 6 chance deals, and final exploitability below `1e-5` after 5,000 deterministic vanilla CFR iterations. The best-response calculation is grouped by information set; it does not maximize separately at hidden concrete states.

### Proper next experiment

Keep the reference small. Extend it only when a missing mechanism is needed for method comparison, such as deck-size axes, starting-life regimes, or a second closure route. A larger CFR/search adapter is justified only if the reduced reference starts predicting qualitative behavior the empirical PSRO loop needs to test.

## PSRO / double oracle

PSRO maintains a restricted population, solves a meta-strategy over its empirical payoff matrix, asks one or more oracles for approximate best responses to that mixture, adds confirmed responses, and repeats.

The cube had performed this manually for many revisions. rev0092 implements the first reusable outer loop in `src/muc5/psro.py`.

### rev0092 round contract

1. Build a constant-sum restricted payoff matrix with balanced seats, starting players, and life totals.
2. Solve the restricted matrix.
3. Evaluate candidate responses only against positive-weight support strategies.
4. Screen candidates on one seed namespace.
5. Evaluate the top finite set on a disjoint holdout namespace.
6. Confirm only the nominated candidate on a third namespace.
7. Add a confirmed response only to an exploratory population.
8. Rebuild and re-solve the expanded matrix.
9. Attribute mechanisms with paired ablations.

### First-round outcome

The initial eight-strategy restricted mixture was 20% `pub_threat60_closure` and 80% `pub_threat60_surge`. The confirmed response was `oracle_map_08_60_mixed_threats_counter_wall`, with final mixture score 0.735 and 95% interval [0.654, 0.816] over 160 support games.

The expanded nine-strategy matrix assigned approximately 0.99992 equilibrium mass to that candidate in both roles. This is an exploratory low-rep matrix result, not a general dominance claim.

## Information-state policy result

rev0092 introduced a readable information-state wrapper so the richer rev0091 contract could affect actions. Controlled unit frames verify that persistent known-top knowledge can change the chosen Jace action.

However, a 96-pair outcome ablation on the confirmed response found no score difference at all between the information-aware wrapper and its legacy observation-only profile. Therefore:

- the interface is action-capable;
- this round does not demonstrate strategic value from the hand-written information bonus;
- the response gain is attributed to the deck proposal;
- future learned or search policies remain free to find better uses for information state.


## rev0094 method result: stress before more methods

The immediate temptation after rev0093 was to launch a new method branch. rev0094 instead hardens the bridge between method families: the first admitted PSRO response is challenged as the effective sole opponent of the expanded meta-strategy. Tiny fictitious-play residue on old strategies is pruned with an explicit error bound, and the population/candidate catalog is refactored into `src/muc5/psro_catalog.py` so future neural and evolutionary oracles share one reconstruction path.

The stress panel says the static finite catalog is not enough to refute the admitted response. The best holdout challenger scores **0.3958** against it, with a 95% interval of **[0.2560, 0.5356]**. Incumbent pure-response controls also fail to beat it in mean; the strongest incumbent is `pub_threat60_pressure` at **0.4167**, so the admitted response's complementary mean is **0.5833**.

This result changed the priority order: the next branch should not be another fixed shortlist. rev0095 now implements that first gameplay-driven generative MAP-Elites oracle (the gameplay-driven generative oracle).

## Implementation order from rev0099

### Now: train or search, not passively rank

rev0095 gave PSRO a gameplay-driven generative MAP-Elites response oracle and found no confirmed challenger. rev0096 then reactivated the dormant frozen rev0023 MLP ranker as a bounded neural response oracle, rev0097 added a small learned-response search, rev0098 audited selection optimism across branches, and rev0099 refreshed the nine-strategy matrix with 80 balanced rows per off-diagonal pair. The frozen MLP did not merely fail to confirm; its best holdout mean against the admitted response was only 0.1458, and no later oracle branch cleared holdout.

The next neural step must therefore be direct response training or search against the solved opponent mixture, not another passive evaluation of historical imitation rankers. The next evolutionary step should be a larger declared MAP-Elites budget or a PSRO round that compares multiple oracle families under equal rollout budgets.

### Continue: reduced tabular CFR reference

rev0093 supplies the first equilibrium calibration. Keep it as a small guardrail and extend only for named missing mechanisms; do not let it become a second doctrine-heavy simulator. It may reveal policy behavior absent from the hand-authored population.

### Neural response oracle after rev0096

The frozen historical MLP is now a negative control. A serious neural branch should train a small masked policy/value learner against the fixed PSRO support, consume `DecisionFrame.information_state` or a documented encoding, and reset through the episode lifecycle. It should be compared as a response oracle, not declared a champion.

### Continue: repeated PSRO rounds

Run multiple oracle families against the same mixture. Keep method budgets, candidate counts, and confirmation rules visible. Stop only after a declared no-improvement rule, not after one attractive response.

## Explicitly deprioritized work

- A neural deck constructor for the already enumerable raw deck-count space, unless it serves as a surrogate for expensive gameplay fitness.
- More passive rankings of a fixed population without generating responses.
- Full-game Deep CFR before a reduced tabular reference exists.
- Determinized MCTS without explicit belief/information semantics.
- Another hand-named counter policy outside the oracle admission path.
- Static MAP-Elites quality treated as matchup evidence.

## External method references

- OpenSpiel algorithm inventory and PSRO tooling: https://openspiel.readthedocs.io/en/latest/algorithms.html
- Lanctot et al., “A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning” (PSRO): https://proceedings.neurips.cc/paper/2017/hash/3323fe11e9595c09af38fe67567a9394-Abstract.html
- McAleer et al., “XDO: A Double Oracle Algorithm for Extensive-Form Games”: https://proceedings.neurips.cc/paper/2021/hash/c9682aa70ea2b714eaf8e2d6ddef79a8-Abstract.html
- Brown et al., “Deep Counterfactual Regret Minimization”: https://proceedings.mlr.press/v97/brown19b.html


## rev0095 result: gameplay-driven MAP-Elites oracle

rev0095 brings back MAP-Elites in the role it should have inside PSRO: a response generator, not a static deck-beauty contest. `src/muc5/gameplay_map_elites.py` keeps descriptor cells for deck shape, pilot family, and mulligan family, but cell quality is the current rollout score against the solved opponent support.

The first bounded run targeted the rev0092 admitted response, evaluated 44 nonduplicate candidates, filled 26 cells, and held out the top generated elites on disjoint seeds. The best holdout candidate led in point estimate at 0.5625, but its lower bound did not clear the response threshold. Thus no strategy is promoted, and the useful artifact is the oracle itself: future PSRO rounds can now compare finite-catalog, gameplay-MAP-Elites, neural, and reduced-search response families under shared budgets.

The next method comparison should avoid more passive ranking. It should ask whether a larger generative budget or a first neural response learner can find a confirmed gain that rev0095's bounded MAP-Elites run did not.


## rev0096 result: frozen MLP neural oracle

rev0096 tests the old neural branch in the safest role available: a bounded response oracle against the current effective PSRO support. `src/muc5/neural_oracle.py` combines frozen rev0023 MLP action-ranker pilots with deck sources from the current population, the admitted PSRO response, and the rev0095 gameplay-MAP-Elites archive. `src/muc5/oracle_reporting.py` refactors shared runner evidence plumbing so new oracles do not copy seed-overlap and score-flattening code.

The model audit confirms the dormant MLP artifact is intact: 81 public action features, 32 hidden units, ReLU activation, and the historical 0.9146 top-one imitation accuracy in its training summary. That is only interface evidence. It is not response evidence.

The oracle evaluated 40 nonduplicate candidates, generated 560 balanced game rows, and recorded zero truncations and zero seed overlap. The best holdout candidate scored only 0.1458 against the admitted response, with lower bound 0.0449. No confirmation stage was triggered and no strategy is promoted.

The interpretation is direct: the old frozen imitation MLP is a poor response oracle in the current ecology. Neural methods remain worth doing only when they train or search directly for response value under the repaired information-state/lifecycle contract.


## rev0097 result: rollout-searched learned response oracle

rev0097 makes the next neural/learned step concrete without jumping to a large opaque RL system. It adds a registry-backed linear information-state action scorer, samples and recenters score vectors by direct rollout performance against the current effective PSRO support, and then evaluates final candidates with seed-disjoint holdout.

The result is negative but useful: the best training candidate reached mean 0.875 and the best final selection candidate reached mean 0.750, but the best holdout candidate fell to mean 0.4375 with a 95% interval of roughly [0.2629, 0.6121]. No confirmation stage triggered and no strategy was promoted.

The method lesson is now sharper: learned policies can generate attractive screen wins, so every learned oracle needs explicit selection-to-holdout optimism reporting before any PSRO admission.

## rev0098 result: oracle selection audit before more expansion

rev0098 pauses method proliferation and measures the winner's-curse problem across the response-oracle branches added since the first PSRO expansion. `src/muc5/oracle_selection_audit.py` parses the compact score outputs from the finite-catalog, gameplay-MAP-Elites, frozen-MLP, and learned-response branches, pairs each candidate's best screen row with its holdout row, and records selection-to-holdout optimism.

The audit shows that the learned branch is the most optimism-prone under the current tiny screen budgets. One learned candidate drops from 0.7500 in selection to 0.28125 on holdout, and the branch's best raw screen falls from 0.8750 to a best holdout of 0.4375. MAP-Elites retains the best inherited holdout point estimate, but its lower bound never clears the challenge threshold.

The common-target frontier retest is more decisive: the best holdout challenger from every branch is remeasured against the rev0092 admitted response with 96 games per candidate. No challenger has a lower bound above 0.5; the best challenger mean is 0.4479. This makes the next method step clearer: improve response-oracle sample efficiency and confirmation discipline before admitting another population member.


## rev0099 result: matrix refresh and balanced evaluation spine

rev0099 does not add a fifth oracle branch. It hardens the measurement substrate those branches depend on. The admitted rev0092 response had become the effective PSRO target, but the first expanded matrix was intentionally low resolution. rev0099 rebuilds that nine-strategy matrix at 80 balanced game rows per off-diagonal pair and moves the life/rep/seat/start design into `src/muc5/evaluation_design.py`.

The refreshed matrix still solves to an effectively pure target: `oracle_map_08_60_mixed_threats_counter_wall` receives row mixture weight 0.9996001799 and is the only strategy above 1e-3 effective support. Its refreshed pure floor against the fixed nine-strategy population is 0.5, and it scores at least 0.6625 in mean against each of the eight incumbents.

The method lesson is narrow but important: future PSRO, MAP-Elites, neural, and learned-response runners should use the shared balanced focal-pair design or produce an explicit balance audit. This prevents seat/start completeness from remaining a convention embedded differently in each script.

## rev0100 result: confidence floor audit

rev0100 is a measurement repair for the PSRO method path. It identifies that the rev0099 `pure_floor_vs_population = 0.5` was caused by the matrix self diagonal, not by a real incumbent matchup.

The new confidence-floor runner tests the admitted response against the eight incumbents with 240 balanced game rows per pair. Its weakest incumbent confidence lower bound is `0.6025503087483217`, with zero truncations. The self-control pair is reported separately and remains compatible with 0.5.

Method consequence: the admitted response is a stronger current PSRO target than rev0099's raw floor field suggested. However, because the audit only covers the fixed incumbent ecology, response-oracle work should continue. This result supports deeper attacks; it does not end the search.


## rev0101 result: OOD transfer stress

rev0101 is the first direct transfer stress of the admitted PSRO response outside the original eight-incumbent ecology. The fixed panel combines branch-frontier candidates from rev0094-rev0098 with degenerate threat-density and counter-control/Jace-control decks that were not part of the rev0100 confidence floor.

The admitted response remains ahead in mean against every OOD opponent, but the method conclusion is not dominance. Its weakest OOD pair is `ood_counter_jace40` at mean 0.528125 with CI lower 0.4507726356760219, and one seed remains nonterminal even after a 1,600-decision rescue cap. This says the next method work should generate or solve against counter-control/Jace-control long-game axes, not merely repeat the prior branch-frontier tests.

Method consequence: PSRO remains the outer loop, but the next oracle target should be adversarial counter-control transfer and long-game adjudication. A future admission should not rely on the rev0100 fixed-incumbent confidence floor alone.

## rev0102 result: long-game cap ladder

The OOD transfer audit's weak axis is now instrumented. `src/muc5/longgame.py` records count-only terminal snapshots and replays exact cap cells over a decision-cap ladder without exposing hidden hand or library identities.

The key result is mixed: the admitted PSRO response beats `ood_counter_jace40` at higher resolution in mean and has CI low above 0.5, but the formal confidence floor remains uncleared because at least one deterministic Jace/control game still hits the cap. This is methodologically important because it separates a statistical challenger from a game-semantics/adjudication problem.

Future PSRO oracles should treat persistent cap rows as evidence debt, not silently as proof of either side's strength.
