# Exact public-head composition authority — rev0085

## Result

Rev0085 closes the source-distance qualifier that constrained rev0077–rev0084.
The supplied source cube contains master commit
`f4e17d59783dbc48ea31d2e899a681e2dd1ed500`. The visible public master head on
2026-06-18 is `a96406e7aa285a3fb2a3e35900686d164a22bf02`, six commits later.

The cube now materializes the target as **exact file content** by applying a
pinned eight-file public delta to the content-addressed bundled base. Every old
and new changed file is checked against its complete Git blob SHA-1, and the
full resulting inventory is checked against a declared digest.

```text
base tree:       776 files / 17,402,957 bytes
base digest:     d6fe257512f7fc3dc965d3d4ac39bd99eab9eb8703722bfa99d7f46d98b6dcbd

target tree:     776 files / 17,403,681 bytes
target digest:   6ec4de125694680a0231eda3bd7d95558a0eb8f02dcdd7e205d516f09b1735e7
```

This establishes exact target-tree bytes. It does not pretend that the cube
contains an independently downloaded Git commit object, signed archive, or
fresh upstream checkout.

## Candidate composition

The public delta changes eight paths. The rev0085 Search Again candidate changes
six different paths. The target sets are disjoint.

The composition audit applies both layers in both orders:

```text
bundled base -> public delta -> candidate
bundled base -> candidate -> public delta
```

Both orders apply cleanly, reverse-check cleanly, and produce the same complete
inventory:

```text
composed tree:   776 files / 17,408,984 bytes
composed digest: 2813a0e6e15f1dd91f9bd8eefdbe6b8112bd9f6db1016ed3380f12420e18ed98
relationship:    disjoint-commutative
```

This is stronger than saying that the candidate's target files were not listed
in the intervening commit summaries. It is executable composition evidence.

## Exact-head regression lane

The baseline and cumulative candidate were each run in a separate disposable
materialization of the exact public-head file-content tree:

```text
baseline: 60 passed, 1 skipped
candidate: 60 passed, 1 skipped
```

`test_i18n.py` is explicitly excluded because `msgfmt` is unavailable. Native
GTK, desktop-shell, and Win32 notification behavior remains untested and keeps
the Search Again packets open.

## Machine authority

```text
data/current_public_head_contract.json
data/current_patch_composition_contract.json
data/current_source_contract.json
data/current_unit_lane_contract.json
tools/materialize_current_public_head.py
tools/audit_current_public_head.py
tools/audit_current_patch_composition.py
tools/run_current_unit_lane.py
```

The derived source tree is never packaged. Only contracts, compact digests,
patch layers, logs, JUnit records, and audits are retained.
