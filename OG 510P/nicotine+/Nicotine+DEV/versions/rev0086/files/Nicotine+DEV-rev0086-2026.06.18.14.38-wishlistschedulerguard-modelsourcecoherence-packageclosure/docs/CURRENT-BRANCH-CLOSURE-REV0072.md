# Exact-current supported-branch closure — rev0072

## Result

rev0072 converts the most important rev0071 uncertainty into a bounded current-source result.

The Nicotine+ security policy identifies `3.3.x` as the currently supported released series. During rev0072, the upstream `3.3.x` branch head was observed as:

```text
98089ac233aa57786e8dbdc48123f6ac1c4767d8
```

The worktree metadata inside the supplied source bundle records the identical commit for `github-branch-3.3.x`. This is an exact commit relation, not a marker-based similarity claim.

## Current-branch before/after gate

The gate uses the source bundle selected by content contract and runs two independent lanes of evidence:

1. Unpatched behavior lane: three existing witnesses must pass; each of the seven fixed-behavior regressions must return nonzero.
2. Patched clean-room lane: the four exported bundle patches must apply; all seven fixed-behavior regressions must return zero.

Observed result:

```text
existing witnesses                              3 / 3 pass
unpatched fixed-behavior expected failures      7 / 7 observed
clean-room patch files                          4 / 4 apply
patched fixed-behavior regressions              7 / 7 pass
patched touched files                           5 / 5 hashed
isolated upstream units, unpatched               58 passed, 1 skipped
isolated upstream units, patched                 58 passed, 1 skipped
```

The nonzero unpatched results are intentional. They establish that the proposed fixed behavior is absent at the exact current supported-branch head. Passing after patching establishes the before/after delta.

## What this closes

The earlier blanket statement “fresh current source is unavailable” is no longer accurate for `3.3.x`. The supplied lane is the current branch snapshot as of the rev0072 observation time because its commit identity exactly matches upstream.

This permits the seven packets to move from:

```text
archived-source only / current status unknown
```

to:

```text
fixed-behavior delta reproduced on exact current supported branch
```

## What this does not prove

- It does not independently establish exploitability or security severity.
- It does not prove that every proposed patch is the maintainers' preferred design.
- It does not replace public issue/PR overlap review.
- It does not establish full current-master equivalence.
- It is time-bounded to the upstream snapshot in `data/rev0072_upstream_ref_snapshot.json`.

## Master corroboration

The observed master head was `a96406e7aa285a3fb2a3e35900686d164a22bf02`, six commits ahead of the uploaded master lane. The public compare showed six commits and eight changed files. File histories at that head showed no strict touched file changed after the uploaded master snapshot:

```text
pynicotine/downloads.py      latest listed 2026-05-01
pynicotine/transfers.py      latest listed 2026-04-07
pynicotine/slskproto.py      latest listed 2026-06-06
pynicotine/search.py         latest listed 2026-02-25
pynicotine/slskmessages.py   latest listed 2026-06-06
```

This supports strict-surface continuity on master, but rev0072 labels it corroboration rather than exact-current runtime proof.

## Canonical outputs

```text
data/rev0072_upstream_ref_snapshot.json
data/rev0072_current_ref_ledger.csv
data/rev0072_current_unpatched_delta_matrix.csv
data/rev0072_current_patched_regression_matrix.csv
data/rev0072_current_packet_state.csv
data/rev0072_current_branch_closure_summary.json
evidence/rev0072-current-branch-closure-runtime/
tools/probe_rev0072_current_branch_closure.py
tools/probe_rev0072_upstream_unit_parity.py
docs/TEST-LANE-ISOLATION-REFACTOR-REV0072.md
```
