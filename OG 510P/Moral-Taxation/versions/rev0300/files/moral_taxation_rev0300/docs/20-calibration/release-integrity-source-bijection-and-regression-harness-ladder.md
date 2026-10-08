# Release-integrity, source-bijection, and regression-harness ladder

## Question in one sentence

How should a living moral-tax archive prove that each release keeps canonical surfaces synchronized, current-law sources fresh, golden cases executable, and calibration ladders distinct?[S594][S645][S646]

## Companion routes

Use this memo with:

- [`../10-framework/release-integrity-source-bijection-and-regression-harness-routing.md`](../10-framework/release-integrity-source-bijection-and-regression-harness-routing.md)
- [`../00-meta/golden-case-cards.md`](../00-meta/golden-case-cards.md)
- [`../00-meta/source-currentness-registry.json`](../00-meta/source-currentness-registry.json)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — prose-only release | update markdown and trust humans to notice drift | Reject for a datacube; prose is necessary but not sufficient. |
| B — manifest-only release | hash files but do not test semantic surfaces | Useful for reproducibility, not for route correctness. |
| C — source bijection check | require SOURCES.json, SOURCES.md, and citations to agree | Baseline release invariant. |
| D — executable golden cases | machine-readable cases with expected routes and failure modes | Required for regression testing. |
| E — generated canonical surfaces | render scorecard, source list, and coverage reports from one canonical layer | Preferred whenever markdown and JSON can drift. |

## Parameter ladder

1. **canonical-source rule** — Declare JSON or markdown canonical for each surface; generated outputs must be exactly reproducible.
2. **source-bijection invariant** — Every cited source ID exists in JSON and markdown; no duplicate URLs/titles; legal sources carry currentness metadata.
3. **scorecard sync invariant** — Markdown criterion IDs and thresholds must match scorecard-template JSON.
4. **cube coverage invariant** — Every calibration file has a cube route record or explicit exemption.
5. **golden-case invariant** — Golden cases are continuous, machine-readable, and include expected routes plus must-not-answer traps.
6. **distinct-ladder invariant** — New or watched ladders cannot reuse a generic shell above a similarity threshold without an intentional-template marker.
7. **new-route invariant** — Each new calibration route has cube record, sources, scorecard hook or reason, and at least one golden case.
8. **source-currentness invariant** — Volatile legal/operational sources record jurisdiction, status, effective date, last checked, review due, and volatility.
9. **manifest invariant** — MANIFEST hashes all files after generation and before packaging.
10. **review trigger** — Fail release on manifest mismatch, stale opening revision, source drift, uncovered calibration, scorecard drift, or golden-case failure.

## Default settings

| Parameter | Default | Redesign trigger |
|---|---|---|
| Canonical outputs | Generated where possible | Hand-maintained markdown diverges from JSON. |
| Coverage | All calibration files indexed | Selective cube with no exemption list. |
| Golden cases | JSON companion plus prose cards | Human-only examples that cannot catch regressions. |
| Currentness | Registry for volatile law/guidance | Current-law claims with no last-checked or review-due date. |
| Review cadence | Every release plus source-refresh triggers | Only manual spot checks. |

## Anti-pattern definitions

- **citation theater** — sources are numerous but not load-bearing, current, or bijective.
- **source surface drift** — SOURCES.json, SOURCES.md, citations, or source-currentness metadata disagree.
- **stale release opening** — public entry surfaces announce an older revision as current.
- **prose sprawl** — new files restate old rules without adding a distinct route, axis, case, or parameter.
- **unchecked case regression** — a golden case changes expected answer but no machine-readable test fails.

## Source IDs only

[S594][S645][S646]

[S594]: ../../SOURCES.md#S594
[S645]: ../../SOURCES.md#S645
[S646]: ../../SOURCES.md#S646
