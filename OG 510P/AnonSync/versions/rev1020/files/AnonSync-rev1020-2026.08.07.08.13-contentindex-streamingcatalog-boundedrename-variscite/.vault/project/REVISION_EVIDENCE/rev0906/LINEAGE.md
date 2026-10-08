# AnonSync rev0906 lineage

Rev0906 is based on the uploaded rev0905 archive
`AnonSync-rev0905-2026.07.26.09.28-forensicstatus-filenamefamily-profileattestation-opalbridge(1).zip`. Its canonical family spelling is
`AnonSync-rev0905-2026.07.26.09.28-forensicstatus-filenamefamily-profileattestation-opalbridge.zip` and its SHA-256 is
`b773e651a1a4b4bf31cedb5e403d7c0e0f17d163f8d1d2db2323802935e8b8c7`. The current verifier passes that parent package **32/32**.

The imported archive contains no `.git` metadata. Rev0906 therefore does not
invent a source commit. The parent evidence retains its own declared
implementation commit `f733f6a9673cf23e4acd3f23521045686374ea4b`, but the rev0906 handoff is
normatively identified by three byte-addressed objects:

1. the exact parent archive SHA-256 above;
2. `CHANGESET.patch` SHA-256 `bba05aad92ea44ae9e38905e98f0f8cd27a681c7e8fd4d71211a0b712333a125`; and
3. active implementation projection v3 SHA-256
   `ac32cb7182ff3ba550cc39410041de96edaf651258f90ffcaac240a3a3d14e65`.

The changeset covers 10 changed non-evidence
paths (2 added and 8 modified),
with 1465 insertions and 180 deletions.
Applied to the exact parent source tree, it reconstructs all **731/731** package
files outside `REVISION_EVIDENCE/`, `RELEASE_GATE.json`, and `MANIFEST.sha256`
byte-for-byte and mode-for-mode.

Active projection v3 binds 470 active files and
21854536 bytes, including `cmake/` build authority. The projection
JSON itself has SHA-256 `d6caa833592c8eebda01b2081f96713cd681fb23fdef0ca45a4b8b6b6c81db15`.

Final directory and ZIP reports remain external to the archive because embedding
a report into the bytes it attests would change those bytes.
