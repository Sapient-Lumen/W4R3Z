# Candidate-native identifiability promotion-readiness matrix

This document applies the route-level promotion gate to the current live landscape.
It does **not** add a new witness level, add a field protocol, reopen the followthrough queue, or promote any lane.
It is the compact answer to a different question:

> after the eight-field ledger and no-compensation gate are installed, which rows are actually near promotion, and what is the first blocker that still caps them?

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-identifiability-promotion-gate.md`
- `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md`
- `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`
- `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md`
- `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md`
- `docs/40-model/candidate-native-identifiability-decision-trace-docket.md`
- `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-response-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md`
- `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`
- `docs/40-model/candidate-native-equivalence-collapse-protocol.md`
- `docs/40-model/candidate-native-acquisition-realizability-protocol.md`
- `docs/40-model/candidate-native-inverse-completeness-stability-protocol.md`
- `docs/40-model/candidate-native-abstention-no-verdict-protocol.md`
- `docs/40-model/candidate-native-public-bridge-challenge-protocol.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The archive now has seven distinct controls for `OQ-0057`:

1. **field inventory** — the route template and route ledger say what fields exist and how current rows score field by field;
2. **field discipline** — the equivalence, acquisition, inverse/stability, abstention, and public-bridge protocols say what would count as a real field upgrade;
3. **route promotion discipline** — the promotion gate says field strengths do not average into closure;
4. **evidence-intake discipline** — the evidence-intake docket says new artifacts do not update this matrix unless they change a field, coupled-field dependency, route state, readiness class, or dominant blocker rather than repeating saturated same-package credit;
5. **supersession / decay discipline** — the supersession docket says prior credit must be retained, narrowed, replaced, demoted, quarantined, or retired rather than silently carried forward when its support changes;
6. **dependency-propagation discipline** — the dependency docket says a changed field, route cell, public bridge, or witness-package handoff does not change readiness until dependent upstream and downstream cells have been recomputed or explicitly held unchanged.
7. **adversarial-control discipline** — the adversarial-control battery says positive route success cannot be spent as `S4`/`S5` credit until hostile decoys, spoofing, prior-leakage, margin, abstention, public-bridge, and witness-borrowing controls are declared and survived.

The missing operational layer before this matrix was a **readiness table**.
Without it, a future revision could still ask the right field questions and then misread the live landscape: it could treat the strongest formal target row, the strongest laboratory record row, or the strongest family-C partial route as if it were the closest full closure candidate for the same reason.
They are not the same shape of near-miss.

The current readiness verdict is:

**no live lane is an `S4` candidate-native identifiability candidate or an `S5` closure row; family C is the strongest bounded `S3` partial-identification family; most completion bids are target-rich `S1`/`S2` rows; laboratory and simulation lanes are record-rich `S2` rows that can become `S3` only for named discriminator classes, not for broad candidate-native target spaces.**

## State key

Use the promotion states from `docs/40-model/candidate-native-identifiability-promotion-gate.md`:

| State | Short use in this matrix |
|---|---|
| `S0` | no candidate target / record route |
| `S1` | route sketch |
| `S2` | field-local improvement |
| `S3` | partial-identification route with explicit residual debt |
| `S4` | candidate-native identifiability candidate for a bounded regime |
| `S5` | candidate-native identifiability closure for the claimed target class |

This matrix allows mixed state labels only when the row genuinely splits by regime.
For example, a laboratory route can be `S3` for a named two-alternative discriminator but only `S2` for broad completion-bid identifiability.
Mixed labels are not promotion language; they are scope warnings.

## Current promotion-readiness matrix

| Row | Current route state | Earliest dominant blocker | Current strength | What would actually move it | Overclaim blocked |
|---|---|---|---|---|---|
| Family C — entanglement wedge / code-subspace reconstruction | bounded `S3` | equivalence quotient and public bridge remain package-bound | strongest partial inverse-interface row; real restricted reconstruction and overlap structure | a candidate-native same/different rule plus public bridge that survives beyond the fixed boundary / code-subspace package | treating bounded reconstruction as identified bulk ontology |
| Family C — sparse, learned, or route-specific inverse reconstruction | `S2`, sometimes bounded `S3` for a named surrogate target | acquisition and inverse/stability coupling | strongest method-diverse route-improvement row | acquired records plus declared deficiency map, robustness transport, no-inversion zone, and challengeable public audit handle | treating fit, regularization, or benchmark performance as stable identification |
| Family B — thermodynamic / entropic equation recovery | `S1`/`S2` | target / record entry | genuine equation-recovery and trace-discipline clue | a candidate-native record carrier and non-equilibrium acquisition route whose inverse says what target quotient is learnable | retelling thermodynamic repair vocabulary as witness ownership |
| String / M-theory and strongest holographic / collapse corridors | `S1`/`S2` | record class and acquisition path | richest target menu and strongest completion-bid corridor set | finite public acquisition route from native target quotient to observed-sector records, with abstention and public challenge behavior | treating formal target richness or special-package success as acquired identifiability |
| Asymptotic safety and conservative fixed-point extraction | `S1`/`S2` | equivalence quotient and acquisition path | serious UV fixed-point / predictive-extraction discipline | gauge-, scheme-, and truncation-aware target quotient tied to observable extraction and finite-record inverse margins | treating fixed-point seriousness or stable coefficients as identified UV ontology |
| Loop / canonical and spin-foam continuum routes | `S1`/`S2` | record class and inverse completeness | real background-independence and continuum-limit pressure | public record route that separates semiclassical recovery from topological-collapse or rigging-map ambiguity, with a no-verdict rule | treating formal continuum control as observed semiclassical identification |
| Causal-set / discrete-growth routes | `S1`/`S2` | acquisition path and inverse completeness | real causal-order / discreteness pressure | native quantum-growth records that can be publicly acquired and inverted without classicalized order-selection overclaim | treating causal-order minimalism as enough dynamics or witness evidence |
| Bootstrap, amplitudes, positive geometry, and selection tools | `S2` for tool-local selection; below `S3` for ontology | target / record ownership | sharp consistency and selection pressure inside formal packages | handoff from consistency space to a candidate target, acquired record class, equivalence rule, and public inverse route | treating elegant or discrete selection as standalone ontology |
| Low-energy gravity lab and semiclassical simulation routes | `S2`; bounded `S3` only for named discriminator classes | candidate target class | strongest acquired-record and public-challenge fragments | candidate-native target quotient plus inverse-completeness claim showing which theory distinctions, not merely alternatives, the records identify | treating record richness or null-result discipline as broad candidate-native identifiability |
| Witness-side frame, asymptotic-access, and de Sitter observer routes | `S2` | public bridge and cross-frame equivalence | real frame/access/observer discipline | same-fact transport across frames plus public custody, replay, challenge, and terminal-state rules | treating special access maps as public reference-standard closure |
| Vacuum-energy and cosmological proposal classes | `S1`/`S2` when they name target relief; otherwise `S0` for identifiability | target / record entry and witness package split | useful burden accounting and proposal-class braking | local record-bearing route that distinguishes local-law credit, cosmological-package credit, and witness-package credit without selection-package borrowing | treating global selection or burden reshuffling as candidate-native identification |

## Readiness classes

### 1. Strongest partial route: family C

Family C is closest only in the narrow sense that it already has partial target, record, inverse, stability, overlap, calibration, abstention, policy, and public-bridge fragments.
That breadth earns bounded `S3` treatment where the target and regime are explicitly named.
It does not earn `S4`, because the route still depends on fixed packages for equivalence, acquisition, public bridge, and witness ownership.

Promotion pressure for family C should therefore ask:
- which exact field changed;
- whether the change survives outside the borrowed boundary / code-subspace / simulation package;
- whether the route now has a public bridge that outsiders can possess, replay, and challenge;
- and whether witness-package debt is still separate after any identifiability improvement.

### 2. Target-rich but record-poor rows: completion bids

String / M-theory, asymptotic safety, loop / canonical programs, causal-set programs, and related completion bids are often target-rich.
They can name candidate structures, formal corridors, fixed points, histories, amplitudes, constraints, or discrete growth rules.
That does not by itself identify anything from public records.

Their first promotion-relevant move is usually not another target refinement.
It is a public acquisition and inverse route from native target quotient to acquired record class, plus the no-verdict and challenge behavior that says when the route fails.

### 3. Record-rich but target-poor rows: laboratories and simulations

Low-energy gravity laboratories, semiclassical simulations, local-operator constructions, and public replay tools can be record-rich.
They can have better acquisition, custody, challenge, and no-verdict practice than many completion bids.
That does not by itself make them broad candidate-native identifiability routes.

Their first promotion-relevant move is usually not more publicness.
It is a native target quotient and inverse-completeness claim that says which candidate distinction the records identify rather than which external alternative they discriminate.

### 4. Access-rich but bridge-limited rows: frame and observer lanes

Frame-conditioned, asymptotic, de Sitter, edge, observer, and relational routes expose something important: many apparent facts are access- and frame-conditioned.
That is discipline, not closure.

Their first promotion-relevant move is a same-fact transport and public-bridge rule: which frame-relative records can be made into stable public objects, which apparent disagreements collapse, and which remain no-verdict states.

### 5. Burden-accounting rows: vacuum and cosmological packages

Vacuum-energy and cosmological proposal classes often reduce or rearrange burdens.
That work belongs in the broad ToE credit split unless it supplies a candidate-native target-to-record route.

Their promotion-relevant move is not another selection or relaxation story by itself.
It is a local record-bearing route that keeps local-law, cosmological-package, and witness-package credit separate.

## Update rule

Do not update this matrix merely because a row sounds more promising.
A future revision should update it only after doing the following:

1. update the route ledger field that actually changed;
2. apply the relevant field protocol if the change is in equivalence, acquisition, inverse/stability, abstention, or public bridge;
3. apply the promotion gate to decide whether the row state changed or only a field-local cell improved;
4. name the earliest remaining dominant blocker;
5. say whether the row stays in its readiness class or moves to another class;
6. keep the followthrough queue empty unless the change exposes a genuinely earned next proof point rather than a nice-to-have wish.

If several rows appear to improve at once, report whether the improvement is shared method credit, shared record credit, shared public-bridge credit, or actual transfer of candidate-native identifiability structure.
Do not treat generic tooling uplift as route promotion.
For new papers, simulations, experiments, code releases, or formal results, run `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md` before changing this matrix; `E0`/`E1` results leave this matrix unchanged, `E2` results normally update only a field cell, `E3` results trigger the promotion gate, and only `E4` or higher changes this readiness readout.

## Dependency-propagation note

A readiness row should not change merely because a local field improved or old credit was rescored. Use `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md` after evidence intake and supersession / decay review to decide whether upstream target / record assumptions, downstream inverse / stability / abstention / public-bridge fields, cross-lane leakage checks, or witness-package handoffs force a real readiness recomputation. If the propagation stops at `G0`, `G1`, `G2`, or `G3` without changing the earliest blocker, this matrix should not move.
If propagation returns conflict / quarantine or leaves competing rows unresolved, use `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md` before changing readiness class; the matrix cannot choose the favorable side of an unresolved conflict.

## Net result

The promotion gate now has a concrete landscape readout.
The archive can answer not only **what fields are missing**, but **which kind of row is missing which kind of thing first**.

Current ranked posture:

1. family C remains the strongest bounded partial-identification route;
2. laboratory and simulation lanes remain the strongest acquisition / public-record fragments;
3. completion bids remain the strongest target-rich formal rows;
4. frame and observer lanes remain the strongest access-discipline rows;
5. cosmological proposal classes remain burden-accounting rows unless they produce local record-bearing identifiability routes.

No row reaches `S4` or `S5`.
No claim of public witness closure, public reference-standard closure, or candidate-native identifiability closure is newly earned.


## Supersession discipline

A readiness class is not permanent credit.
When a new artifact, reanalysis, contradiction, source refresh, public-carrier failure, or protocol upgrade touches the basis of a row in this matrix, first classify the new artifact through `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md`, then re-audit the old credit through `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`.

The matrix changes only if the supersession row changes the route state, earliest dominant blocker, or readiness class.
Otherwise the result remains citation refresh, local narrowing, field-cell update, or historical-anchor cleanup.

Challenge-response control: a readiness row that survives replay is still not durable against a route-bearing objection until `docs/40-model/candidate-native-identifiability-challenge-response-docket.md` classifies the challenge and states whether the row remains, narrows, freezes, retags, separates, or rolls back.

Challenge-closure control: after a challenge is classified and answered, use `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md` before reusing the challenged credit. Closure must state whether the case is duplicate-closed, retagged, retained, narrowed, frozen, public-bridge-reconditioned, witness-separated, or still closure-barred.

Adversarial-control battery: before any future `S4`/`S5` promotion attempt, high-state reuse, or route-bearing challenge spends positive route success as candidate-native identifiability credit, use `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`. Hostile target decoys, equivalence relabelings, acquisition-spoof checks, prior-leakage checks, margin perturbations, abstention hard negatives, public-bridge fragility checks, and witness-borrowing substitution controls must be declared; missing, damaging, conditional, or unreplayable controls narrow, freeze, retag, witness-separate, or bar promotion rather than becoming vague caveats.

Calibration-anchor docket: before any future route score, readiness state, adversarial-control pass, or high-state support is compared across lanes or reused as broad `OQ-0057` posture, use `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`. Target grain, record denominator, route width, control difficulty, publicness, and witness-owner boundaries must be normalized or explicitly marked non-comparable; uncalibrated score labels freeze rather than ranking unlike rows on one ladder.

Residual-cap ledger: after calibration, any bounded, conditional, non-comparable, weaker-control, borrowed-public, mixed-record, or witness-separated score that is reused outside its owner row must use `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md` so the bounded label, owner boundary, and earliest remaining blocker travel with the score rather than evaporating in broad mirrors.

## Export-claim control

Readiness classes are easy to over-export. The safe current capsule is: family C is the strongest bounded package-grain `S3` partial-identification row; completion bids are target-rich `S1`/`S2`; lab / simulation rows are record-richer `S2` with named discriminator-class `S3` pockets; no live row reaches `S4` or `S5`. Any shorter release, restart, or external summary should pass through `docs/40-model/candidate-native-identifiability-export-claim-docket.md`.

## Reimport firewall handoff

If this surface is later cited through a release note, restart capsule, generated index, user-facing answer, abstract, handoff note, or external paraphrase, that derivative wording is only a pointer. Before it supports `OQ-0057` posture, route state, readiness, calibration, residual-cap transfer, publicness, witness credit, or promotion pressure, use `docs/40-model/candidate-native-identifiability-reimport-firewall.md` to reanchor the claim to canonical owner rows, preserve caps and freshness, and split echo from genuinely new content.

## Lineage-merge handoff

If this surface returns through an older release, fork, cherry-picked document, generated archive artifact, or externally edited bundle, do not merge its route state directly. Use `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md` to identify the source lineage, rebase touched owner rows through the current `OQ-0057` stack, split stale branch posture from genuinely new evidence or challenge content, and preserve the most restrictive surviving cap.

## Release-seal note

Bundle-level reuse of this `OQ-0057` posture is downstream of `docs/40-model/candidate-native-identifiability-release-seal-docket.md`, `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`, `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`, and `docs/40-model/candidate-native-identifiability-head-succession-docket.md`: packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, and context posture are carriers and pointers, not surrogate route evidence, and their identity, owner-chain, cap, mirror, package-boundary, lineage, challenge, rollback, current-head authority, and successor-transition status must verify, adopt, and succeed before reuse as current posture.


## Current-authority ledger handoff

If this surface is reused to state current `OQ-0057` posture after adoption, succession, branch arbitration, retirement / vacancy, or reinstatement / thaw, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare one scoped authority object, source custody row, owner rows, exclusions, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
