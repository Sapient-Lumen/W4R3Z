# rev0783 lineage decision

## Declared parent rejected

The filename-declared predecessor was:

`AnonSync-rev0782-2026.07.14.23.55-process-bound-sqlite-handle-slot-forkauthorityforge.zip`

SHA-256: `e3cb6a38dd064b7e8298999a8da9f12eac49144124bb1c5a0bc6ca7d86a3d8f2`

The ZIP is structurally readable, but it contains only 50 files and has zero
C++ implementation files, zero headers, zero tests, no `CMakeLists.txt`, and no
README. Its embedded `RELEASE_GATE.json` identifies rev0782 and sets
`required_gate_passed` to false. `tools/verify_release_package.py` rejects it.
It is retained as evidence, not treated as a source parent.

## Verified code parent

Rev0783 was reconstructed from:

`AnonSync-rev0778-2026.07.14.01.57-thread-incarnation-mutex-lifetime-sentinelforge.zip`

SHA-256: `f05bfad00aed87e16e2636bb27a294aa5ad61a3487f808ac99118d6afdd777f2`

That archive contains 307 files, including 46 C++ implementations, 22 headers,
12 C++ tests, a complete CMake project, and a required release gate marked
true. ZIP CRC verification passed before extraction. The extracted tree was
committed locally as the immutable comparison baseline
`a49e2ea rev0778 verified full-source parent`.

## Meaning of the rev0783 delta

`SOURCE_DIFF_rev0778_to_rev0783.patch` is the auditable source delta. Rev0783 is
not claimed to be a byte-for-byte descendant of the source-less rev0779–rev0782
artifacts. Ideas mentioned by those artifacts are credited only where this
revision independently contains source, tests, and validation evidence.
