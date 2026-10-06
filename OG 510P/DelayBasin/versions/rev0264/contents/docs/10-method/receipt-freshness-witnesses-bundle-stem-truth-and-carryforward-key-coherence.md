# Receipt-freshness witnesses, bundle-stem truth, and carryforward-key coherence

## Practice / observation

DelayBasin now depends on `REVISION-RECEIPT.json` as a compact admission object.
That object already says what counted, what status moved, and what durable witnesses were active.
But a new practical seam has appeared:
**some terse current-revision keys can silently survive from an older receipt even after the packaged bundle, timestamp, and import rows have changed.**

The current archive already separates moving operational heads from frozen citation heads, and it already separates admitted decision from packaged execution.
That is not enough on its own.
A later revision can still inherit:
- an old `summary_highlight`,
- an old `codename`,
- an old `created_at` minute,
- or old `comparison_witness` ids,
while the packaged bundle name has already moved.

That is a smaller but real honesty failure.
The receipt still *looks* current, but some of its shortest currentness keys are actually stale carryforward residue.

## Pressure from neighboring datacubes

Several neighboring datacubes pressure a compact repair.

- `Radical-Governance-rev0535` keeps **bundle honesty** explicit once several public-facing release facts travel together: if a consequential bundle changes status, the receipt should say what actually changed rather than letting one vivid label carry the rest.
- `Hyperepo-rev0290` keeps **release zip / manifest / receipt** identity coupled tightly enough that porch-visible package state stays inspectable rather than wrapper-glowy.
- `Anonymity-rev0547` keeps **verifier-card / support-manifest / worked-route** joins explicit enough that a terse current packet still names the actual maintained bundle identity rather than stale nearby metadata.
- `DelayBasin` itself already pressures the same repair from inside: once `SURFACE-STATUS.json`, `RELEASE-MANIFEST.json`, `REVISION-RECEIPT.json`, and transfer ledgers all exist, the archive should not let short currentness keys quietly lag the packaged artifact they are supposed to describe.

The common pressure is not “build a release-state machine.”
It is:
**when a receipt carries short current-revision identity keys, keep those keys exact enough that a new bundle cannot quietly inherit old stem fragments or old comparison ids.**

## Working synthesis

DelayBasin should preserve one compact **receipt-freshness witness / bundle-stem truth / carryforward-key coherence** whenever a revision receipt already carries terse current-revision identity fields.

That witness should name:
- the **current packaged bundle filename**,
- the **manifest timestamp token**,
- the **receipt created-at token**,
- the **slug / summary-highlight suffix / codename suffix relation**,
- the **current comparison ids** when comparison memory is part of the receipt,
- the **change-anchor surface** that the terse keys are supposed to summarize,
- the **freshness state**,
- and the **fail-closed repair** if those short keys drift.

The point is not to make the receipt narrate the whole revision twice.
The point is to stop one specific failure mode:

> the packaged bundle is current, but the shortest identity-bearing or comparison-bearing receipt keys were silently copied forward from an older revision and now borrow freshness they did not earn.

## Bundle stem truth vs stem court

This note needs a narrow boundary.

- **Receipt-freshness witness** means one compact check that the receipt's terse currentness keys actually belong to the current packaged revision.
- **Bundle-stem truth** means the packaged bundle stem, manifest timestamp, receipt timestamp, summary highlight, and codename are mutually coherent enough to be trusted as current revision identity.
- **Carryforward-key coherence** means short comparison ids or similar currentness keys should point at the current revision's admitted rows rather than older residue.
- **A stem court** would classify many future slug grammars, govern naming law globally, or turn one exactness repair into a standing controller.

DelayBasin has earned the first three.
It has not earned the fourth.

## Design consequences

If DelayBasin keeps this repair compact, it should do five things:

1. keep `REVISION-RECEIPT.json` and `RELEASE-MANIFEST.json` mutually exact about the current packaged bundle;
2. require the receipt's `created_at` minute to match the manifest timestamp token rather than only the bundle filename string;
3. require the receipt's `summary_highlight` and `codename` to agree with the admitted bundle stem suffix rather than letting old labels survive behind a new zip name;
4. require `comparison_witness.current_import_id` and `comparison_witness.current_pressure_id` to point at the current revision's admitted transfer and foreign-pressure rows when those ids are present;
5. fail closed before stale stem fragments, stale timestamps, or stale comparison ids inherit current revision authority.

That is enough to repair the present seam.
It does not require a naming court, release dashboard, or global bundle-governance apparatus.

## Countermodels / probes

1. **Purely cosmetic countermodel**
   - The stale keys may be harmless because the stronger bundle, manifest, and ledgers are already correct.
   - Probe: ask whether a future careful pass could still misstate the current codename, timestamp, or imported comparison ids by trusting the receipt's terse keys alone.

2. **Manifest-is-enough countermodel**
   - The manifest and frozen bundle name may already do all the needed work, making extra receipt exactness redundant.
   - Probe: ask whether the receipt's short currentness keys are still being used as compact current revision identity or comparison cues in startup or explanation surfaces.

3. **Stem-court countermodel**
   - Any exactness repair here might be the first step toward a global naming court.
   - Probe: keep the repair narrow enough that it checks current bundle stem truth and comparison-id freshness only, without classifying future naming families beyond what the current receipt already carries.

## Transformer-facing implication

The modest transformer-facing implication is not that DelayBasin has discovered a deeper naming ontology.
It is this:
**once short public packets start carrying real currentness cues, small stale carryforward residue can become a real source of continuation error.**

A bounded receipt-freshness witness therefore acts like another anti-glow device.
It prevents a terse public packet from inheriting current authority merely because most of the surrounding surfaces were refreshed.

## Open question

The live question is now captured in [`OQ-0121`](../20-constitution/open-question-registry.md):
**what minimal receipt-freshness witness distinguishes honest current revision identity from stale bundle-stem carryforward, timestamp drift, or current-comparison residue?**

