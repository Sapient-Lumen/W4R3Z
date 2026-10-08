# Runtime evidence hygiene refactor — rev0081

## Severe package defect found during finalization

The unfinished rev0081 evidence tree preserved pytest's mutable temporary hierarchy inside the package. The measured lane contained:

```text
13 regular temporary files
21,333 regular-file bytes
9 pytest convenience symlinks
absolute symlink targets exposing an earlier /mnt/data work-tree path
```

These were test scratch rather than upstream source, but packaging them would leak local build topology, make the archive non-portable, and blur the distinction between durable evidence and disposable process state.

Four rev0080 evidence files had also been overwritten by a later rerun. They were restored byte-for-byte from the linked rev0080 archive before rev0081 validation.

## Correction

All current mutable lanes place HOME, XDG, TMP, and CWD under external disposable scratch roots. `purge_isolated_environment()` walks those roots without following symlinks, reduces every regular file and link target to a path/kind/size/SHA-256 row, and deletes the mutable tree. The cube retains only JUnit, ordinary logs, and the compact digest ledger:

```text
data/rev0081_search_rekey_environment_writes.csv
```

The final probe recorded 22 transient entries—13 regular files and 9 symlinks—across five lanes, then left zero transient directories or links in current package evidence.

`tools/audit_current_package.py` now rejects these names under the current revision's runtime-evidence root:

```text
cwd
home
tmp
xdg-cache
xdg-config
xdg-data
environment
pytest-of-root
source-states
```

The scope is deliberately current-revision evidence. Historical files remain immutable rather than being rewritten to satisfy a later convention.

## Negative control

A synthetic `tmp/wishlist.json` was inserted under current runtime evidence. The package audit failed only at the runtime-residue check, identified both the directory and file, and returned success after the mutation was removed.

```text
data/rev0081_runtime_residue_negative_control.json
evidence/rev0081-runtime-residue-negative-control.md
```

Runtime hygiene is therefore an executable archive invariant, not an informal cleanup promise.
