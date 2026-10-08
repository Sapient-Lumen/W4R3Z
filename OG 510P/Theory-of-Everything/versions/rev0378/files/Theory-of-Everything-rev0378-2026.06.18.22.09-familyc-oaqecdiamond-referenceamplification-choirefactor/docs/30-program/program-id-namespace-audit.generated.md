# Program ID namespace audit (generated)

Generated from workstream, bridge-experiment, and research-frontier surfaces. Do not edit directly; run `make index` after changing program surfaces.

## `WS` namespace

- Source: `docs/30-program/workstreams.md`
- Unique IDs: `72`
- Duplicate IDs: `0`
- Missing IDs inside observed range: `0`
- Current max: `WS-0072`

## `BR` namespace

- Source: `docs/30-program/bridge-experiments.md`
- Unique IDs: `62`
- Duplicate IDs: `0`
- Missing IDs inside observed range: `0`
- Current max: `BR-0062`

## `RF` namespace

- Source: `docs/30-program/research-frontiers.md`
- Unique IDs: `62`
- Duplicate IDs: `0`
- Missing IDs inside observed range: `0`
- Current max: `RF-62`

## Audit rule

Program IDs are lightweight routing handles, but they should be unique. Duplicate WS/BR/RF IDs hide which workstream or bridge owns an obligation. rev0287 repairs the duplicated rev0286 WS/BR IDs and stale RF pointer, and makes future drift visible.
