# Rev0806 lineage

## Byte-authoritative parent

- Revision: `rev0805`
- Archive:
  `AnonSync-rev0805-2026.07.16.15.34-falsegreen-hostileforge-selftestsplit-proofsurface.zip`
- SHA-256:
  `425f17c3bf5e93b230dff213a5acb030b45dfdf3bde1f3179f8fe138ce1a742c`
- Parent package verifier: **25/25 passed**
- Parent inventory: 1,125 files, 43 source C++ implementation files, 31
  source/public headers, and 28 test C++ files

The complete uploaded archive was extracted and verified before modification.
No object file, executable, build directory, recovered intermediate tree, or
other generated product was used as source lineage.

## Derivation

Rev0806 changes only first-party CMake, C++, private source headers, Python
audits, documentation, and revision evidence. The pinned SQLite 3.53.3 source
and every other third-party byte are unchanged from the parent.

The active code delta is preserved in
`SOURCE_DIFF_rev0805_to_rev0806.patch`. The normalized extracted-body proof in
`extraction/EXTRACTION_EQUIVALENCE.json` shows that after undoing explicit
private-bridge qualification, the moved 8,719-line selftest body differs only
where five unsigned fixture values gained checked conversion before entering a
signed CLI argument boundary.

`ACTIVE_IMPLEMENTATION_PROJECTION.json` binds the final CMake, source, headers,
tests, tools, fuzz sources, and third-party source. `MANIFEST.sha256` binds the
complete sealed package inventory.

## Revision intent

Rev0805 closed a false-green test gate and established a general runtime versus
selftest support library. Rev0806 follows through on the largest remaining
ownership defect: the domain-model corpus no longer shares the 24,531-line
runtime translation unit, and focused reporting wrappers no longer inherit that
corpus through a monolithic diagnostic target.

## Deliberate continuity statement

The revision advances exactly one step from the verifier-clean uploaded
`rev0805` package to `rev0806`. The parent filename and digest are retained
verbatim because the exact uploaded bytes, rather than an inferred repository
state, are authoritative.
