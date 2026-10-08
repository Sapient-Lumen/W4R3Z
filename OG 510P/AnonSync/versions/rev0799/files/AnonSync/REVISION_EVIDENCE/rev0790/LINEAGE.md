# AnonSync rev0790 lineage

Immediate parent: `AnonSync-rev0789-2026.07.14.23.34-rowstate-aliasproof-fuzzgraph-projectiontruth.zip`
Parent SHA-256: `31e3196dddddcf8355148c0ca39640e6c617e2496ec77a5de94b0db2a396b0ea`

The current release verifier passes all 25 checks against that parent archive.
Rev0790 changes 15 active files: three additions and twelve modifications. The
source-only inventory is `CHANGED_SOURCE_FILES.txt`, and the auditable unified
patch is `SOURCE_DIFF_rev0789_to_rev0790.patch`.

The parent active projection is 92 files / 14,719,184 bytes with SHA-256
`c6128ec0f2156922a56badc6170122de6957eb0132581a6b045e460103d78882`.
The current v2 projection is 96 files / 14,761,320 bytes with SHA-256
`e15ef38a5f481e4e8e5e1c98d1fff8f90b03927853272e7dcdf093f078a9c404`.

The semantic lineage is monotone: rev0789 established live-row and one-to-one
projection evidence; rev0790 reuses those checks and centralizes all production
SQLite scalar conversion so exact storage class and byte length are verified
before durable values acquire C++ authority. Historical evidence bytes are not
rewritten.

The final ZIP name and digest are freeze outputs and are deliberately external
to avoid a self-referential package hash.
