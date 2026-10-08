# Family-C selective safety versus discriminator coverage screen

This document sits inside `docs/40-model/family-c-identifiability-stack.md`, the archive's canonical ordered router for the family-C partial-identification / inflation-screen chain.
It keeps one specific inflation move in focus:
**an inverse route becoming safer only by abstaining on the very cases that would actually separate bulk candidates.**
Score that gain at this stage, then route broader family-C credit through the stack rather than promoting directly to candidate-native identifiability closure.

Read this together with:
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/family-c-abstention-competence-vs-soft-confidence-screen.md`
- `docs/40-model/family-c-point-estimate-vs-calibrated-solution-bundle-screen.md`
- `docs/40-model/family-c-thin-data-vs-acquirable-witness-screen.md`
- `docs/40-model/family-c-overlap-class-screen.md`
- `docs/40-model/family-c-recoverand-vs-surrogate-screen.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`
- `docs/40-model/family-c-witness-closure-gate.md`

## Compression verdict

The archive should now preserve six compact points at once:
- family C is strong enough that **abstention competence must now be scored together with retained discriminator coverage**, because safer behavior can be purchased by discarding the very regime where candidate-level same/different pressure lives; `REF-0147`, `REF-0148`, `REF-0149`
- recent selective conformal work makes the trade explicit: one can jointly control accepted-sample coverage and conditional risk while abstaining on uncertain cases, so higher reliability may simply reflect **selection** rather than deeper identification; `REF-0151`
- recent selective-classification work sharpens the next warning: under **covariate shift**, which is the realistic setting for scientific deployment, the abstention rule itself can move materially and needs its own robustness discipline; `REF-0152`
- recent inverse-problem work makes the scientific point directly: predictive performance alone does not settle physically meaningful or uniquely identified solutions, and extra geometric constraints can be what actually closes uniqueness; `REF-0150`
- so family C now needs one more check beyond calibrated bundles and abstention semantics: **which regime is still covered after abstention, and does that retained coverage still contain the candidate-separating hard cases?** `REF-0147`, `REF-0150`, `REF-0151`, `REF-0152`
- the archive should therefore award family C a new screen: **selective safety earns credit only if the route preserves a declared coverage floor on discriminator-bearing regimes, rather than improving risk merely by ejecting them from the answered set.** `REF-0147`, `REF-0148`, `REF-0150`, `REF-0151`, `REF-0152`

## Why this document exists

The archive already distinguishes:
- restricted inverse success from identifiability closure,
- route breadth from common-target convergence,
- thin-data recovery from acquirable witness closure,
- conditioned robustness from portable inverse stability,
- surrogate recovery from candidate-native target recovery,
- point estimates from calibrated bundles,
- and soft confidence from real abstention competence.

What it still lacked was one short rule for the next inflation move:

> this route now abstains or controls selective risk, therefore it is closer to candidate-native identifiability.

That step is still too fast.
A route can become **safer on answered cases** while also becoming **less informative about the candidate-level hard cases**.
If the abstention policy systematically drops the boundary packages, observer-map cases, finite-`N` regions, or noisy / thin-data situations where rival bulk stories actually separate, then the route may improve its dashboard metrics while losing the very evidence mass the archive cares about.

The archive therefore needs one explicit distinction between:
- a route that lowers answered-case risk by declining hard inputs,
- a route that preserves a declared **coverage floor** over the cases that matter for candidate separation,
- and a route that can additionally reacquire or redesign the missing witness path rather than simply routing the hard cases into permanent silence.

## The five checks the archive should now require

### 1. Selective safety is weaker than discriminator retention

Selective prediction can improve reliability by refusing uncertain cases.
That is often good.
But if the refused cases are precisely the ones where candidate bulk stories differ, then the route has become safer without becoming more identificatory.
The archive should therefore require every family-C abstention-capable route to name the **discriminator-bearing regime class** it still claims to cover.

### 2. Accepted-sample guarantees are weaker than hard-case coverage floors

Xu, Guo, and Wei are useful here because they make selective uncertainty control operationally precise.
Their Selective Conformal Risk Control framework calibrates which examples are accepted, applies conformal risk control on the accepted subset, and explicitly optimizes the tradeoff among coverage, conditional risk, and informative set size while preventing trivial solutions such as always predicting or always returning huge sets. `REF-0151`

That is exactly why the archive needs the next screen.
A route may satisfy accepted-sample guarantees and still give up the cases that matter most for candidate-level same/different rules.
So the archive should now require a **hard-case coverage floor**, not only a global accepted-sample guarantee.

### 3. Coverage under one ecology is weaker than shift-robust selective behavior

Heng and Soh matter because they push selective classification into the covariate-shift setting and treat that setting as realistic rather than exceptional. Their result is not a family-C solution, but it sharpens the archive's warning: an abstention rule that looked prudent on one data ecology may move significantly once the test distribution shifts. `REF-0152`

Family C now needs that same discipline.
If the route only retains discriminator-bearing coverage inside one training / calibration package, one cutoff family, or one observer-map ecology, then it has not yet shown that its abstention policy preserves the hard cases under nearby shifts.

### 4. Safer predictive performance is weaker than meaningful inverse identification

Mototake and Sasaki are valuable because they say the scientific point without euphemism: inverse physics should not be evaluated by predictive performance alone, because physically meaningful and uniquely identified solutions may require additional constraints, and otherwise materially different coefficient functions can remain live. `REF-0150`

That is exactly the family-C lesson here.
A route that becomes more accurate by abstaining on ambiguous cases may still leave the candidate-level inverse question unanswered.
The archive should therefore ask whether the retained answer set still bears on **unique candidate-level identification**, not merely whether it looks cleaner after refusal.

### 5. Honest abstention is still weaker than witness reacquisition

Even a well-calibrated selective route can leave the archive with a hard remainder: the refused cases may be the ones where witness acquisition, experimental redesign, or new boundary packages are needed.
So the archive should require one further statement:
- are the refused discriminator-bearing cases merely deferred,
- are they empirically collapsed under a declared rule,
- or do they demand a new acquisition path before any stronger identification claim is possible?

Without that distinction, abstention can become a rhetorical sink for unresolved witness debt.

## False promotions the archive should reject

1. **lower conditional risk is not yet stronger candidate identification**
   - A route can look more reliable simply because it answers fewer hard cases.

2. **global accepted-sample coverage is not yet discriminator-bearing coverage**
   - Coverage aggregated over easy and hard cases can hide evacuation of the cases that actually separate rivals.

3. **one abstention rule is not yet shift-robust abstention competence**
   - A refusal policy that behaves well in one ecology may fail under nearby covariate, cutoff, or observer-map changes.

4. **safer predictions are not yet unique physically meaningful solutions**
   - Predictive cleanliness after abstention can still leave multiple scientifically live inverse stories.

5. **deferral is not yet reacquisition**
   - Refusing the hard cases is not the same as naming the new witness or experiment path needed to resolve them.

6. **discriminator-bearing coverage is not yet candidate-native identifiability closure**
   - Even a route that preserves hard-case coverage can still borrow gauge, map, recoverand, and witness assumptions.

## What would change archive state

A future family-C lane should earn stronger identifiability credit only if it adds, in one compact route:
1. a declared discriminator-bearing regime class rather than only a global coverage number,
2. selective risk / coverage reporting that is conditional on that hard regime rather than averaged across the whole ecology,
3. a declared minimum coverage floor or equivalent witness access floor on those candidate-separating cases,
4. a shift analysis showing that nearby covariate, cutoff, observer-map, or training-package changes do not simply eject that regime from the answered set,
5. a declared rule mapping refusals in that regime to empirical collapse, deferred reacquisition, or unresolved same/different status,
6. and, ideally, one reacquisition or redesign path showing how the refused discriminator-bearing cases could become answerable rather than merely filtered away.

Without that six-part upgrade, family C should be scored as safer at **selective answering**, not yet as stronger at candidate-native identification.

## Bottom line

The archive should now stop moving directly from “family C can abstain or control risk” to “family C is now closer to identifiability closure.”

The stronger compact posture is:

**family C now has a sharper abstention discipline, but that discipline earns real identification credit only if the retained answered set still covers the discriminator-bearing hard cases rather than merely improving reliability by abstaining on them.** `REF-0147`, `REF-0148`, `REF-0150`, `REF-0151`, `REF-0152`
