# Candidate-native abstention and no-verdict protocol

This document sharpens field 7 of `docs/40-model/candidate-native-identifiability-cashout-template.md`.
It does **not** add a new witness level, open the followthrough queue, or promote any live lane.
It says what a future route must disclose before the archive may treat a forced output, best-fit candidate, posterior mode, reconstructed geometry, selected vacuum, or classifier label as candidate-native identification rather than as a decision made under unresolved evidence.

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-public-bridge-challenge-protocol.md`
- `docs/40-model/candidate-native-equivalence-collapse-protocol.md`
- `docs/40-model/candidate-native-acquisition-realizability-protocol.md`
- `docs/40-model/candidate-native-inverse-completeness-stability-protocol.md`
- `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-abstention-competence-vs-soft-confidence-screen.md`
- `docs/40-model/family-c-point-estimate-vs-calibrated-solution-bundle-screen.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

A route that can acquire a record and run an inverse still has not identified a candidate-native target if it cannot say when the correct output is **not one target**.

Candidate-native abstention is not politeness, caution, or a UI option.
It is the native rule that tells the lane when the evidence should collapse to:
- an equivalence class;
- a calibrated solution bundle;
- an interval, posterior family, or rank-deficient manifold;
- a proxy-only or surrogate-only output;
- an out-of-regime warning;
- a no-acquisition or no-inversion state;
- or a public no-verdict.

So the archive should now use the stronger sentence:

**candidate-native identifiability requires a native refusal rule: the same route that names targets, records, equivalence classes, acquisition channels, inverse completeness, and margins must also name the evidence states in which it refuses target-level identification and returns a collapsed, underdetermined, out-of-regime, or no-verdict output.**

That sentence changes audit state, not closure state.
No current live lane is promoted.

## Why field 7 is needed after fields 5 and 6

The inverse-completeness / stability protocol already asks for a no-inversion zone.
That is necessary but not sufficient.
A no-inversion zone says where a mathematical or statistical inverse should not be trusted.
Field 7 asks what the candidate route **does instead** and whether that refusal behavior is native, public, and stable.

Without a field-7 protocol, a lane can over-credit itself in six common ways:

1. **best-answer inflation** — a route always reports the top candidate even when the evidence only supports an equivalence class;
2. **soft-confidence inflation** — wide uncertainty bars, entropy scores, or posterior spreads are treated as abstention even though the route never refuses target identity;
3. **policy inflation** — a threshold, regularizer, prior, or classifier policy decides when to defer, but the deferral rule is not candidate-owned;
4. **exception erasure** — out-of-regime, null, nuisance-dominated, proxy-only, or rank-deficient cases are filtered away before scoring;
5. **bundle collapse inflation** — a calibrated solution bundle is narrated as one recovered geometry, state, vacuum, or history;
6. **public-noise inflation** — failed acquisition, unstable custody, or irreproducible rerun is treated as weak confirmation rather than no public verdict.

Field 7 blocks those moves.
It makes no-verdict behavior a positive competence only when the route says exactly which evidence states trigger it and what output replaces target identification.

## Minimum abstention / no-verdict row

A future field-7 upgrade should provide one compact row with the fields below.
A blank field locates debt; it does not by itself refute the lane.

| Row item | Minimum content | Inflation blocked |
|---|---|---|
| Target claim boundary | The exact target, quotient, class, bundle, interval, or proxy the route is allowed to identify before abstention is triggered. | Letting a route refuse vaguely while still claiming a strong target when convenient. |
| Trigger state | The native condition that forces abstention: empirical collapse, rank deficiency, no acquisition, no inversion, low margin, nuisance domination, out-of-regime setup, unstable policy, proxy-only record, or failed public bridge. | Hiding no-verdict cases inside discretionary judgment. |
| Evidence state returned | What the route returns instead of a target: equivalence class, calibrated solution bundle, partial order, interval, posterior family, underdetermined manifold, discriminator-only result, proxy-only output, or no public verdict. | Reporting one answer where the evidence supports a weaker object. |
| Native trigger owner | Whether the trigger is declared in candidate bridge variables, borrowed from ordinary statistics / laboratory practice / boundary packaging, or imposed by an external decision policy. | Treating generic uncertainty management as candidate-native abstention. |
| Margin and tie relation | How the abstention trigger relates to the field-6 separation margin, tie zone, robustness transport, and no-inversion condition. | Making deferral independent of the actual inverse / margin debt. |
| Acquisition relation | How no-acquisition, proxy-only, nuisance-dominated, or failed custody states become abstention rather than weak evidence. | Treating unavailable or unstable records as partial confirmation. |
| Equivalence relation | Whether the route abstains because targets are physically the same, empirically collapsed, gauge/frame redescription, or merely unresolved by the present record. | Confusing identity, collapse, and ignorance. |
| Re-entry condition | What additional record, margin, regime control, public rerun, or bridge declaration would move the route from no-verdict to partial identification. | Creating a permanent ambiguous holding pen with no cash-out path. |
| Public challenge handle | How an outside community can inspect the abstention behavior: challenge set, null suite, blind rerun, error certificate, disclosed policy, calibration ledger, custody audit, or analytic proof. | Letting private exception handling masquerade as public evidential discipline. |

## Field-code rule

This protocol refines field 7 in the route ledger.

| Field-7 state | Code | Meaning |
|---|---|---|
| No abstention, collapse, underdetermination, out-of-regime, no-acquisition, or no-inversion behavior is named. | `M` | Missing abstention discipline. |
| Abstention is imported from generic statistics, ordinary laboratory confidence language, benchmark conventions, boundary packaging, model-selection policy, or a human review rule. | `B` | Borrowed abstention discipline. |
| The route declares a bounded no-verdict, bundle, equivalence-class, proxy-only, or out-of-regime output for one record domain, validity window, target quotient, dataset ecology, or decision policy. | `P` | Partial abstention discipline. |
| The candidate's own bridge variables specify the trigger states, returned evidence states, re-entry conditions, and public challenge handle for refusing target-level identification. | `N` | Native abstention / no-verdict discipline for the stated regime. |

An `N` in field 7 still does not close candidate-native identifiability.
The route still owes native target, record, equivalence, acquisition, inverse, stability / margin, and public bridge fields.
But no route with `M` in field 7 should be scored above partial identification, because it cannot distinguish successful identification from forced answer production.

## Relation to the previous field protocols

### 1. Equivalence discipline is not abstention discipline

The equivalence-collapse protocol says whether two apparent targets are the same, distinct, or empirically collapsed.
The abstention protocol says what the route returns when that rule blocks target-level identification.
A route may know that two states are empirically collapsed and still lack a public no-verdict procedure.

### 2. No-acquisition is not weak evidence

The acquisition-realizability protocol asks whether a record can be obtained.
If the answer is no, proxy-only, nuisance-dominated, or custody-unstable, field 7 must say whether the correct output is no acquisition, no public verdict, or a lower-level proxy result.
The archive should not let failed acquisition become a faint positive signal.

### 3. No-inversion is not merely bad performance

The inverse-completeness / stability protocol asks where the inverse becomes rank-deficient, unstable, tied, or margin-insufficient.
Field 7 converts those zones into declared outputs.
A route that knows its no-inversion zone but still reports one target has not earned abstention credit.

### 4. Calibration is not abstention unless it changes the output class

A calibrated posterior, bundle, error bar, entropy score, or classifier confidence is useful.
It becomes abstention only when the route has a rule saying when those quantities force an equivalence-class, bundle, interval, proxy-only, or no-verdict output rather than one target.

### 5. Public challenge is part of abstention

A private no-verdict policy is weaker than a public challengeable one.
Outside reruns must be able to discover whether the route abstained in the right places, deferred selectively, or hid hard cases through preprocessing. The public-bridge challenge protocol is broader: it asks whether the full identification route, not only its refusal behavior, can be exported to a challengeable public carrier.

## Application to the current landscape

### Family C

Family C has the strongest partial field-7 profile among current rows.
The archive already contains screens for point-estimate versus calibrated solution bundles, abstention competence versus soft confidence, selective safety versus discriminator coverage, policy choice versus candidate-order stability, and order-stability versus separation margin.
Those surfaces make Family C unusually explicit about the danger of forced geometry, forced bulk, or forced target outputs.

But field 7 is still not native closure.
The deferral and bundle language remains tied to boundary dictionary choices, sparse-data route assumptions, regularizers, training or simulation ecology, posterior and policy choices, finite-window controls, code-subspace restrictions, and public-record custody borrowed from ordinary laboratory / boundary practice.
The candidate does not yet own the rule that says when target identity should collapse to bundle, equivalence class, no-inversion, or no public verdict.

Current score impact: **keep field 7 at `P/B`, not `N`.**
Family C earns serious abstention-discipline credit because it names more failure modes than the other current rows, not because it has candidate-native refusal closure.

### Completion bids

Completion bids often prefer a total answer: one vacuum, one UV completion, one fixed-point trajectory, one continuum corridor, one causal growth law, one amplitude island, or one selection result.
A total formal answer is not a no-verdict policy.
A completion bid earns field-7 credit only if it says when observed records, formal constraints, or special corridors should return underdetermination, equivalence class, multiple compatible sectors, no observed-sector attribution, or no public verdict.

Current score impact: **target-rich completion rows remain abstention-poor** unless they install an explicit refusal rule tied to public records and candidate variables.

### Low-energy laboratory, detector, and simulation lanes

Lab and simulation lanes can have good null results, control conditions, threshold tests, challenge sets, and no-signal outcomes.
That can be real field-7 progress.
But the abstention rule is often experimenter-owned or statistics-owned rather than candidate-owned: it says the campaign cannot discriminate the chosen alternatives, not that the candidate itself has returned a native no-identification state.

Current score impact: **public no-result discipline can be strong while candidate-native abstention remains borrowed.**

### Witness-side frame and observer routes

Frame, observer, and asymptotic-access lanes are especially good at revealing when one frame fact should not be retold as a public cross-frame fact.
That is a genuine abstention pressure.
But public same-fact transport, custody, cross-frame comparison, and shared challenge standards remain unpaid.

Current score impact: **perspective-sensitive no-verdict discipline is valuable, but not yet public or candidate-native closure.**

### Family B

Family B still stops earlier.
Thermodynamic and trace discipline can say when a derivation is regime-bound or equilibrium-limited, but it does not yet supply a native target / record / inverse route whose abstention behavior could be field-7 scored.

Current score impact: **bounded caution remains below candidate-native abstention credit.**

## Future-edit rule

A future revision may claim a field-7 improvement only if it says all of the following:

1. which ledger row changed;
2. the old field-7 code and proposed new field-7 code;
3. the target claim boundary and target quotient to which abstention applies;
4. the trigger states that force no-verdict, bundle, equivalence-class, proxy-only, or out-of-regime output;
5. the evidence state returned instead of one target;
6. whether the trigger is candidate-native, borrowed, or policy-imposed;
7. how the trigger relates to the field-3 equivalence rule, field-4 acquisition route, and fields-5/6 inverse / margin row;
8. the re-entry condition that would convert no-verdict into partial identification;
9. the public challenge handle for testing that the route abstains in the right places;
10. whether any claim-registry status changed or the revision only clarified debt.

If those ten items are absent, the revision may still be useful, but it should be scored as caution, uncertainty reporting, benchmark calibration, null-result discipline, or policy engineering rather than as candidate-native abstention progress.

## Anti-inflation rules

Reject the following shortcuts:

1. **best-fit shortcut** — the top-ranked target is not identified when the route owes an equivalence class or bundle.
2. **uncertainty-bar shortcut** — an error bar is not abstention unless it changes the allowed output class.
3. **threshold shortcut** — a numerical cutoff is not native refusal unless the candidate owns the trigger and returned state.
4. **null-result shortcut** — a no-signal or failed acquisition is not weak confirmation by default.
5. **hard-case filtering shortcut** — removing ambiguous cases before scoring is not abstention competence.
6. **posterior-mode shortcut** — a narrow or broad posterior is not a native no-verdict rule by itself.
7. **policy-stability shortcut** — stable deferral under one policy is not candidate-native abstention unless neighboring admissible policies preserve the same refusal semantics.
8. **publicness shortcut** — a public no-result can be strong laboratory discipline while the candidate-native field remains borrowed.

## Net result

The archive now has a field-7 counterpart to the equivalence, acquisition, and inverse / stability protocols.
Candidate-native identifiability no longer allows a route to force one target merely because it can name a formal target, acquire a record, run an inverse, or report a margin.
It must also say when the honest output is equivalence class, bundle, proxy-only, out-of-regime, no acquisition, no inversion, or no public verdict.

That sharpens `OQ-0057` without promoting any lane:
- family C remains the strongest partial abstention row but still borrows decisive refusal semantics from boundary, policy, simulation, regularization, and public-record practice;
- completion bids remain especially vulnerable to total-answer inflation;
- lab and simulation lanes may have strong null-result discipline while remaining candidate-target-limited;
- witness-side frame routes may have strong perspective-collapse discipline while public bridge debt remains unpaid;
- and no current lane earns candidate-native identifiability closure.
