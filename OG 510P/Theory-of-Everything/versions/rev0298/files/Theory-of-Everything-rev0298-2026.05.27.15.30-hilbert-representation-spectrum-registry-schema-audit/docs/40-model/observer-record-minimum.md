# Observer / record minimum

This document gives the smallest cross-framework specification the archive will currently accept for **record**, **observer contact**, and **classical evidence trace**.
It is intentionally minimal. It does **not** claim to solve the full measurement problem.

For broad stable / restart / program routing across observer / record minimum, witness borrowing, and witness-package closure pressure, use `docs/40-model/empirical-contact-burden-router.md` rather than replaying those surfaces separately.

## Minimal record criteria

A physical record should satisfy all of the following.

1. **Distinguishability**
   - There is a coarse-grained difference between possible record states that can matter physically.

2. **Causal provenance**
   - The record is produced by an interaction history with some source system or process.
   - A “record” is not just an arbitrary labeling of a branch in prose.

3. **Persistence**
   - The relevant distinction survives for a nonzero time window under the dynamics of the host system or environment.

4. **Re-readability**
   - A later interaction can recover the same coarse-grained fact without requiring reconstruction of the full microscopic state.

5. **Backaction / thermodynamic cost**
   - Record formation is not free: it requires coupling, leaves traces, and should fit inside entropy/information bookkeeping.

## Stronger objectivity criterion

The archive treats **objectivity** as stronger than mere recordhood.
A record becomes objectively usable when the same coarse-grained fact is accessible through more than one downstream interaction channel or environmental fragment, so agreement is not encoded in a single privileged observer memory alone.

This stronger criterion is motivated by decoherence and environment-as-witness style reasoning. See `REF-0015` and `REF-0016`.

Cross-frame portability is weaker than full public objectivity. Multiple observers may successfully translate the same coarse-grained fact between frames while still borrowing a silent public comparison standard — for example a shared orientation, timing, calibration rule, or adequacy threshold. The archive now treats **public reference-standard closure** as the stronger condition that the standard of comparison itself is public enough for multi-observer use, rather than merely presupposed. See `docs/40-model/cross-frame-portability-vs-public-reference-standard-closure-gate.md`.

Public reference-standard closure is itself weaker than full diachronic evidence closure. A standard may be public at one time while still borrowing stable observer identity, calibration traceability, metadata provenance, or record-token reidentification across later rereads and successor devices. The archive now treats **diachronic witness-lineage closure** as the stronger condition that the same public evidence remains the same evidence through time, rather than only in one comparison episode. See `docs/40-model/public-reference-standard-vs-diachronic-witness-lineage-closure-gate.md`.

Diachronic witness-lineage closure is itself weaker than full **cross-site reproducibility closure**. A lineage may stay coherent within one laboratory, provider, or inherited instrument stack while still borrowing silent protocol transport, shared software, vendor conventions, or tacit operator skill that blocks independent reinstantiation elsewhere. The archive now treats **cross-site reproducibility closure** as the stronger condition that the same coarse-grained evidential claim survives across independently maintained sites or stacks rather than only inside one inherited chain. See `docs/40-model/diachronic-witness-lineage-vs-cross-site-reproducibility-closure-gate.md`.

Cross-site reproducibility closure is itself weaker than full **intervention-grade control closure**. Several sites may independently recover the same evidential claim while still borrowing one hidden actuation semantics, timing budget, feedback path, or control-stack culture, and without showing that the same coarse-grained evidential state can be deliberately written, steered, conditionally rerouted, stabilized, or erased across sites. The archive now treats **intervention-grade control closure** as the stronger condition that the same evidential state can be actively manipulated under public, transportable control and feedback rules rather than merely re-observed. See `docs/40-model/cross-site-reproducibility-vs-intervention-grade-control-closure-gate.md`.

Intervention-grade control closure is itself weaker than full **drift-resilient autonomy closure**. A lane may control a state skilfully across sites while still borrowing frozen calibration windows, continuous expert babysitting, stop-the-world recalibration, manual retuning, or one hidden maintenance ecology. The archive now treats **drift-resilient autonomy closure** as the stronger condition that the same control loop remains live through drift, recalibration, relocation, and long-horizon use rather than only inside a well-tuned episode. See `docs/40-model/intervention-grade-control-vs-drift-resilient-autonomy-closure-gate.md`.

Drift-resilient autonomy closure is itself weaker than full **public auditability closure**. A lane may keep control running for a long time while still borrowing opaque thresholds, hidden policy versions, private dashboards, or irreplayable intervention rationale rather than making the reasons for control decisions public enough for outside audit and contest. The archive now treats **public auditability closure** as the stronger condition that intervention rationale, decision context, and replay path are themselves public evidence rather than trusted operator lore. See `docs/40-model/drift-resilient-autonomy-vs-public-auditability-closure-gate.md`.

Public auditability closure is itself weaker than full **assertibility closure**. A lane may expose replayable decision provenance while still issuing categorical public claims without a publicly inspectable entitlement certificate, declared scope, or mandatory abstention state when support is insufficient. The archive now treats **assertibility closure** as the stronger condition that public claims are gated by challengeable warrants rather than post-hoc explanations alone. See `docs/40-model/public-auditability-vs-assertibility-closure-gate.md`.

Public assertibility closure is itself weaker than **public adjudication closure**. A lane may bind public claims to entitlement certificates, declared scope, and abstention semantics while still routing disputes through private inboxes, moving-target reruns, or informal review rather than a bounded public challenge path with fixed replay bundles and public terminal outcomes. See `docs/40-model/assertibility-vs-public-adjudication-closure-gate.md`.

Public adjudication closure is itself weaker than **public evidence-custody closure**. A lane may expose frozen replay bundles, challenge windows, and public terminal outcomes while still borrowing one host-controlled repository, silently mutable artifact store, expiring token path, or uncertified reference-object chain. The archive now treats **public evidence-custody closure** as the stronger condition that the decisive evidence bundle or reference artifact can be extracted, identity-checked, versioned, preserved, cited, and later reopened beyond one privileged host. See `docs/40-model/public-adjudication-vs-public-evidence-custody-closure-gate.md`.

Public evidence-custody closure is itself weaker than **fresh-host reinstantiation closure**. A lane may preserve evidence bundles, reference artifacts, and version chains very well while still borrowing the executable workflow object, stable software identity, environment recipe, or rerun-equivalence rule needed to rehydrate the evidential process on new infrastructure. The archive now treats **fresh-host reinstantiation closure** as the stronger condition that public custody extends to executable reenactment rather than to possession alone. See `docs/40-model/public-evidence-custody-vs-fresh-host-reinstantiation-closure-gate.md`.

Fresh-host reinstantiation closure is itself weaker than **independent implementation closure**. A lane may let outsiders rerun the preserved executable bundle on fresh infrastructure while still borrowing one inherited code lineage, one reference implementation, one under-specified semantic contract, or one untested equivalence rule rather than supporting genuinely separate implementations of the claimed evidential method. The archive now treats **independent implementation closure** as the stronger condition that the evidential process survives a public semantic reimplementation test rather than only a preserved executable rerun. See `docs/40-model/fresh-host-reinstantiation-vs-independent-implementation-closure-gate.md`.

Independent implementation closure is itself weaker than **independent evidence-generation closure**. A lane may support several conforming code lineages while still borrowing one frozen benchmark corpus, one inherited detector stream, one central evaluator, one reference simulator, or one single metrology chain rather than paying for separately generated records. The archive now treats **independent evidence-generation closure** as the stronger condition that the evidential class survives blind / holdout routes, interlaboratory comparison paths, or separately acquired / prepared record streams rather than only separate analysis of one inherited evidence source. See `docs/40-model/independent-implementation-vs-independent-evidence-generation-closure-gate.md`.

Independent evidence-generation closure is itself weaker than **candidate-native witness closure**. A lane may support blind / holdout routes, interlaboratory comparisons, or separately acquired evidence very well while still borrowing the actual record carrier, stabilization story, rereadability semantics, or objectivity side from ordinary laboratory witness structure rather than expressing those in its own bridge language. The archive now treats **candidate-native witness closure** as the stronger condition that those witness functions are carried in the candidate's own bridge variables rather than only in external lab-side prose. See `docs/40-model/independent-evidence-generation-vs-candidate-native-witness-closure-gate.md`.

Candidate-native witness closure is itself weaker than **candidate-native intervention closure**. A lane may express record carriers, stabilization, and reread paths natively while still borrowing the preparation recipe, trigger semantics, selective-update rule, or write / erase path from ordinary laboratory action language. The archive now treats **candidate-native intervention closure** as the stronger condition that the candidate's own bridge variables also represent experiment choice, preparation, update, and deliberate manipulation rather than only passive witness structure. See `docs/40-model/candidate-native-witness-vs-candidate-native-intervention-closure-gate.md`.

Candidate-native intervention closure is itself weaker than **candidate-native counterfactual closure**. A lane may express how one evidential path is prepared, triggered, selectively updated, and deliberately manipulated in native variables while still borrowing the menu of alternative probes, the sameness / difference criterion for interventions across branches or frames, or the contrastive outcome map for experiments of our choosing from ordinary laboratory or EFT-side language. The archive now treats **candidate-native counterfactual closure** as the stronger condition that alternative experimentally choosable interventions and their differential record commitments are represented in the candidate's own bridge variables. See `docs/40-model/candidate-native-intervention-vs-candidate-native-counterfactual-closure-gate.md`.

Candidate-native counterfactual closure is itself weaker than **candidate-native threshold closure**. A lane may express a native menu of alternative experiments, a native intervention-identity rule, and contrastive outcome commitments while still borrowing the decisive resolution scale, tolerance / coarse-graining map, uncertainty budget, bias rule, or under-resolution boundary from ordinary laboratory or metrology language. The archive now treats **candidate-native threshold closure** as the stronger condition that those evidential thresholds are also represented in the candidate's own bridge variables. See `docs/40-model/candidate-native-counterfactual-vs-candidate-native-threshold-closure-gate.md`.

Candidate-native threshold closure is itself weaker than **candidate-native identifiability closure**. A lane may express native resolution, tolerance, uncertainty, and under-resolution budgets while still borrowing the inverse map from thresholded public record classes back to candidate-level states, couplings, geometries, frame choices, or histories from ordinary tomography, model-selection, gauge-fixing, or empirical-equivalence language. The archive now treats **candidate-native identifiability closure** as the stronger condition that the candidate's own bridge variables also say which distinctions are learnable, gauge-collapsed, or empirically underdetermined under those native thresholds. See `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`.

Candidate-native counterfactual closure is itself weaker than full local public witness closure. A lane may express native records, native interventions, and a native menu of alternative interventions while still depending on ordinary laboratory infrastructure for the final public record ecology.

## Minimal vocabulary

- **Observer interaction**
  - any physical coupling that turns a prior uncertainty into a downstream, re-readable correlation structure.

- **Record**
  - a persistent, causally generated, re-readable correlation that can function as evidence.

- **Classical evidence trace**
  - a record whose coarse-grained content is stable enough to support ordinary empirical comparison across later interactions.

- **Objectivity**
  - not metaphysical certainty, but redundant or independently recoverable accessibility to the same coarse-grained fact.

## What this minimum is for

Future bridge claims should say:
- where records physically live,
- what stabilizes them,
- what counts as their observable content,
- and whether objectivity is primitive, emergent, approximate, or merely practical.

For the current family-by-family audit surface, see `docs/40-model/discriminator-wedges.md` and `docs/40-model/witness-borrowing-ladder.md`.

## Non-claims

This minimum does **not** by itself settle:
- why one outcome is experienced rather than another,
- whether decoherence is sufficient for definite outcomes,
- the status of Born-rule justification,
- or whether observer structure is fundamental or emergent.

It only blocks handwaving.
A candidate theory that cannot say how records become persistent and re-readable has not yet reached empirical closure.
