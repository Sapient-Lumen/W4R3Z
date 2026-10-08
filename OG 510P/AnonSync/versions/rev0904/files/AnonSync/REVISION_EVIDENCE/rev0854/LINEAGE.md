# AnonSync rev0854 lineage

Rev0854 descends directly from the sealed rev0853 archive:

`AnonSync-rev0853-2026.07.19.23.07-busysetterfence-slotnamespace-mutexatomic-raceproof.zip`

Parent archive SHA-256:

`6e202f7c60213954d0c496d27840ffff0dc5e0f1f3f0ff2c64edabbe21a44bc4`

The current release verifier accepts that archive at **26/26** checks and its
extracted `AnonSync/` tree at **22/22** checks. The rev0854 source patch applies
to that verified tree and reproduces all **279/279** active implementation files
exactly. The patch SHA-256 is recorded in `LINEAGE.json` and
`validation/source-patch-compare.json`.

The active implementation projection binds every root `.gitignore` and
`CMakeLists.txt` plus every regular file under `include/`, `src/`, `tests/`,
`tools/`, `third_party/`, and `fuzz/` by path, byte count, and SHA-256.
