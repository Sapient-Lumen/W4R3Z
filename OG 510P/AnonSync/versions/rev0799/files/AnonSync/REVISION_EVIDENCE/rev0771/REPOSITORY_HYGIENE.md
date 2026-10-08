# Repository hygiene audit — rev0771

- Source-tree files scanned: **148**
- Source-tree bytes scanned: **19,224,865**
- Files at least 5 MB: **1**
- Generated/build artifacts found inside the recovered source tree: **0**
- Revision/ZIP artifacts found inside the recovered source tree: **78**
- Exact duplicate groups (files ≥1 KiB): **2**
- Estimated exact-duplicate excess bytes: **324,265**
- Potential credential patterns: **4**

The machine-readable inventory is in `repository_hygiene.json`. Duplicate identity does not prove that deletion is safe; generated artifacts and nested revision archives are excluded from rev0771 packaging, while source and test fixtures are preserved. The long-term correction is to keep immutable release evidence outside the active source tree and regenerate build products from manifests instead of copying them forward.
