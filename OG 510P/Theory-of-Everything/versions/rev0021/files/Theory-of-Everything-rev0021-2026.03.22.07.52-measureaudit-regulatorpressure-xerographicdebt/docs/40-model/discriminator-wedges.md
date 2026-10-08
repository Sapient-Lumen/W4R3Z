# Discriminator wedges

This document converts the invariant matrix into a **small set of wedges** that could actually change archive state.
A wedge is useful only if a positive or negative result would sharpen, merge, demote, or promote a bridge family.

Read this together with:
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
- **Current archive read:** `docs/40-model/local-law-vs-cosmological-boundary-split.md` now installs the split in bounded form and closes the queue item that had left this distinction too slogan-level.

## Promotion filter

No bridge family should be promoted by elegance alone.
A candidate needs, at minimum:
1. a low-energy recovery story,
2. a gravity/geometry story,
3. a record carrier and stabilization story,
4. an observable-content story,
5. and a statement of what would falsify or demote it.

## Immediate use

Use this document to guide future revisions toward **short audits** rather than long summaries.
The next best move is not another survey. `W-0001` now has a first compact assumption audit in `docs/40-model/thermodynamic-gravity-assumption-audit.md`, a second-pass non-equilibrium witness discipline in `docs/40-model/non-equilibrium-observable-record-map.md`, a shared borrowing score in `docs/40-model/witness-borrowing-ladder.md`, a no-climb audit in `docs/40-model/family-b-witness-climb-audit.md`, and now a minimum beyond-equilibrium gain gate in `docs/40-model/family-b-beyond-equilibrium-gate.md`; `W-0002` now has a bounded control stack across `docs/40-model/rt-claim-audit.md`, `docs/40-model/entanglement-thermodynamic-surplus-audit.md`, `docs/40-model/covariant-regime-stress-audit.md`, `docs/40-model/family-c-stronger-reconstruction-audit.md`, and `docs/40-model/family-c-witness-closure-gate.md`; `W-0003` remains open on record closure, but future family-C progress now has to pass an explicit closure gate instead of reopening the same borrowed-interface promise; and `W-0005` now blocks boundary/package-locality smuggling before it can masquerade as a new explanatory gain.
