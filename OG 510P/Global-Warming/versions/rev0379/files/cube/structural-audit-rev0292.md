# Structural audit — rev0292

## Scope

Audited rev0291 and added a nuclear bankability/buildability refactor. The audit target was the gap between nuclear preference and actual delivery: finance, market design, offtake, long-lead procurement, construction controls, risk allocation and public-value safeguards.

## Findings

- Nuclear preference existed, but bankability and buildability were not first-class enough.
- Large loads/data centers were routed to nuclear grid/load matching, but not enough to capital-stack and public-value controls.
- Construction risk existed in delivery-risk language, but needed explicit long-lead component and project-control artifacts.
- Public finance and corporate offtake needed ratepayer/taxpayer/host-community safeguards.

## Actions

- Added files `444`–`448`.
- Added gates `NG_29`–`NG_40`.
- Added 22 service floors and finance/buildability tables.
- Rebuilt route/source/tag/scorecard/maturity/SQLite outputs.

## Validation

11 / 12 rev0292 validation rules passed.
