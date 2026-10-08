# rev0789 lineage

## Immediate supplied parent

`AnonSync-rev0788-2026.07.14.18.23-exact-vfs-uri-controlplane-lineagetruth-fenceforge(1).zip`

The archive has SHA-256 `02b1d020667224fa167c4dab705f933d59c8770f194db322ad64e6698cfdee7d`. The rev0789 verifier passes **24/24**
checks against it, including safe ZIP paths, one `AnonSync/` root, exact manifest,
CRC, required gate, and a recomputation of rev0788's legacy active projection.
The local `(1)` suffix is a download collision suffix, not a different project
revision.

Rev0788 itself records an inherited historical discontinuity: its intended
rev0787 ZIP was absent, so it anchored to a verified rev0786 archive plus an
explicit recovered rev0787 candidate. Rev0789 does not rewrite or conceal that
history; its immediate parent is the now-verified rev0788 package.

## Projection-version correction

Rev0788's `anonsync-active-projection-v1` digest is `27155873c3eca548628a73a8da230ba98f1c7e3b54e9bd0f1da25dc13f9ebf29` and covers 88
files. That legacy scope excluded the three files then under `fuzz/`.
Recomputed under the rev0789 v2 scope, the same parent bytes have digest
`d181e06574abcff8ee47897c64590356cf221178997ae1f97d40846a7eb410cb` and cover 91 files.

## rev0789 active implementation

`anonsync-active-implementation-projection-v2` includes `.gitignore`,
`CMakeLists.txt`, and all files under `include/`, `src/`, `tests/`, `tools/`,
`third_party/`, and `fuzz/`. Its tested digest is `c6128ec0f2156922a56badc6170122de6957eb0132581a6b045e460103d78882` across
92 files and 14719184 bytes. The legacy v1-compatible
digest of the current tree (excluding `fuzz/`) is `8c4a8d5212c966dbaba761e18b0db04c74e9524e0e394c9b799ef4500923c4a2`.

Active files changed or added relative to rev0788:

- `CMakeLists.txt`
- `src/persistence/sqlite_projection_decoder.cpp`
- `src/persistence/sqlite_projection_decoder.hpp`
- `tests/persistence/sqlite_projection_decoder_tests.cpp`
- `fuzz/fuzz_sqlite_projection_decoder.cpp` (new)
- `tools/verify_release_package.py`

README, revision notes, release gate, and rev0789 evidence are release metadata
and are bound by `MANIFEST.sha256`, not by the active implementation projection.
