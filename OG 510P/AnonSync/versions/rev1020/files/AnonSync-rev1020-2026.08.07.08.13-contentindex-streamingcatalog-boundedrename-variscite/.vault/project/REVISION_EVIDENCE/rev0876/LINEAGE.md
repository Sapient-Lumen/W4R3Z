# AnonSync rev0876 lineage

- Parent revision: `rev0875`
- Parent archive: `AnonSync-rev0875-2026.07.22.03.01-timenscapability-unknownquarantine-ambiguousdelivery-cloudseal.zip`
- Parent archive SHA-256: `af723216a4ee86b7acd0f08ac900a2de5dc94461ddc8ae6383dd3bb2499572c5`
- Working-tree base commit: `f04ae382833ec1e0d54da4b9dd6270f4c633071d`
- Source patch: `CHANGESET.patch`
- Source patch SHA-256: `c7990feea090fb529fec245ed70188ce34b5688404ea3e39bf1cce663da7b6ad`
- Patch paths: 24 non-evidence text paths
- Final active projection: 352 files, 19103147 bytes
- Final active projection SHA-256: `359a8f3f8061f92c5aa2d974a59a709f57cbb46e4d9216ce9d4a08ec06c07200`
- Active delta: 21 paths (9 added, 12 modified, 0 removed)

The projection uses the verifier's v2 active set: `.gitignore`,
`CMakeLists.txt`, and all files under `include/`, `src/`, `tests/`, `tools/`,
`third_party/`, and `fuzz/`. Its digest is SHA-256 over sorted lines of the form
`<file-sha256>  <path>\n`.

The patch excludes revision evidence, `RELEASE_GATE.json`, and
`MANIFEST.sha256` to avoid recursive metadata. The final package manifest binds
those release artifacts separately.
