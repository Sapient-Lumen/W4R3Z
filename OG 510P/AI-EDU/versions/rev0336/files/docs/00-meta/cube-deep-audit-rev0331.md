# Cube deep audit — rev0331

## Finding

The riskiest remaining defect after rev0330 was a second, quieter small-cell path. The structured
session summary was masked, but `FINAL-READOUT.csv` remained free text and was copied into
`MICRO-PILOT-RESULT.json` unchanged. That meant a careful operator could satisfy the formal
suppression rule and still leak `n=2`, `2/2`, a tiny percentage, or a small move-sample count through
the final narrative surface.

The defect mattered because final readouts are the artifacts people reuse in summaries. A leak there
is more dangerous than a leak in an internal scratch row.

## Refactor made

- The result recorder now redacts numeric/small-cell-sensitive final-readout fields before writing
  the result receipt.
- The receipt lists suppressed row/field coordinates without copying the suppressed values.
- The structured `session_summary` remains the only place where thresholded aggregates can appear.
- The allowed local decision row remains visible, but the decision is still not evidence.
- No new schema, validator family, evidence grade, registry, or public-claim layer was added.

## Waste corrected

This revision repairs an existing hot-path tool rather than adding more doctrine. The practical
operator behavior is now clearer: use `FINAL-READOUT.csv` for local owner review, but do not let its
free text become the exportable result surface when it contains exact small cells.

## Remaining risk

The project still lacks its first real educator/tutor contact and first real feasibility cycle. The
next field move remains human discovery, not another internal assurance layer.
