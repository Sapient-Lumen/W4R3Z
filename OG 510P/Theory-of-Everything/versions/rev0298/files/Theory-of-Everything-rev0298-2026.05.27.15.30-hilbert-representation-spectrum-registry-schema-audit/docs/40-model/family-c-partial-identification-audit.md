# Family-C partial-identification audit

This document sits at the front of `docs/40-model/family-c-identifiability-stack.md`, the archive's canonical ordered router for the family-C partial-identification / inflation-screen chain.
It preserves the first bounded family-C identifiability gain without letting that gain masquerade as either a new witness level or candidate-native identifiability closure.

Read this together with:
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/family-c-stronger-reconstruction-audit.md`
- `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-witness-closure-gate.md`
- `docs/40-model/family-c-nonuniqueness-triage.md`
- `docs/40-model/family-c-overlap-class-screen.md`
- `docs/40-model/witness-borrowing-ladder.md`

## Compression verdict

The current archive answer is now slightly sharper than a flat no-progress verdict:
- family C does earn **bounded partial-identification credit** in a restricted inverse setting, because recent holographic reconstruction work gives an explicit inversion formula from boundary entanglement data to bulk metric deformations near a fixed AdS background; `REF-0020`, `REF-0128`
- family C also now has a **first package-bound theory-reconstruction extension**, because entanglement-entropy data have been pushed further toward reconstructing not only geometry but also a bulk scalar-potential / RG-flow package in a tightly controlled holographic setting; `REF-0128`, `REF-0160`
- that gain remains heavily packaged by background choice, entangling-region choice, monotonicity / null-energy assumptions, perturbative or model-side control, and boundary-side observables rather than by a regime-free candidate-native inverse map; `REF-0127`, `REF-0128`, `REF-0160`
- and even a strong boundary-side dictionary does not automatically yield generic semiclassical uniqueness, because a single holographic CFT state may admit more than one simple semiclassical bulk description. `REF-0129`

So the correct archive move is:
**preserve family C as the strongest current partial inverse-interface lane, award only bounded partial-identification credit inside special packages, and still award no candidate-native-identifiability closure.**

## Why this document exists

The cross-family identifiability audit already says that family C is the strongest partial case.
What it still left compressed was a narrower practical question:

> strongest in what sense, exactly?

Without this family-specific audit, future revisions could oscillate between two equally distorting retellings:
- "reconstruction is already close to identification," or
- "nothing new happened beyond operator accessibility."

Both are too coarse.
This document fixes the middle ground.

## What family C has genuinely gained

### 1. Family C now has an explicit restricted inverse result

The archive can now point to more than a general reconstruction slogan.
In a controlled asymptotically AdS setting, variations in boundary entanglement entropy for ball-shaped regions can be related by an explicit inversion formula to bulk metric deviations about a fixed background, with a proposed iterative route toward fuller recovery near that background. `REF-0128`

That is real inverse progress.
It is stronger than merely saying that some bulk operator classes are reconstructable from some boundary region.
It shows that, in a disciplined package, family C can sometimes recover **specific geometric deformation data** rather than only advertise a qualitative dictionary. `REF-0020`, `REF-0128`

### 2. Family C now has a first package-bound theory-reconstruction extension

The live gain is no longer only that some boundary entanglement data can recover geometric deformation structure.
A newer reconstruction pass argues that, in a tightly packaged holographic setting, one can push from entanglement entropy to a reconstructed bulk scalar field profile and scalar potential, then read off RG-flow information from that reconstructed gravity package. `REF-0160`

That is a real strengthening of what counts as restricted inverse progress.
It means the archive can now point to a first family-C route that tries to recover a small piece of the **dual gravity theory**, not only the background geometry.

### 3. The gain is still package-bound rather than regime-free

This inverse progress still does not arrive as a general native identification map for arbitrary bulk structure.
It depends on a fixed asymptotic setting, controlled entangling regions, an Abel-inversion style reconstruction package, monotonicity / null-energy conditions, and boundary-side observables whose informational role is still doing much of the work. `REF-0127`, `REF-0128`, `REF-0160`

So the archive should award real credit, but only as **restricted inverse-interface credit plus one package-bound theory-reconstruction extension**.
The gain is not yet a general rule for which bulk distinctions or theory-level structures are learnable across the family-C lane as a whole.

### 4. Semiclassical uniqueness can still fail

The archive should now pair the restricted inverse gain with a matching brake.
Antonini and Rath give a concrete example in which one holographic CFT state admits two simple semiclassical bulk descriptions: one with a closed universe and one without.
Their conclusion is not that holography fails, but that the dictionary can remain ambiguous even when the boundary state is fixed. `REF-0129`

That matters directly for identifiability.
Even where family C has a strong forward dictionary and a sharpened inverse interface, the candidate still needs an explicit rule for when apparently different bulk descriptions count as genuinely different targets, gauge-related redescription, or empirically collapsed alternatives.
Without that rule, reconstruction strength is still weaker than identifiability closure. `REF-0119`, `REF-0129`

## Why this still does not close candidate-native identifiability

### 1. The target space is still partly borrowed from the boundary package

The family-C inverse gain is formulated relative to a chosen boundary observable package, background neighborhood, and reconstruction regime.
Even the new theory-reconstruction extension still targets a scalar-potential / RG-flow package specified through that boundary-guided reconstruction ecology.
That means the target of identification is not yet specified in a regime-free candidate-native way.
The candidate still inherits too much of its same/different structure from the boundary setup. `REF-0127`, `REF-0128`, `REF-0160`

### 2. Informational completeness is local and conditional, not archive-wide

An explicit inversion formula in one controlled regime is not yet a family-wide statement of informational completeness.
It does not yet tell the archive which bulk distinctions remain invisible outside that regime, which are only partially identified, and which collapse once finite-`N`, closed-universe, or non-perturbative complications are restored. `REF-0061`, `REF-0128`, `REF-0129`

### 3. Uniqueness failure blocks overpromotion

If one boundary state can support multiple semiclassical bulk descriptions, then even a strong inverse interface cannot simply be retold as a unique bulk-identification rule.
The archive should therefore block any move from "we can reconstruct something in a restricted package" to "family C now identifies the underlying bulk ontology." `REF-0129`

### 4. Candidate-native empirical-collapse rules remain unpaid

The decisive debt is still the same one named by `OQ-0057`.
Family C does not yet say in its own bridge variables which bulk distinctions are:
- uniquely learnable,
- only equivalence-class identifiable,
- setup-relative,
- or properly underdetermined / empirically collapsed.

Until that native collapse map is explicit, the archive should keep family C below candidate-native identifiability closure. `REF-0119`, `REF-0061`, `REF-0129`

## False promotions the archive should reject

1. **explicit inversion is not generic identification**
   - A controlled inversion formula near a fixed background is not yet a regime-free bulk-identification rule.

2. **reconstruction of deformation data is not unique ontology**
   - Recovering metric perturbations in one package is not the same as uniquely fixing the physically relevant bulk description in all relevant packages.

3. **same boundary state is not yet one bulk story**
   - A fixed boundary state does not by itself settle whether there is one semiclassical bulk target, several equivalent targets, or several genuinely distinct but empirically collapsed descriptions.

4. **strongest partial case is still not closure**
   - Family C can be the strongest current inverse-interface lane while still failing candidate-native identifiability.

## What would change archive state

A future family-C lane should earn stronger identifiability credit only if it adds, in one compact route:
1. a clearer native target class for the bulk distinctions under discussion,
2. an explicit native sameness / equivalence / empirical-collapse rule,
3. a declared informational-completeness or partial-identification condition,
4. an inversion-stability statement beyond one tightly packaged perturbative neighborhood,
5. and an explicit rule for when non-uniqueness is physical, gauge, or underdetermination rather than hidden dictionary drift.

Without that five-part route, family C remains the archive's strongest partial inverse lane, not a solved identification lane.

## Net result

The archive now has a tighter family-C answer under `OQ-0057`.
Family C has moved beyond pure reconstruction rhetoric: it now has restricted inverse progress worth preserving plus a first package-bound theory-reconstruction extension.
But that same lane still lacks a general candidate-native identifiability story, and current holographic uniqueness tensions make overpromotion even less acceptable than before. `REF-0128`, `REF-0129`, `REF-0160`

That is the right archive state:
**real partial inverse credit, one package-bound theory-reconstruction extension, explicit non-uniqueness brake, no identifiability closure.**
