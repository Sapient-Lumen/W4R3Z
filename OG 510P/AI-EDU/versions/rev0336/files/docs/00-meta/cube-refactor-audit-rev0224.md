# Cube refactor audit rev0224

## Audit question

Rev0223 deliberately saturated the `FT-0181` control plane. The rev0224 audit asked a different question: what part of the cube is now too hard to re-enter, duplicated, stale, or over-enumerated even though the underlying controls pass lint?

## Findings

| Finding | Evidence from the rev0223 tree | Risk |
|---|---|---|
| Re-entry duplication | `README.md` repeated 26 local link targets; `START_HERE.md` repeated 20. | Maintainers can read the same control list twice and still miss the intended path. |
| Numbering drift | `START_HERE.md` had repeated ordered-list numbers around the control-plane section. | A human reviewer may think a path is shorter or differently ordered than it is. |
| Stale surface overview | `surface-map-overview.md` still described the rev0213 overlay even after the rev0220-rev0223 control-plane layers. | The map looked comprehensive but explained an older operating state. |
| Startup overload | `context-pack.json` carried a very long startup path that mixed canonical surfaces with branch-history tails. | Re-entry prompts become bulkier without improving first-decision quality. |
| Control-plane discoverability | The controls were valid but scattered across release candidate, audit, assurance, coverage, refresh, quorum, invariant, dependency, delta, drill, saturation, maintenance, custody, and claim surfaces. | Future work could add another control because the existing one is hard to find. |

## Refactor actions

1. Added `reentry-navigation-map.md` as the single compact path map.
2. Rewrote `README.md`, `START_HERE.md`, and `AGENTS.md` to delegate navigation instead of restating long lists.
3. Refreshed `surface-map-overview.md` for the rev0224 state.
4. Shortened `context-pack.json` generation into a tiered startup path rather than a branch-heavy list.
5. Added `check_reentry_navigation.py` to catch duplicate local links, missing gate language, and context-pack path overload.

## No-control-expansion decision

This release does not add a new `FT-0181` control artifact. The audit found navigation and re-entry debt, not an uncovered import risk. Under the control-saturation rule, a new pre-import control would be inappropriate without a named material gap.

## Residual debt

The largest remaining refactor opportunity is the hot-exam branch archive. Moving the branch-history tail into a dedicated subdirectory could make `docs/20-governance` easier to scan, but it would also create heavy path churn across `ARCHIVE_INDEX.md`, `SURFACES.json`, historical references, and release audit examples. That should wait until there is a concrete retrieval or maintenance failure, not merely aesthetic discomfort.

## Speculation

The next useful deep pass is probably not another validator. It is either:

- a real `SRC2+` pilot import, if a source packet arrives; or
- a branch-archive migration plan with compatibility redirects, if maintainers repeatedly fail to find non-hot-exam governance surfaces.

Until then, the cube should prefer maintenance, evidence refresh, and navigation hygiene over new gates.
