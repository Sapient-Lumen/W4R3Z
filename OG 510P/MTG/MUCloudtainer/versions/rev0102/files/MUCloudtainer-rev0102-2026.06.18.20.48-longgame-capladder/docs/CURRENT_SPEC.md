# MUCloudtainer current executable specification

**Revision:** rev0097 (`learnedoracle-infostateaudit`)  
**Status:** current normative surface for policy-facing information, episode lifecycle, empirical response-oracle execution, and gameplay-driven generative-oracle evaluation, and learned-response oracle evaluation. `docs/muc5_spec.md` remains historical rules context.

## Scope

This file specifies the boundaries most likely to invalidate learning, recurrent policies, replay, or population expansion. It does not declare a generally optimal strategy.

## Information-state rules

### SPEC-INFO-001: observation versus information state

`GameState.observation(player)` is a compact current snapshot. Legacy memoryless public agents may use it.

`GameState.information_state(player)` is the durable imperfect-information policy boundary. It includes:

- the current observation for `player`;
- ordered public events;
- ordered private events visible only to `player`;
- tracked private knowledge such as known top cards;
- current revision and schema identifiers.

### SPEC-INFO-002: public zone identity

Exile is public in MUC-5. Public snapshots expose both legacy `exile_count` and a card-count `exile` map. Force pitch cards and Jace-ultimate exiled cards are observable through public state/events.

### SPEC-INFO-003: Jace +2 knowledge retention

The acting player privately learns the viewed top card and receives `known_top_cards[target]`.

- `leave`: knowledge persists until the library top changes.
- `bottom`: tracked top-card knowledge clears.
- the public stream records look/order events without revealing card identity to a non-actor.

### SPEC-INFO-004: draw invalidation and recall

Drawing a known top card clears the tracked top slot. The observing player retains a private event that the known card moved into the drawing player's hidden hand; this is not a public reveal.

### SPEC-INFO-005: Brainstorm putback privacy

Jace zero draws and card identities remain private except for public counts. The actor receives private putback recall and knows the new top card of their own library.

### SPEC-INFO-006: replay binding

New public-decision traces record an `information_state_fingerprint` at every decision. Replay verifies it when present. Older traces without the field remain replayable.

## Episode-lifecycle rules

### SPEC-AGENT-001: distinct seat objects

A single mutable policy or mulligan object may not occupy both seats in one game. Models and immutable weights may be shared underneath, but each seat must have a distinct wrapper and recurrent state.

### SPEC-AGENT-002: reset before hidden state exists

Before `start_game` deals or mulligans, every opt-in policy wrapper receives `reset_episode(EpisodeContext)`. The context contains only public metadata: opaque episode ID, seat, starting player, and starting life. It must not reveal shuffle or transition seeds.

A policy that sets `requires_episode_reset = True` but lacks a callable reset method fails closed.

### SPEC-AGENT-003: public terminal callback

After a game, an opt-in wrapper receives `end_episode(EpisodeResult)` containing seat-scoped score, public winner/loss reason, and decision count. No hidden hand or library contents are delivered.

### SPEC-AGENT-004: seat-scoped caching

Bulk evaluators may cache policy wrappers for efficiency only when:

- seat 0 and seat 1 use different objects;
- wrappers are reset every episode;
- cache identity includes the complete strategy signature, not only a human-readable strategy ID or policy name.

### SPEC-AGENT-005: replay recorder parity

The replay recorder applies the same distinct-seat, reset, and terminal-callback contract as ordinary public gameplay. Recording a trace must not bypass lifecycle safety.

## Empirical-game and response-oracle rules

### SPEC-ORACLE-001: constant-sum restricted game

A symmetric empirical population matrix uses draw-half scores, a 0.5 diagonal, and `M[j,i] = 1 - M[i,j]`. Pair evaluation balances both seats, both starting-player roles, configured life totals, and declared repetitions.

### SPEC-ORACLE-002: stage-namespaced deterministic seeds

Restricted-game construction, candidate selection, holdout, confirmation, ablation, and expanded-game construction use deterministic stage-namespaced seeds. Seed intersections between inferential stages must be empty unless a test is explicitly paired by design.

### SPEC-ORACLE-003: support-only and effective-support response evaluation

When estimating value against a solved opponent mixture, strategies with exact zero mixture weight may be omitted. Their contribution to the weighted estimand is exactly zero. The evaluator records the included support, normalized support weights, omitted-opponent count, included mass, omitted mass, and maximum score error from pruning.

Tiny nonzero solver residue may be omitted only when a declared tolerance is recorded and the omitted mass is treated as a hard payoff-error bound. For scores in `[0, 1]`, renormalizing the included support can change any weighted response estimate by at most the omitted normalized mass. rev0094 uses this only to attack the nearly pure rev0092 expanded mixture.

This optimization is not permitted when constructing a full payoff matrix.

### SPEC-ORACLE-004: finite-oracle admission sequence

Candidate selection does not authorize expansion. A response must pass:

1. exploratory selection;
2. seed-disjoint top-k holdout screening;
3. a further seed-disjoint single-candidate confirmation.

The rev0092 confirmation criterion is:

```text
confirmation CI lower bound
    > restricted best-response upper value + declared minimum gain
and zero truncations
and not an existing strategy duplicate
```

### SPEC-ORACLE-005: exploratory expansion is not promotion

A confirmed response may be added to the empirical PSRO population so the game can be re-solved. This does not establish general strategic superiority, transfer, mechanism, or a user-facing recommendation.

### SPEC-ORACLE-006: mechanism attribution requires ablation

When candidate deck, mulligan, and pilot all change, performance cannot be attributed to one component without a controlled comparison. Paired same-seed ablations should hold all other components fixed.

### SPEC-ORACLE-007: gameplay-driven generative MAP-Elites is an oracle, not a claim gate

A MAP-Elites cell may be retained by actual rollout score against a declared opponent mixture. The runner must serialize the descriptor cell, candidate source, generation, rollout configuration, seed namespace, truncations, and duplicate-signature status. Static construction quality may seed proposals, but it must not be copied forward as matchup evidence.

Generated candidates require seed-disjoint holdout and, when a holdout pass exists, seed-disjoint confirmation before PSRO population expansion. A point-estimate lead from a generated cell is not a strategic promotion.


### SPEC-ORACLE-008: frozen learned-policy oracles are negative controls unless trained for the target

A frozen historical learned policy may be evaluated as a response oracle only when the runner records the model artifact, feature count, candidate source, duplicate-signature status, target support, seed namespaces, truncations, and nonpromotion scope. Historical imitation accuracy is interface evidence, not response evidence.

A frozen learned-policy failure should not be generalized to all neural methods. A future neural response learner must document its information-state encoding, episode reset behavior, training seed namespace, evaluation seed namespace, and admission threshold.


### SPEC-ORACLE-009: learned response-oracle training is not response confirmation

A learned policy trained, sampled, or searched against a solved opponent mixture must serialize its model/agent registry, feature names, training seed namespace, evaluation seed namespace, candidate catalog, duplicate-signature status, truncations, and selection-to-holdout outcome. Training and selection performance are screening evidence only. A learned candidate may enter confirmation only after seed-disjoint holdout clears the declared response threshold.

A learned oracle must use the ordinary public-agent factory and episode lifecycle. Loading a learned registry-backed policy must not bypass `DecisionFrame.information_state`, seat-specific reset, or terminal callbacks.


### SPEC-ORACLE-010: selection optimism is evidence debt

Every response-oracle family with a screen and holdout stage must report candidate-level selection-to-holdout optimism before a candidate can enter confirmation. The report must identify the best screen candidate, whether that candidate was held out, the best holdout candidate, the largest within-candidate optimism gap, and whether any holdout lower bound clears the declared challenge threshold.

When several oracle families target the same effective opponent support, their branch winners should be eligible for a common-target retest before further population admission. A common-target retest is still not a strategic promotion; it is a bias and stability guard.


### SPEC-ORACLE-011: balanced focal-pair design is shared infrastructure

Empirical focal-pair estimates must be auditable as configured life totals × repetitions × both physical orientations × both starting-player roles. Runners should use the shared `balanced_pair_cells()` design helper or serialize enough row metadata for `audit_balanced_focal_rows()` to verify completeness.

A full empirical matrix may enforce constant-sum antisymmetry by setting `M[j,i] = 1 - M[i,j]`, but the underlying rows must still record seat/start design integrity before the matrix is solved. Diagonal cells remain 0.5 unless a runner explicitly states that self-play sampling is diagnostic rather than matrix construction.



### SPEC-ORACLE-013: fixed-population confidence is not transfer confidence

A confidence floor against a fixed incumbent population must not be generalized to out-of-distribution opponents without a separate transfer stress. Transfer panels should serialize opponent families, deck/pilot/mulligan signatures, duplicate checks against the old population and focal target, balanced life/seat/start rows, self-control diagnostics, and seed separation.

If an OOD pair produces a nonterminal cap hit, the runner must record it as evidence debt rather than silently treating it as a clean draw. A rescue attempt may show whether the cap was operational, but persistent rescue truncation should become a named future attack axis.

rev0101 applies this rule to the admitted PSRO response. It reports mean-positive OOD performance but leaves transfer confidence open because the weakest lower bound is below 0.5 and the weakest counter-control/Jace axis has a persistent truncation.

## Reduced equilibrium-calibration rules

### SPEC-CFR-001: reduced games must be independently projected

A reduced CFR/search game is a calibration artifact, not a clone of the full simulator. It must state which MUC mechanisms it preserves and which it omits. rev0093 preserves Jace private top-card knowledge, public leave/bottom order, Force pitch visibility, and closure pressure.

### SPEC-CFR-002: best response may not peek through information sets

Exploitability must be measured by selecting one shared action per responding-player information set. A concrete-state shortcut that maximizes separately for hidden top-card or hand states is invalid.

### SPEC-CFR-003: reduced CFR is not strategic promotion

A converged reduced-game policy is a method calibration result. It may suggest empirical PSRO probes, but it does not promote a full-game deck or policy without simulator evaluation, seed-disjoint confirmation, and mechanism attribution.

## Required regression evidence

The package must execute tests for:

- Jace +2 leave retention and bottom clearing;
- public Force pitch identity;
- information-state replay fingerprint tamper detection;
- identical observations producing different actions when information states differ;
- stateful wrapper reset and public terminal callbacks;
- rejection of one policy object shared across seats;
- seat-scoped self-play payoff caching;
- replay lifecycle parity;
- constant-sum empirical-game construction;
- exact-zero and tiny-residue mixture opponents being skipped only with audited support and error-bound metadata;
- gameplay-driven MAP-Elites descriptors, archive replacement, and duplicate-signature rejection;
- frozen MLP neural-oracle model audit, candidate bounding, duplicate rejection, and shared oracle-reporting seed-overlap checks;
- learned-response registry shape, information-state feature activation, candidate duplicate rejection, and seed-disjoint training/selection/holdout audit;
- cross-oracle selection-to-holdout optimism audit and common-target frontier retest;
- balanced focal-pair design coverage, malformed-row detection, and expanded-matrix constant-sum checks;
- OOD transfer-stress panel uniqueness, family metadata, balanced rows, self-control separation, and truncation-rescue accounting;
- strategy-cache identity distinguishing changed policies under recycled IDs;
- reduced CFR information projection preserving Jace privacy and Force pitch visibility;
- reduced CFR exploitability measured with grouped information-set best response.

## Current non-goals

- rev0092 does not prove that the hand-written information-state policy is strategically better.
- rev0093 does not implement a generational evolutionary oracle, neural best-response training, full-game CFR, or Deep CFR.
- rev0092 does not promote the confirmed finite-oracle response as a general answer.
- rev0093 does not claim the reduced CFR game is a full MUC-5 solution.
- rev0094 does not promote the admitted PSRO response; it stress-tests it and records that no second static-catalog response cleared holdout.
- rev0095 does not promote a generated MAP-Elites challenger; its best holdout point estimate fails the response threshold.
- rev0096 does not revive the old MLP as a strong policy; it records that frozen historical imitation is a poor current response oracle and promotes no strategy.
- rev0097 does not promote a learned response; it records a direct learned-score-vector screen that overfits training/selection and fails seed-disjoint holdout.
- rev0098 does not admit another PSRO population member; it records selection-bias evidence and a common-target retest in which no challenger clears 0.5 by confidence lower bound.
- rev0099 does not promote the admitted response; it refreshes the fixed-population matrix and factors out balanced evaluation design.
- rev0100 does not promote the admitted response; it clears a fixed-incumbent confidence floor only.
- rev0101 does not promote the admitted response; it records that OOD transfer confidence remains open, especially on counter-control/Jace-control long-game axes.

### SPEC-ORACLE-012: matrix self diagonal is not opponent-floor evidence

When a symmetric empirical matrix uses a 0.5 diagonal for self-play or constant-sum solving, that diagonal must not be reported as the floor against challengers without explicit labeling. Runners that report a pure floor should distinguish:

1. floor including self diagonal;
2. floor excluding self diagonal;
3. weakest non-self opponent by mean;
4. weakest non-self opponent by confidence lower bound;
5. any separate self-control diagnostic.

A confidence floor against a fixed population is scoped evidence only. It may strengthen a current PSRO target, but it is not a general strategic promotion unless the relevant response-oracle, holdout, confirmation, and mechanism-attribution gates are also satisfied.

### SPEC-ORACLE-014 — Long-game cap rows are not heuristic wins

A game stopped by `max_decisions_reached` remains scored as `0.5` unless a future revision explicitly changes the MUC-5 rules. Count-only terminal snapshots and diagnostic advantage scores may be used to classify cap debt, but they must not replace terminal payoff in PSRO, confidence-floor, or oracle-admission evidence.

Any long-game audit must state whether it resolved the original cap row, whether hidden hand/library identities are exposed in exported evidence, and whether remaining cap rows block the claimed confidence floor.
