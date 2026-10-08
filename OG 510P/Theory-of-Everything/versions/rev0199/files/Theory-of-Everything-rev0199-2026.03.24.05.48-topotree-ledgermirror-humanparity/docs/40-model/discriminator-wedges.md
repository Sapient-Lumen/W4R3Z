# Discriminator wedges

This document converts the invariant matrix into a **small set of wedges** that could actually change archive state.
A wedge is useful only if a positive or negative result would sharpen, merge, demote, or promote a bridge family. For broad stable / restart / program routing across bridge-family snapshots, the matrix, and wedges, use `docs/40-model/cross-family-pressure-router.md` rather than replaying those surfaces separately.

Read this together with:
- `docs/40-model/cross-family-pressure-router.md`
- `docs/40-model/invariant-matrix.md`
- `docs/40-model/observer-record-minimum.md`
- `docs/40-model/candidate-bridges.md`

## Minimal wedge format

Each wedge should say:
1. the exact pressure question,
2. what would count as real evidence rather than rhetoric,
3. and what archive state would change if the wedge lands.

## Record / observable audit by family

| Family | Where records currently live | What stabilizes them | What counts as observable content | Main unresolved gap |
|---|---|---|---|---|
| A — EFT-first gravity baseline | ordinary matter, apparatus, environment, detector chains | open-system dynamics, metastability, decoherence, coarse-graining | gauge-aware correlators, scattering data, detector events, semiclassical observables where valid | excellent baseline contact, but not a deep account of gravity microstructure or final diffeomorphism-aware observables |
| B — Thermodynamic / entropy gravity | usually imported from ordinary matter/environment or horizon bookkeeping | thermodynamic persistence and coarse-grained state variables | entropy, temperature, area/Noether-charge relations, effective geometric response | often uses record structure as an external input rather than deriving it |
| C — Holography / entanglement geometry | boundary degrees of freedom, encoded subregions, sometimes relational bulk reconstructions | entanglement structure, redundancy, code-like protection in best cases | boundary correlators, entanglement entropies, relational/bulk operators where defined | record/objectivity language is still too often borrowed from a classical cut or special dual settings |
| D — Measurement / nonlocality pressure | pointer states, environmental fragments, memory chains, downstream witnesses | decoherence, redundancy, repeated accessibility | persistent re-readable coarse-grained correlations and witness agreement | strong on empirical contact, weak as a standalone gravity/unification account |

## W-0001 — A vs B: does horizon entropy force dynamics beyond EFT bookkeeping?

- **Pressure question:** do Jacobson/Wald/Bekenstein style results genuinely reconstruct geometric dynamics, or do they mainly constrain how a low-energy theory must organize horizon thermodynamics?
- **Real evidence:** a derivation that makes its assumptions explicit and shows exactly where geometry enters, what counts as local equilibrium, and what is recovered beyond the EFT baseline.
- **Archive-state shift:**
  - if strong, B gains explanatory weight beyond being a clue;
  - if weak, A remains the honest baseline and B is demoted toward interpretive pressure rather than live derivation.
- **Current archive read:** `docs/40-model/thermodynamic-gravity-assumption-audit.md`, `docs/40-model/non-equilibrium-observable-record-map.md`, and `docs/40-model/family-b-beyond-equilibrium-gate.md` now land this wedge on the side of “live clue family with stricter admissibility, but still not a promoted replacement or a clean beyond-equilibrium explanatory winner.”

## W-0002 — B vs C: is entanglement geometry more than thermodynamic re-description?

- **Pressure question:** does entanglement-based reconstruction predict geometric structure that coarse thermodynamic language alone does not already capture?
- **Real evidence:** a clean case where entanglement-specific quantities do decisive work, not just a relabeling of entropy gradients or equilibrium conditions.
- **Archive-state shift:**
  - if yes, C remains distinct from B;
  - if no, B and C may be partly the same bridge family in different notation and should be merged or re-charted.
- **Current archive read:** `docs/40-model/rt-claim-audit.md`, `docs/40-model/entanglement-thermodynamic-surplus-audit.md`, and `docs/40-model/covariant-regime-stress-audit.md` now give a bounded yes-case: a partition-sensitive subregion geometry bridge survives beyond generic thermodynamic language and survives one disciplined covariant widening beyond static RT, but still only inside a special holographic regime.

## W-0003 — C vs D: are records explained or assumed?

- **Pressure question:** can a holographic or entanglement-first account specify where persistent, re-readable records live and how objectivity appears without quietly importing a classical observer split?
- **Real evidence:** an explicit statement of record carriers, stabilization mechanism, observable content, and limits of validity, all in the candidate's own language.
- **Archive-state shift:**
  - if strong, C improves on `INV-0008` and becomes more than geometry-plus-suggestion;
  - if weak, D remains an external pressure lane that C still owes.
- **Current archive read:** `docs/40-model/entanglement-admission-checklist.md`, `docs/40-model/rt-claim-audit.md`, `docs/40-model/covariant-regime-stress-audit.md`, `docs/40-model/family-c-stronger-reconstruction-audit.md`, `docs/40-model/family-c-witness-closure-gate.md`, and `docs/40-model/witness-borrowing-ladder.md` now provide a compact gate, multiple bounded family-C audits, an explicit `WB-2` placement, and a concrete future closure test; the result is still incomplete because stronger reconstruction sharpens the interface without yet turning boundary-borrowed record structure into candidate-native closure.

## W-0004 — Cross-cutting closure: what observables can become records?

- **Pressure question:** which relational or gauge-honest quantities can actually be written into persistent records inside the theory?
- **Real evidence:** a map from formal observable content to physical record carriers, not just a list of abstract operators.
- **Archive-state shift:** any candidate that cannot answer this stays below promotion, even if its geometry story is elegant.

This wedge is where `REF-0017` becomes load-bearing: observable language must stay tied to physically retrievable relations rather than float above record formation. Family B now carries a first bounded application of this demand in `docs/40-model/non-equilibrium-observable-record-map.md`, and `docs/40-model/witness-borrowing-ladder.md` now gives the shared score surface for whether either family is actually reducing that borrowing debt.


## W-0005 — Local law vs cosmological boundary: what is actually being explained?

- **Pressure question:** is a candidate deriving generic local dynamics, or does its apparent gain depend on a special global state, asymptotic boundary package, measure choice, vacuum selection, or horizon/ensemble setup?
- **Real evidence:** an explicit split between what is fixed and what is derived, plus a portability statement saying whether the gain survives outside the global package that made it visible.
- **Archive-state shift:**
  - if the split is sharp, fake explanatory wins are demoted and real local-law versus cosmological-package progress can be tracked separately;
  - if the split stays blurry, future revisions will keep laundering special global assumptions into generic local-law claims or vice versa.
- **Current archive read:** `docs/40-model/local-law-vs-cosmological-boundary-split.md` now installs this split in bounded form and keeps local-law credit and cosmological-package credit scored separately. The surviving local-measure residue is compressed canonically under `CL-0049` / `W-0006` and the audit stack rooted in `docs/40-model/measure-population-typicality-audit.md`; do not replay that closed lane inside `W-0005`.

## W-0006 — Record support versus raw throughput: what should observations track when the two come apart?

- **Pressure question:** if one regime carries thicker durable public rereadability while another carries higher gross entropy throughput, which side should the surviving local-measure lane favor?
- **Admissibility gate:** `W-0006` may count only when the archive's current support window, proxy family, xerographic family, nearby prior freedom, tail discipline, entry weighting, evidence floor, and objectivity requirement are held fixed tightly enough that the comparison isolates **record support versus throughput** rather than sneaking in a new package choice.

| Gate clause | When it applies | What `W-0006` may say | What it blocks |
| --- | --- | --- | --- |
| **Bite condition** | durable public redundancy genuinely thickens on one side while admitted gross throughput is higher on the other | favor the record-richer side over the merely throughput-richer side | blocks a raw-throughput default from pretending to be predictive closure |
| **Quiet condition** | both sides remain redundancy-thick and publicly rereadable | go mostly quiet; modest throughput differences no longer do the work | blocks treating every structured regime difference as a live discriminator |
| **Anti-smuggling condition** | calmness, longevity, or lower rewrite / disruption pressure improve without materially thickening durable public rereadability | stay quiet; those changes earn no extra force by themselves | blocks a generic preference for calmness, longevity, or low disturbance |
| **Reopen threshold** | a new benchmark yields either a quantified threshold-like relation / ordering magnitude, or a genuinely new bounded axis that changes archive state without reusing record-thickness, calmness, or rewrite-pressure surrogates already screened here | widen or sharpen the wedge again | blocks endless local casework that only restates the same bounded pattern |

- **Current archive read:** the first positive screen, aligned-structured negative control, nearby rewrite-pressure portability screen, and anti-smuggling calmness screen now collapse to one bounded rule: a structured record-richer regime can outrank a throughput-richer regime only when durable public redundancy is actually thicker; the wedge should go mostly quiet when both sides keep thick public records; and it should also stay quiet when calmer, longer-lived, or rewrite-lighter conditions do not materially improve public rereadability. That earns **weak bounded operational credit**, not quantified or regime-portable closure.
- **Stop rule:** do not add another local environment screen to `W-0006` unless the reopen threshold above is met. Matching reopen triggers belong in `ASSUMPTION-LEDGER.json` as `standby-threshold`, not as active next-move guidance.

## Promotion filter

No bridge family should be promoted by elegance alone.
A candidate needs, at minimum:
1. a low-energy recovery story,
2. a gravity/geometry story,
3. a record carrier and stabilization story,
4. an observable-content story,
5. and a statement of what would falsify or demote it.

## Immediate use

Use this document to route work toward **short audits** rather than long summaries.
- Open a wedge only when a positive or negative result would actually promote, demote, merge, or sharpen archive state.
- Treat `W-0006` as closed under `CL-0049`; this surface should name only the admissibility gate, stop rule, and reopen threshold rather than narrate a faux next move or global queue state.
- Route family-specific progress back to each wedge's cited canonical audit stack instead of restating closed history here.
