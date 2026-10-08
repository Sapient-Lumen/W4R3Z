# rev0072 evidence index — exact-current supported branch

The external source bundle selected by SHA-256 contains a `github-branch-3.3.x` head equal to the upstream branch head recorded in `data/rev0072_upstream_ref_snapshot.json`.

Canonical results:

```text
source contract                         pass
exact current 3.3.x ref match          pass
existing behavior witnesses            3 / 3 pass
unpatched fixed-behavior deltas         7 / 7 observed
clean-room patch files                  4 / 4 apply
patched fixed-behavior regressions      7 / 7 pass
patched touched-file hashes             5 / 5 present
isolated upstream unit suite            58 passed, 1 skipped (both states)
active numbered source-alias dependency 0
package hygiene                         pass
```

The unpatched fixed-behavior tests are expected to return nonzero. Their successful rows mean the absence of each proposed behavior was reproduced before patching.

Machine-readable summaries:

```text
data/rev0072_current_branch_closure_summary.json
data/rev0072_current_packet_state.csv
data/rev0072_upstream_unit_parity_summary.json
```

Raw outputs:

```text
evidence/rev0072-current-branch-closure-runtime/
evidence/rev0072-upstream-unit-parity-runtime/
```

Revision-delta integrity:

```text
data/rev0072_delta_inventory.csv
handoff/rev0072/MANIFEST.sha256
```
