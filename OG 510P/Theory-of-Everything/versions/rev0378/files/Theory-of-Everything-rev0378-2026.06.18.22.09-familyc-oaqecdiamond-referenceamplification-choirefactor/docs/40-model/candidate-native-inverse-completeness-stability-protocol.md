# Candidate-native inverse-completeness and stability protocol

This document is the field-5 / field-6 counterpart to the candidate-native equivalence and acquisition protocols.
It does **not** add a witness level, open the followthrough queue, or promote any current lane.
It says what a future lane must disclose before a target-to-record route can be retold as stable candidate-native identification rather than as discrimination, fitting, reconstruction, or proxy success.

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-abstention-no-verdict-protocol.md`
- `docs/40-model/candidate-native-public-bridge-challenge-protocol.md`
- `docs/40-model/candidate-native-equivalence-collapse-protocol.md`
- `docs/40-model/candidate-native-acquisition-realizability-protocol.md`
- `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/acquisition-vs-attribution-gate.md`

## Compression verdict

A record route does not become candidate-native identification just because the record is acquirable.
It becomes identification only to the extent that the candidate can say:

**which native targets are recoverable, which are collapsed into an equivalence class, which are rank-deficient or nuisance-confounded, which become unstable under finite precision or policy variation, and when the honest output is no inverse / no verdict.**

That is the paired debt after acquisition.
Field 4 asks whether the record can be obtained.
Field 5 asks what the obtained record can identify.
Field 6 asks whether that identification survives finite resolution, noise, cutoff, prior, regularization, training ecology, and policy changes with a declared margin.

## Why fields 5 and 6 must be paired

The archive has several ways to over-credit an inverse route:

1. **separability inflation** — one pair of alternatives can be separated, so the whole target space is treated as identified;
2. **best-fit inflation** — the top-ranked candidate is treated as identified despite ties, flat directions, or nearby nuisance packages;
3. **formal-inverse inflation** — a mathematical inverse exists under exact data, but finite public records make it ill-conditioned;
4. **regularized-success inflation** — a filter, ansatz, prior, or neural route stabilizes an answer by importing structure not owned by the candidate;
5. **benchmark inflation** — in-distribution performance is retold as portable candidate-native learnability;
6. **quotient erasure** — the route actually identifies an equivalence class, bundle, interval, posterior family, or coarse-grained object, but the prose names one target.

Fields 5 and 6 therefore function as one paired check.
A lane may get field-5 partial credit for a restricted inverse.
It may get field-6 partial credit for margins inside a finite route.
It cannot get candidate-native identifiability closure unless the inverse-completeness claim and the stability / margin budget apply to the same declared target quotient under the same route boundary.

## Required inverse row

A future field-5 / field-6 upgrade must fill this row.
A missing cell is not a stylistic gap; it is the remaining debt.

| Row item | Minimum content | Inflation blocked |
|---|---|---|
| Candidate target quotient | The exact target, effective target, parameter, geometry, sector, history, frame fact, or equivalence class the route claims to recover. State whether the target has already been quotientized by the equivalence-collapse protocol. | Recovering one representation while claiming a stronger object. |
| Record domain | The acquired record class and acquisition boundary to which the inverse claim applies. Link to the field-4 acquisition row when one exists. | Exporting an inverse beyond the records actually obtainable. |
| Completeness claim | Whether the route is complete, locally complete, subset-complete, quotient-complete, partially identifying, discriminating only, rank-deficient, or missing. | Treating some discrimination as target-space identification. |
| Deficiency map | The null directions, gauge / frame ambiguities, counterpart choices, nuisance packages, hidden variables, priors, selection effects, or empirical-collapse zones that remain. | Hiding nonuniqueness behind the best answer. |
| Stability budget | Finite-resolution, noise, cutoff, finite-`N`, conditioning, regularization, sample-size, training-distribution, emulator-error, systematic, and computational budgets under which the inverse remains usable. | Treating exact or clean data as representative of public records. |
| Separation / tie margin | The distance, likelihood ratio, posterior spread, interval width, discriminant, classifier margin, reconstruction error, or order-stability condition that separates the claimed targets from nearby collapsed alternatives. | Treating ranked output as identified without a margin. |
| Robustness transport | What happens when the route is re-run under nearby gauges, frames, dictionaries, priors, regularizers, truncations, backgrounds, calibration states, or acquisition campaigns. | Treating one policy-stable answer as portable candidate-native stability. |
| No-inversion / no-verdict zone | The native condition under which the route must return underdetermined, equivalence-class, rank-deficient, out-of-regime, unstable, or no-verdict rather than one target. | Forcing identification when the route itself should abstain. |
| Public audit handle | How an outside community could inspect the inverse claim: rerun data, disclosed code, analytic proof, error certificate, calibration ledger, challenge set, or public record custody. | Letting private or package-bound inversion masquerade as public learnability. |

## Field-code rule

This protocol refines fields 5 and 6 of the route ledger.
It keeps the existing `M/B/P/N` ledger code language but forces the two fields to be interpreted together.

### Field 5: inverse-completeness state

| Field-5 state | Code | Meaning |
|---|---|---|
| No inverse or learnability claim is named. | `M` | Missing inverse discipline. |
| The inverse is imported from ordinary tomography, external parameter estimation, gauge fixing, benchmark labels, prior choice, modeler's truth, or a boundary dictionary whose target semantics are not candidate-owned. | `B` | Borrowed inverse discipline. |
| The route identifies a named subset, quotient, interval, posterior family, feature class, discriminator-bearing contrast, or regime-limited target, with boundaries declared. | `P` | Partial inverse discipline. |
| The candidate's own bridge variables specify what is recoverable and what is collapsed or underdetermined for the declared target quotient and record domain. | `N` | Native inverse-completeness for the stated regime. |

### Field 6: stability / margin state

| Field-6 state | Code | Meaning |
|---|---|---|
| No finite-resolution or robustness budget is named. | `M` | Missing margin discipline. |
| Stability is borrowed from a benchmark, regularizer, filter, training distribution, external statistical convention, or ordinary lab confidence language. | `B` | Borrowed margin discipline. |
| A margin or robustness budget exists for one finite route, validity window, ansatz class, setup, code subspace, or dataset ecology. | `P` | Partial margin discipline. |
| The candidate's own bridge variables declare finite-resource, nuisance, cutoff, no-inversion, and robustness conditions for the same target quotient and record domain scored in field 5. | `N` | Native stability / margin discipline for the stated regime. |

### Paired-score rule

Use the lower of field 5 and field 6 when deciding whether an inverse route can support candidate-native identifiability credit.
A complete-looking inverse with unstable margins is not stronger than `P`.
A stable-looking policy with an incomplete or borrowed inverse is not stronger than `P`.
A route that cannot name its no-inversion zone should not be scored above `P`, even if it performs well on examples.
A route that names a no-inversion zone still owes field-7 behavior: the abstention / no-verdict protocol says what the route returns in that zone and how outsiders can challenge the refusal rule. Field 8 then asks whether the whole route has a public bridge object, custody unit, replay path, challenge rule, terminal states, and independence boundary.

## Distinctions the archive should preserve

### 1. Discrimination versus identification

A route can discriminate between two alternatives without identifying the underlying target.
That is real evidence when the alternatives matter, but it is not candidate-native identifiability closure unless the route says which larger target distinctions remain learnable or collapsed.

### 2. Reconstruction versus inverse completeness

A reconstruction can return a geometry-like object, operator, history, state, or model parameter.
Inverse completeness asks whether every candidate-relevant distinction in the declared target class is recoverable, quotientized, or honestly left unresolved.

### 3. Regularization versus native stability

A regularizer, prior, ansatz, network, truncation, or filter can be scientifically useful.
It becomes candidate-native stability only if the lane discloses which structure is imported, which targets are stabilized by the candidate itself, and which outputs change under nearby admissible choices.

### 4. Posterior concentration versus empirical collapse

A narrow posterior or high-confidence classifier is not automatically target identity.
The route must say whether nearby targets are physically distinct, gauge / frame redescription, empirically collapsed, or merely disfavored under a chosen prior.

### 5. Public reproducibility versus candidate-native inverse ownership

Public code, public data, or reproducible benchmarks can strengthen auditability.
They do not by themselves make the inverse candidate-native.
The candidate still owes the target quotient, deficiency map, stability budget, and no-inversion rule in its own bridge language.

## Application to the current landscape

### Family C

Family C remains the strongest partial row because it has real restricted inverse routes, thin-data geometry recovery, overlap-class checks, inverse-stability screens, recoverand discipline, calibration pressure, abstention competence, policy-stability checks, and separation-margin screens.
Those gains should be preserved.

But field 5 and field 6 still do not close.
The target quotient is usually package-, code-subspace-, boundary-, dictionary-, finite-window-, large-`N`-, or gauge-conditioned.
The record domain is often boundary or simulation ecology rather than a candidate-owned public record class.
The deficiency map still includes nonuniqueness, sparse-data underdetermination, observer-map choice, counterpart / frame choice, training priors, ansatz restrictions, and finite-resolution limits.
The stability budget is route-specific rather than native and portable.

Current score impact: **keep field 5 and field 6 at `P`, not `N`.**
Family C is strongest because it exposes the inverse debts most explicitly, not because it has paid them all.

### Completion bids

Completion bids can often name enormous target spaces, formal dualities, fixed points, histories, amplitudes, vacua, spectra, or consistency regions.
That is not an inverse-completeness row.
A completion bid must still state which public records would identify which target quotient, which nearby targets remain empirically collapsed, and what finite margin distinguishes the target from alternatives.

Current score impact: **target-rich completion rows stay inverse-borrowed or inverse-partial** unless they give a record-domain-specific deficiency map and stability budget.

### Laboratory, detector, and simulation lanes

Laboratory and simulation lanes may have stronger acquisition and public-audit handles than formal completion lanes.
They can also have local margins, error bars, counts, decoherence budgets, or rerunnable pipelines.
That is real field-4 and sometimes field-6 credit.

But the inverse target is often externally chosen: mediator quantumness, a semiclassical alternative, a stochastic environment class, a local-operator package, or a limited model contrast.
A strong margin for one contrast is not a native inverse for the full candidate target space.

Current score impact: **real discriminator and margin credit, not candidate-native inverse closure.**

### Witness-side frame and observer routes

Frame-conditioned and observer-relative lanes are useful because they expose where target identity depends on perspective, gauge, edge structure, clocks, or relational variables.
They are therefore close to the equivalence problem but still often weak on public inverse transport.
A one-frame inverse or one-observer record can be stable locally while remaining nonportable across public comparison standards.

Current score impact: **bounded frame-side inverse discipline, not public candidate-native identification.**

### Family B

Family B remains earlier than this protocol.
Equation recovery, entropy balance, and trace sharpening do not yet supply a candidate-native inverse row from public records back to candidate targets.

Current score impact: **bounded trace discipline remains below field-5 / field-6 inverse credit.**

## Future-edit rule

A future revision may claim an inverse-completeness or stability-field improvement only if it says all of the following:

1. which route-ledger row changed;
2. whether field 5, field 6, or both changed;
3. the old code and proposed new code for each touched field;
4. the candidate target quotient and record domain;
5. the completeness claim and deficiency map;
6. the stability budget and separation / tie margin;
7. the robustness transport tests across nearby admissible route choices;
8. the no-inversion / no-verdict zone;
9. the public audit handle;
10. whether the result changes attribution, public bridge, or witness-package debt, or only local inverse discipline.

If those ten items are absent, the revision may still be useful, but it should be scored as reconstruction, discrimination, fit, benchmark performance, regularized proxy success, or margin sharpening rather than as candidate-native inverse-completeness progress.

## Anti-inflation rules

Reject the following shortcuts:

1. **pairwise-separation shortcut** — separating two alternatives is not identifying the target space.
2. **exact-data shortcut** — an inverse under ideal data is not stable identification under public finite records.
3. **regularizer shortcut** — a stable filtered answer is not native stability unless imported structure and failure modes are declared.
4. **benchmark shortcut** — in-distribution success is not portable inverse closure.
5. **posterior shortcut** — confidence is not target identity without an equivalence and deficiency map.
6. **ranking shortcut** — top-ranked output is not identification without tie and separation-margin discipline.
7. **auditability shortcut** — public code or repeatability is not candidate-native inverse ownership.
8. **silence shortcut** — failing to name collapsed, rank-deficient, or no-inversion zones should lower the score, not raise confidence.

## Net result

The archive now has a paired field-5 / field-6 protocol after the equivalence and acquisition protocols.
Candidate-native identifiability can no longer move from acquired record to identified target without declaring inverse completeness and finite stability margins.

That sharpens `OQ-0057` without promoting any lane:
- family C remains the strongest partial inverse row but still has package-, boundary-, dictionary-, route-specific stability, target-quotient, and abstention / no-verdict debt;
- completion bids remain target-rich but public-record-to-target inverse-poor;
- laboratory and simulation lanes may have real acquisition and margin credit while remaining candidate-target-limited;
- witness-side frame lanes may clarify local or perspective-conditioned inverse structure while still lacking public inverse transport;
- and no current lane earns candidate-native identifiability closure.
