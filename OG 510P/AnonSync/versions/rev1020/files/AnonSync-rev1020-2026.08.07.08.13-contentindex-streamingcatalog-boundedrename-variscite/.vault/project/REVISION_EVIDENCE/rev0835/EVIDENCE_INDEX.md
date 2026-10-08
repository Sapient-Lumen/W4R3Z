# Evidence index — AnonSync rev0835

`EVIDENCE_INDEX.json` inventories every evidence file except the two index files themselves, avoiding a circular digest.

## Coverage

| Group | Files |
|---|---:|
| `audits` | 18 |
| `defect` | 4 |
| `inventory` | 2 |
| `lineage` | 3 |
| `root` | 15 |
| `validation` | 25 |

## Bound results

- Active projection: **211 files**, **16686958 bytes**, `ba1c35ae0d132a2762932faa3b40432fe8be6775e26ef32f867bc64e5c8fd4f5`.
- Source delta: **23 files**, **+2485/-602**.
- Source patch: `6b5435f70b6c459150f4ff49d7fcb36f74370012f28bc480c0a62e34f2828c40`.
- CTest: **122/122** in bounded final partitions.
- Structural audits: **277/277**.
- Focused runtime: **491/491**; stress **90/90 (nine targets repeated ten times)**.
- Focused ASan/UBSan: **9/9 built and executed after final WNOWAIT changes**; leak detection not claimed.
