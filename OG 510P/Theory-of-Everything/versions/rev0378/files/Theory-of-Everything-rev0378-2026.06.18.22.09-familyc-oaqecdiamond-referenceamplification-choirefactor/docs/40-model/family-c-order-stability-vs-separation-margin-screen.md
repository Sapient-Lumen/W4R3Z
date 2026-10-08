# Family-C order stability versus separation margin screen

This document sits inside `docs/40-model/family-c-identifiability-stack.md`, the archive's canonical ordered router for the family-C partial-identification / inflation-screen chain.
It keeps one specific inflation move in focus:
**a route producing a bulk ordering or same/different verdict that remains stable across a reasonable policy family and source ecology, and that verdict then being retold as discriminator-grade candidate-native identification.**
Score that gain at this stage, then route broader family-C credit through the stack rather than promoting directly to candidate-native identifiability closure.

Read this together with:
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/family-c-policy-choice-vs-candidate-order-stability-screen.md`
- `docs/40-model/family-c-selective-safety-vs-discriminator-coverage-screen.md`
- `docs/40-model/family-c-abstention-competence-vs-soft-confidence-screen.md`
- `docs/40-model/family-c-point-estimate-vs-calibrated-solution-bundle-screen.md`
- `docs/40-model/family-c-overlap-class-screen.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`
- `docs/40-model/family-c-witness-closure-gate.md`

## Compression verdict

The archive should now preserve six compact points at once:
- family C is now strong enough that **policy-stable ordering must also be scored for separation margin**, because a route can keep the same preferred bulk across nearby policies while still leaving the nearest rivals inside a flat ambiguity band; `REF-0156`, `REF-0158`
- recent ranked-abstention work makes the first warning explicit: confidence-based abstention improves ranked decisions monotonically only when rank alignment and no-inversion zones actually hold, so safer retained decisions do not by themselves certify a stable ordering margin; `REF-0156`
- recent full-ranking conformal work makes the second warning explicit: valid rank prediction sets can remain materially wide even after efficiency improvements, so “top candidate preserved” is weaker than a non-overlapping rank interval or declared separation certificate; `REF-0158`
- recent epistemic-uncertainty work makes the third warning explicit: the same conformal prediction region can hide very different levels of model multiplicity, so apparent rank stability can still sit on a thick layer of unresolved predictive ambiguity; `REF-0157`
- recent selective pairwise-judging work makes the fourth warning explicit: accepted same/different judgments become more trustworthy only after the uncertainty signal is made order-invariant and selectively risk-controlled, so one pairwise verdict is weaker than a margin that survives presentation and tie handling; `REF-0159`
- the archive should therefore award family C a new screen: **a candidate ordering or same/different verdict earns stronger credit only if it is backed by a declared separation margin or no-inversion certificate that keeps the leading bulk distinct from nearby rivals, rather than merely staying nominally on top across one still-flat ambiguity band.** `REF-0156`, `REF-0157`, `REF-0158`, `REF-0159`

## Why this document exists

The archive already distinguishes:
- restricted inverse success from identifiability closure,
- route breadth from common-target convergence,
- thin-data recovery from acquirable witness closure,
- conditioned robustness from portable inverse stability,
- surrogate recovery from candidate-native target recovery,
- point estimates from calibrated bundles,
- soft confidence from real abstention competence,
- safer selective answering from retained discriminator-bearing hard-case coverage,
- and one calibrated policy package from policy-stable candidate ordering.

What it still lacked was one short rule for the next inflation move:

> this route preserves its bulk order across nearby policies and source ecologies, therefore its top candidate is now cleanly separated and closer to candidate-native identifiability.

That step is still too fast.
A route can preserve the same winner while the nearest alternative remains effectively tied inside the uncertainty object actually returned by the route.
Small changes in calibration rank, abstention gate, pairwise presentation, or local score geometry can still flip the second-versus-first relation exactly where the candidate-level discriminator would have to live.
If the winner survives only because every nearby policy defers the fragile cases or because the rank interval remains wide, the archive has learned that the route is not reckless.
It has not yet learned that the route separates candidate bulks with an honest margin.

The archive therefore needs one explicit distinction between:
- a route that yields the same preferred bulk under a declared family of policies,
- a route that additionally certifies a non-flat separation zone around that winner,
- and a route that can preserve that separation when pairwise presentation, calibration rank, and local ambiguity structure are perturbed nearby.

## The five checks the archive should now require

### 1. Policy-stable order is weaker than margin-certified order

A route may keep the same preferred bulk under several reasonable action packages while still having almost no daylight between the winner and the nearest rival.
The archive should therefore require every family-C route that claims stronger identification to declare the **separation object** it is using: rank interval, score gap, pairwise margin, no-inversion zone, or another explicit tie-handling certificate.

### 2. Rank validity is weaker than non-overlapping rank support

Liao et al. matter here because the paper makes the ranking lesson exact: conformal ranking can be valid while the admissible absolute-rank set remains materially wide, and efficiency gains matter precisely because wide rank sets are too weak for downstream ranking claims. `REF-0158`

That is exactly the archive issue.
A family-C route may keep one preferred bulk on top while the acceptable rank support for that bulk still overlaps substantially with the support for nearby rivals.
So the archive should now require a **declared non-overlap or margin condition**, not only a valid ranking object.

### 3. Selective safety is weaker than a no-inversion zone

Doku matters because the paper states the ranked-decision warning plainly: confidence-based abstention improves ranked decisions cleanly only when rank alignment and no-inversion zones hold. `REF-0156`

That is exactly the next family-C lesson.
A route may abstain responsibly and preserve a top candidate on the retained set while still lacking any guarantee that the retained ordering will not invert near the candidate-separating frontier.
The archive should therefore ask whether the route has a **no-inversion certificate** near the cases that matter for discriminating candidate bulks.

### 4. One prediction region is weaker than low model multiplicity

Chau et al. matter because they show that two instances can share the same conformal prediction region while differing sharply in epistemic predictive uncertainty, since multiple plausible predictive models may remain compatible with the data. `REF-0157`

That is exactly why “same winner, same set size” is not yet enough here.
A family-C route can look order-stable while still carrying thick hidden multiplicity under the predictive surface.
So the archive should now require a **multiplicity-sensitive ambiguity readout**, not only the visible prediction-set or rank-set object.

### 5. Accepted pairwise verdicts are weaker than tie-robust pairwise margins

Badshah et al. matter because they make the pairwise lesson concrete: selective same/different judging improves only after the uncertainty signal is made invariant to presentation order and the acceptance threshold is calibrated to bound error on the retained judgments. `REF-0159`

That is exactly the archive analogue.
If a family-C same/different verdict depends on one candidate being presented first, one score convention, or one tie-breaking habit, then the archive has not yet earned discriminator-grade pairwise separation.
It has one retained pairwise verdict.

## False promotions the archive should reject

1. **one stable winner is not yet a separated winner**
   - The same top bulk can survive nearby policies while still remaining effectively tied with the nearest rival.

2. **valid rank sets are not yet discriminator-grade rank margins**
   - Coverage-valid ranking output can still leave the admissible rank support materially overlapping.

3. **responsible abstention is not yet a no-inversion certificate**
   - A route can get safer by abstaining while still lacking local order robustness where the candidate decision matters.

4. **one visible uncertainty object is not yet low hidden model multiplicity**
   - The same returned set or interval can mask very different levels of epistemic ambiguity.

5. **accepted pairwise judgments are not yet pairwise separation margins**
   - A retained same/different verdict can still depend on presentation order or fragile tie handling.

6. **margin-certified ordering is not yet candidate-native identifiability closure**
   - Even a real separation margin can still borrow gauge, map, recoverand, witness, and acquisition structure.

## What would change archive state

A future family-C lane should earn stronger identifiability credit only if it adds, in one compact route:
1. a declared separation object for bulk ordering or same/different verdicts,
2. a non-overlap or no-inversion certificate around the candidate-separating frontier,
3. ambiguity reporting that distinguishes visible rank-set width from hidden model multiplicity,
4. pairwise presentation or tie-handling robustness where the route uses pairwise judgments,
5. evidence that discriminator-bearing hard cases remain inside the margin-certified region rather than only inside a retained easy subset,
6. and, ideally, one compact result showing that the same separated order survives nearby calibration and presentation perturbations without collapsing into a tie or inversion band.

Until then, family C has improved ordering discipline, not yet discriminator-grade candidate separation.

## Net result

Family C is now bounded one step more tightly:
1. **policy discipline** — one calibrated action package is weaker than policy-stable ordering,
2. **margin discipline** — policy-stable ordering is weaker than a declared separation margin or no-inversion certificate,
3. **closure discipline** — even separated ordering is still weaker than candidate-native identifiability closure.

That keeps the archive sharper without widening it.
