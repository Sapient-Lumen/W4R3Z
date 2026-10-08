# Family-C recoverand versus surrogate screen

This document sits inside `docs/40-model/family-c-identifiability-stack.md`, the archive's canonical ordered router for the family-C partial-identification / inflation-screen chain.
It keeps one specific inflation move in focus:
**route-local bulk recovery being retold as recovery of the candidate-native bulk target itself, rather than of a filtered, ansatz-bound, or prior-loaded surrogate.**
Score that gain at this stage, then route broader family-C credit through the stack rather than promoting directly to candidate-native identifiability closure.

Read this together with:
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/family-c-inverse-stability-and-regularization-screen.md`
- `docs/40-model/family-c-thin-data-vs-acquirable-witness-screen.md`
- `docs/40-model/family-c-overlap-class-screen.md`
- `docs/40-model/family-c-partial-identification-audit.md`
- `docs/40-model/family-c-inverse-portability-screen.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`

## Compression verdict

The archive should now preserve four compact points at once:
- family C does earn **surrogate-aware inverse credit**, because current routes can recover structured bulk objects from boundary data in more than one way: explicit inverse formulas near fixed backgrounds, inverse-scattering reconstruction from correlators, phenomenological two-point-function dictionaries, and learned inverse RT maps. `REF-0128`, `REF-0130`, `REF-0140`, `REF-0142`
- but several of these routes already tell us, in their own setup language, that the recovered object lives inside a **declared reconstruction ecology**: a phenomenological dictionary rather than a full non-perturbative one, a strict large-`N` / GFF package, a single-function metric ansatz, hard or soft physics-informed constraints, a filtering stack, or a training distribution. `REF-0130`, `REF-0140`, `REF-0142`, `REF-0143`
- so route-local success can still mean **recovery of a best-fit surrogate bulk** — a representative inside one model family or one regularized equivalence class — rather than recovery of the candidate-native bulk target whose same/different structure the archive ultimately cares about. `REF-0130`, `REF-0140`, `REF-0142`, `REF-0143`
- the correct archive move is therefore: **treat current family-C inverse outputs as recoverands only after an explicit surrogate audit naming the target variables, the prior / ansatz / constraint stack, the filtering or regularization stack, and the candidate-level distinctions that provably survive those choices.** `REF-0128`, `REF-0130`, `REF-0140`, `REF-0142`, `REF-0143`

## Why this document exists

The archive already blocks several overpromotions in the family-C lane:
- multiplicity is no longer allowed to bypass non-uniqueness triage,
- method diversity is no longer allowed to bypass overlap-class alignment,
- thin-data success is no longer allowed to bypass acquisition and witness questions,
- and conditioned robustness is no longer allowed to bypass portability or abstention discipline.

What still remained under-explicit was one more inflation move:

> if the route returns a bulk geometry-like object with good accuracy, then it has recovered the real bulk target.

That step is still too fast.
Current family-C papers increasingly succeed by **declaring and then working inside a reconstruction ecology**.
The archive should preserve that progress honestly, but it should also distinguish:
- a candidate-native bulk target,
- a route-specific recoverand,
- and a filtered / prior-loaded surrogate produced because the route has fixed too much of the answer class in advance.

## The four required declarations

### 1. Target declaration versus model-family declaration

A family-C route should first declare what it is actually recovering.
Kim's inverse RT Transformer is explicit that it approximates the inverse relation **within a metric ansatz** and targets a single blackening function in `AdS_3`, not the full gravitational solution space. `REF-0142`
Nebabu et al. are likewise explicit that they pursue a **phenomenological dictionary** from boundary two-point data to a semiclassical bulk geometry and bulk operators, not a full non-perturbative dictionary. `REF-0140`

So the archive should now ask:
**is the route recovering the candidate-native target, or one declared representative variable inside a narrower model family?**
If the latter, it earns route credit, not candidate-native identification credit.

### 2. Prior / ansatz / constraint stack declaration

Physics-informed inverse routes do not start from nowhere.
Jeong et al. describe PIML explicitly as integrating prior physical or theoretical knowledge into the learning process, and note that boundary or initial conditions may be imposed directly as hard constraints through an ansatz to stabilize convergence. `REF-0143`
Kim likewise fixes asymptotic AdS behavior and a regular single-horizon geometry class from the outset. `REF-0142`
Nebabu et al. assume a boundary generalized free field in a strict large-`N` limit. `REF-0140`

So the archive should now ask:
**which part of the recovered bulk story came from the data, and which part was already carved out by the prior / ansatz / constraint stack?**
Without that split, route-local recovery may still be best-fit selection inside a heavily pre-shaped target manifold.

### 3. Filtering / regularization stack declaration

Some current family-C gains depend materially on regularization choices.
Fan and Yang explicitly analyze reconstruction under measurement noise, show serious degradation at larger perturbations, and then improve accuracy with repeated filtering and truncation strategies. `REF-0130`
Kim reports that adding white noise during training was crucial for generalization and that predictions degrade sharply outside the training range. `REF-0142`

So the archive should now ask:
**is the recovered bulk object invariant across nearby filtering, truncation, training-noise, and regularization choices, or is it one regularized representative selected by the current stack?**
If the latter, the output is still a route-conditioned surrogate until the equivalence class is named and the stack dependence is bounded.

### 4. Surviving distinction declaration

Even after the first three declarations, a route still needs to say which candidate-level distinctions survive its ecology.
Jokela et al. recover metric deformations near a fixed background; Nebabu et al. recover semiclassical geometry from two-point data under a phenomenological dictionary; Kim recovers a blackening-function profile inside one ansatz family. `REF-0128`, `REF-0140`, `REF-0142`
These are real gains, but they do not yet by themselves say whether candidate-level differences in topology, gauge/frame class, matter content, horizon structure, or non-perturbative completion have been identified, collapsed into one equivalence class, or silently excluded by construction.

So the archive should now ask:
**which bulk differences remain visible after the route's ecology is fixed, and which were never in play because the route only aimed at a surrogate recoverand?**
That question belongs inside identifiability scoring, not after it.

## False promotions the archive should reject

1. **good reconstruction error is not yet target recovery**
   - Accurate output inside one ansatz family can still be best-fit surrogate selection.

2. **phenomenological dictionary is not candidate-native dictionary closure**
   - A useful route from boundary data to semiclassical geometry can still borrow the target class from a setup-relative dictionary.

3. **hard constraints are not neutral background choices**
   - Boundary conditions, architecture choices, and encoded ansätze shape what can count as a valid recovered bulk.

4. **filtered agreement is not surrogate-free identification**
   - Better accuracy after truncation, denoising, or training-noise conditioning can still leave the route selecting one regularized representative.

5. **one recoverand is not the whole bulk target space**
   - Recovering a blackening function, near-background deformation, or effective geometry does not yet identify all candidate-level same/different structure.

## What would change archive state

A future family-C lane should earn stronger identifiability credit only if it adds, in one compact route:
1. an explicit declaration of the candidate-level target object and the narrower surrogate recoverand if these differ,
2. one audit of which priors, ansätze, hard constraints, and theory-side assumptions pre-shape the admissible output family,
3. one invariance statement across nearby filtering / regularization / training-stack choices,
4. one out-of-family or abstention rule for data that do not support a unique recoverand inside the ecology,
5. and one candidate-native same/different or empirical-collapse rule for the bulk distinctions that remain after all of the above.

Without that five-part upgrade, family C should be scored as stronger at producing disciplined surrogates, not yet as having recovered the candidate-native bulk target.

## Net result

The archive should now stop sliding from “family C can output a bulk object with real accuracy” to “family C has therefore recovered the real bulk target.”
That is too fast.
The stronger and still disciplined statement is:

**family C now has enough inverse success that the archive must distinguish recoverand from surrogate: current routes can reconstruct useful bulk objects, but many of those objects are still carved out by phenomenological dictionaries, strict large-`N` packages, metric ansätze, hard constraints, filtering stacks, or training ecologies, so the lane earns surrogate-aware inverse credit without candidate-native identifiability closure.** `REF-0128`, `REF-0130`, `REF-0140`, `REF-0142`, `REF-0143`
