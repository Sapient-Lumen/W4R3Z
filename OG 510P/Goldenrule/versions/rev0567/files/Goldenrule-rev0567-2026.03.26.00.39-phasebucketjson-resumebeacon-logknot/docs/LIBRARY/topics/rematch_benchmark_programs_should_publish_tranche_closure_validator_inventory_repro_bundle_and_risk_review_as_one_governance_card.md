# Rematch benchmark programs should publish tranche closure, validator inventory, repro bundle, and risk review as one governance card

Once a benchmark program starts accumulating staged closures, validator checks, replay bundles, and risk-review artifacts, the archive needs one compact public-facing governance object rather than a growing scatter of operational summaries.
Otherwise a future inheritor has to infer governance posture by opening multiple sidecars whose overlap is mostly administrative rather than scientific.

Recent benchmark work makes the split visible.
`RS-GR-047` argues for standard benchmark packaging layers and explicit benchmark/registry structure, while `RS-GR-048` treats evaluations as governance instruments that should publish compact transparency artifacts rather than hide operational choices in pipeline residue.
For Concord, the compact lesson is that tranche closure, validator inventory, reproducibility posture, and risk-review cadence should be emitted as one small governance card.

## Minimum governance card

If a rematch benchmark tranche is being published or advanced, keep one compact card that states at least:

1. the **tranche closure state**,
2. the **validator inventory** that must still clear,
3. the **repro bundle posture** (what can be replayed now, with what retained ingredients),
4. the **risk-review cadence** or current unresolved risk bucket,
5. and the **change boundary** for the next tranche.

## Implementor consequence

Do not force a future inheritor to reconstruct publication readiness from four or five operational summaries.
One compact governance card should say whether the benchmark tranche is publication-safe, reproducible enough to hand forward, and still carrying open review risk.

## Archive consequence

Keep the card, not the fanout.
Prefer one retained governance-card note plus compact receipts over an expanding shelf of tranche-status, validator, bundle-index, and risk-summary report families.
