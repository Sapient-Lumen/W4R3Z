# PRESSURE-CASES

This note records the compact concrete cases used to prune the hook layer in rev0009.

## PC-01 — traceable market timing is not just "accurate time"

Financial-timing sources keep pulling on:
- synchronization procedures
- verification at the destination
- continuous monitoring of UTC traceability

Effect on the archive:
- keep `traceability_posture`
- do not pretend ordinary applicability labels are enough for finance-facing evidence needs

## PC-02 — interference and holdover change recovery behavior

CISA guidance emphasizes that systems with resilient alternate timing often see minor or no degradation during interference, and that reacquiring the original signal may need to be delayed depending on holdover capability.

Effect on the archive:
- keep `holdover_class`
- treat holdover as more than a hidden implementation detail

## PC-03 — packet timing is pressured by asymmetry and known uncertainty

NIST power-profile and packet-timing material keeps surfacing:
- asymmetry as a degrading factor
- explicit compensation / monitoring behavior
- dependence on known uncertainty rather than vague confidence

Effect on the archive:
- keep `sync_dimension`
- resist replacing precision-network concerns with generic "better time" language

## PC-04 — restoration after loss is not the same as ordinary synchronization

Resilient-architecture material suggests that calibrated links can help resynchronize nodes after loss or restoration, but not always with ordinary confidence or accuracy.

Effect on the archive:
- keep `rejoin_marker`
- keep `locality_scope`
- do not treat recovery from isolation as merely another normal regime transition

## Archive judgment

These cases did **not** justify a larger core.
They justified a smaller, more selective hook layer.
