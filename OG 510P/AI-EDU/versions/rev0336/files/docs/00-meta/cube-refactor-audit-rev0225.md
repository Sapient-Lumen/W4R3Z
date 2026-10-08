# Cube refactor audit rev0225

## Audit question

Rev0224 fixed duplicated re-entry lists. Rev0225 asks what else makes the cube hard to maintain even when lint passes.

The answer is the branch-history tail: `docs/20-governance` contains many valid but highly specific historical branch surfaces, especially hot-exam continuation surfaces. They are not wrong, but they make the governance directory look more canonical than it is.

## Findings

| Finding | Evidence | Risk |
|---|---:|---|
| Branch-history concentration | 100 detected branch surfaces. | Maintainers may create another sibling branch instead of using compression or terminal disposition. |
| Single-family dominance | `hot_exam_recipient_followup_shells` has 50 surfaces. | The hot-exam tail can dominate scans of the whole governance layer. |
| Path-migration cost | Branch files are referenced by archive index, surface map, history, receipts, and narrative surfaces. | Moving them physically would add churn and risk broken historical links. |
| Retrieval gap | The archive had `SURFACES.json`, but no branch-family lens. | A maintainer could find an individual file without seeing its family or compression rule. |

## Refactor actions

1. Added [`BRANCH_FAMILY_INDEX.json`](../../BRANCH_FAMILY_INDEX.json) as a generated branch-family map.
2. Added [`branch-family-index-and-refactor-map.md`](branch-family-index-and-refactor-map.md) as the human-readable scan layer.
3. Added `tools/gen_branch_family_index.py` and `tools/check_branch_family_index.py`.
4. Wired branch-family generation and validation into the lint suite.
5. Updated the surface-map generator so branch-history rows receive the `branch-archive` tag and `branch_archive` lifecycle.
6. Added the branch-family map to the compact re-entry route without restoring long branch-history lists.

## No path-migration decision

The audit did not justify moving files. The safer refactor is to index them, tag them, and make new branch creation harder. A physical migration can happen later only if there is a concrete retrieval failure that the family index cannot solve.

## New invariant

A new `first-*`, `portable-*`, or `late-relapse-*` governance file should be exceptional. The maintainer must be able to name the family it extends, the compression rule it could not use, and the material pattern that justifies another branch.

## Residual debt

The index is rule-based. It is good enough for scan and anti-sprawl control, but some individual family assignments may deserve hand-curation after repeated use. That is a maintenance task, not a blocker for this release.

## Speculation

The cube is now near a productive maintenance plateau. The next meaningful progress is still likely either real `SRC2+` pilot evidence for `FT-0181` or a targeted hand-curation pass over the largest branch family after someone uses the index in practice.
