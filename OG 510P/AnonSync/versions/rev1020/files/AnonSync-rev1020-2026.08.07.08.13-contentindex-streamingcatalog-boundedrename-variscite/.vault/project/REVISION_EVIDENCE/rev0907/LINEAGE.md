# AnonSync rev0907 lineage

Rev0907 is based on the exact rev0906 archive `AnonSync-rev0906-2026.07.26.21.24-boundedsessions-causaldispatch-pressurestop-opalcurrent.zip`. Its SHA-256 is
`0a7ccd4ee7663cd68408654250b4873644ffd7a1df145153e47fe3d491cf9872` and its size is 19119428 bytes. The current verifier passes
that parent package **32/32**.

The imported archive contains no `.git` metadata. Rev0907 therefore does not
invent a source commit. This handoff is normatively identified by three
byte-addressed objects:

1. the exact parent archive SHA-256 above;
2. `CHANGESET.patch` SHA-256 `8ad01f8b76d35aeb0ad95f06ef439840dcaa1c2077fd084307168544f24b8bbf`; and
3. active implementation projection v3 SHA-256 `82e36c01d64cce2af3c686381d5083ab55a84b7c30376c17a1b256bfc2cf9a8a`.

The changeset covers 16 changed non-evidence
paths (5 added and 11 modified),
with 2409 insertions and 312 deletions.
Applied to the exact parent source tree, it reconstructs all **736/736** package
files outside `REVISION_EVIDENCE/`, `RELEASE_GATE.json`, and `MANIFEST.sha256`
byte-for-byte.

Active projection v3 binds 473 active files and
21927208 bytes, including CMake build authority. The projection JSON
itself has SHA-256 `415e6a853ad7f658d2b205ab0b8e9684e95229baa9779a84c7c2e68f2bb6c6a0`.

Final directory and ZIP reports remain external to the archive because embedding
a report into the bytes it attests would change those bytes.
