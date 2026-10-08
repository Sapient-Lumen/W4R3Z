# Rev0848 repository hygiene

## Active projection

- active files: **267**;
- active bytes: **17,497,160**;
- active projection SHA-256: `f1aa2b2ebe6bc5cbeafad45ba07cf39dc745397c05a9e9ab9a6a9403594ec7e8`;
- changed active files: **11**;
- source delta: **+1,669 / -60**;
- bundled third-party files changed: **0**.

## Refactor effect

`SqliteBusyHandlerOwner` is a separately linkable persistence boundary rather
than another private helper inside `sync_peer_ingress_lifecycle.cpp`. The
callback no longer reaches the broad result document. A minimal lifecycle main
allows focused compiler and sanitizer builds to link only `anonsync_core_lib`,
while the registered CTest preserves CLI dispatcher coverage.

## Generated-artifact incident and correction

An intermediate `py_compile` invocation created `tools/__pycache__`, which was
correctly included by the active-projection algorithm and would have violated
the package verifier. It was removed before final projection generation. Final
evidence generation disables bytecode writes. No `.pyc`, object, archive,
executable, CMake build tree, VCS metadata, or symlink is included in the release
root.

The first Git evidence recipe also omitted untracked additions. The final patch
uses a fully staged parent comparison and was replayed on a fresh verified
parent tree. All **267** active files match exactly.

## Remaining cost centers

The active implementation is still dominated by very large domain and selftest
translation units, a long hand-maintained `CMakeLists.txt`, and a growing set of
lexical architecture audits. The focused driver is a useful local reduction,
but broader decomposition and generated registration data are still warranted.

Historical `REVISION_EVIDENCE` remains much larger than the active first-party
implementation and is recursively carried in release ZIPs. A content-addressed
external evidence store would reduce routine handoff cost while preserving
lineage, but this revision keeps the existing package contract unchanged.
