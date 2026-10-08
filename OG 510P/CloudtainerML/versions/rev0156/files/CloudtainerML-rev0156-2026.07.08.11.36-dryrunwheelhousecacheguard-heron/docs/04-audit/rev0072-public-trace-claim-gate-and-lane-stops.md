# rev0072 — public trace claim gate and lane stops

rev0071 produced a stop signal for support reuse: safe certificates were still slower than dense/fresh histogram, while raw reuse was fast but invalid. rev0072 converts that into two executable protections:

1. **Public trace claims require provenance.** A schema-valid external NPZ is no longer enough to claim public/pretrained evidence. The gate now requires a manifest that matches the trace hash and rules out local tiny/surrogate/random-weight origin.
2. **Dead-end lanes are machine-paused.** Recent measured results are converted into a lane decision matrix so the default next work moves to actual public/pretrained trace capture and named-hardware/fused-kernel replay.

## Contract result

- Flag-only `--public-pretrained-trace` claim: rejected.
- Fixture-origin manifest: rejected.
- Schema-only external trace: loaded as external, not public/pretrained.
- Oracle leakage rows in the contract probe: `0`.

## Lane decisions

Paused or retired as next-default work:

- raw anchor support reuse — fast but invalid;
- certified support reuse — safe but slower;
- boundary-refined selector — fixes over-selection but remains slower;
- deployable score-only selector/layout on local CPU — computes all QK and loses end-to-end.

Highest-priority continuation:

1. capture/import actual public pretrained trace bundle with provenance manifest;
2. replay that bundle through QK/native dispatch/value-layout audits;
3. run named-hardware or fused-kernel timing.

This is not a promotion revision. It is a waste-prevention and claim-boundary repair.
