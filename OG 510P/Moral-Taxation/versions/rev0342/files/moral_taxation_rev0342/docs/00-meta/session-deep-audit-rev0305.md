# Session deep audit — rev0305

Priority chosen: base/instrument/proof-posture synonym sprawl. After Rev0301 eliminated accountability placeholders and Rev0303 eliminated not-specific sentinels, the riskiest defect was not missing facts but unusable precision: three axes had hundreds of live values, most singletons.

## Findings

- `base`: 356 unique live values, 299 singletons.
- `instrument`: 344 unique live values, 266 singletons.
- `proof_posture`: 244 unique live values, 189 singletons.

The repeated failure mode was not conceptual richness. It was route-local phrasing occupying formal cube axes where controlled buckets would be more useful.

## Corrections

- Refactored live route records to controlled buckets for `base`, `instrument`, and `proof_posture`.
- Rebuilt declared axis values from live route usage plus case-contract requirements, so the cube does not keep dead vocabulary while still preserving executable test flags.
- Extended `tools/audit_axis_hygiene.py` with Rev0305 ceilings for all five compressed axes.

## Remaining risk

The next compression target is not another broad string sweep. The more important follow-up is route-memo compaction: now that actor-accountability profiles and cube axes are specific, repeated accountability-map prose in calibration memos can be shortened to references plus route-specific exceptions.
