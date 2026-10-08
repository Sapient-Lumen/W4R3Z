# Public-master exact-content lane — rev0085

## What changed

The cube no longer treats a public-web source review as though it were an
executed current-source lane. It now derives an executable tree for visible
public master `a96406e7aa285a3fb2a3e35900686d164a22bf02` from two independently
checked inputs:

1. the content-addressed bundled master proxy at
   `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`; and
2. the public compare delta across the six intervening commits.

The materializer verifies the base-tree inventory, exact changed-path set,
old and new full Git blob SHA-1 values for all eight changed files, delta
digest, final file count, byte count, and final tree inventory digest.

```text
base files:        776
base bytes:        17,402,957
target files:      776
target bytes:      17,403,681
target tree SHA-256:
6ec4de125694680a0231eda3bd7d95558a0eb8f02dcdd7e205d516f09b1735e7
```

This establishes the exact target **file content** represented by the pinned
base plus verified delta. It does not claim possession of an independently
obtained upstream Git commit object, signed tag, or release archive.

## Candidate composition

The public delta changes eight files. The current research candidate changes
six different files. Both application orders were executed:

```text
public delta -> current candidate
current candidate -> public delta
```

Both produce the same 776-file, 17,408,984-byte tree with inventory digest:

```text
2813a0e6e15f1dd91f9bd8eefdbe6b8112bd9f6db1016ed3380f12420e18ed98
```

The relationship is therefore source-backed and executable
`disjoint-commutative`, not merely inferred from path lists.

## Exact-head execution

The exact-content baseline and current-candidate lanes each report:

```text
60 passed, 1 skipped
pytest.main() returned: true
process exit code: 0
source writes: 0
source/environment cleanup: pass
```

`test_i18n.py` is explicitly excluded because `msgfmt` is unavailable.

## Authorities

```text
data/current_public_head_contract.json
data/current_patch_composition_contract.json
data/current_unit_lane_contract.json
tools/materialize_current_public_head.py
tools/audit_current_public_head.py
tools/audit_current_patch_composition.py
tools/run_current_unit_lane.py
```
