# Cube refactor audit rev0226

## Audit target

Rev0226 audits the machine-control layer rather than the policy content. The branch-family and
re-entry refactors in rev0224-rev0225 made the archive easier to enter, but the lint plane still had
an older shape: the orchestrator listed every check directly, and several validators inferred wiring
by searching that source file.

## Findings

| Finding | Risk | Treatment |
|---|---|---|
| `run_lint_suite.py` contained a growing hardcoded list of validators and generators. | A future check could be created but not run, while release records still look healthy. | Created `CUBE_TOOLCHAIN_REGISTRY.json`; refactored the runner to read it. |
| Validators used plain-text searches over `run_lint_suite.py` to decide whether controls were wired. | The meaning of "wired into lint" could drift after any runner refactor. | Updated those validators to read `CUBE_TOOLCHAIN_REGISTRY.json`. |
| Utility scripts and failing validators were not separated as first-class metadata. | Refactor audits could treat helper tools as missing controls or leave them unreviewed. | Added `utility_tools` coverage and a rule that every Python tool must be linted or declared utility. |
| Generated artifacts were known socially, not as a single machine list. | A canonical generated map could be omitted from release review. | Added a generated-artifact list with generator and check references. |

## Decision

The cube should treat the lint plane as part of the cube. A validator that protects a release claim
is not complete until it is discoverable, ordered, and covered by the toolchain registry.

## Non-changes

No historical branch files were moved. No real pilot data was imported. No `FT-0181` closure state
changed. No validator was removed; this pass changed how validators are registered and discovered.

## Next maintenance posture

Future refactor releases should prefer registry coverage, dependency clarity, and stale-link repair
over adding additional `FT-0181` gates. A new control still needs a named uncovered material risk;
otherwise rev0223's saturation rule remains the default.
