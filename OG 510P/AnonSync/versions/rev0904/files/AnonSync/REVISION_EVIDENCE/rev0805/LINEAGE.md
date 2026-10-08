# Rev0805 lineage

## Byte-authoritative parent

- Revision: `rev0804`
- Archive:
  `AnonSync-rev0804-2026.07.15.20.58-sourcefirst-schemapin-callbackfence-focusgraph(1).zip`
- SHA-256:
  `ddc449742935aaf6345ca8821dd61f631defb857cdf209fd3e458bb58f621b70`
- Parent package verifier: **25/25 passed**
- Parent inventory: 1,090 files, 42 production C++ files, 30 production
  headers, 28 test C++ files

The uploaded archive was extracted to a clean source directory and verified
before modification. No build product, recovered executable, object file, or
unverified intermediate tree was used as source lineage.

## Derivation

Rev0805 changes only first-party C++, headers, CMake, Python audits,
documentation, and revision evidence. The bundled SQLite source and other
third-party bytes are unchanged from the parent.

The source delta is preserved in
`SOURCE_DIFF_rev0804_to_rev0805.patch`. The active implementation projection
binds the resulting CMake, source, header, test, tool, fuzz, and third-party
source inventory. `MANIFEST.sha256` binds the complete final package inventory.

## Revision intent

Rev0804 established source-first ownership transfer, callback fences, exact
schema owner-generation pins, and a focused schema boundary. Rev0805 does not
replace or weaken those invariants. It repairs the proof gate around them,
restores two drifted hostile-database diagnostics, and removes test support from
runtime consumers and the runtime API.

## Deliberate continuity statement

The revision number advances from the verified uploaded `rev0804` artifact to
`rev0805`. The parent filename includes the upload disambiguator `(1)`; that
suffix is retained in lineage metadata because the exact uploaded bytes, not a
normalized filename assumption, are authoritative.
