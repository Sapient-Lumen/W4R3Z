# rev0071 cloudtainer waste / source-alias audit

```text
status: pass
source zip supplied: Nicotine-source(2).zip
source zip status: pass
payload files excluding generated rev0071 metrics: 2698
payload bytes excluding generated rev0071 metrics: 141784846
ranked audit queue files: 141
ranked audit queue bytes: 107805463
ranked audit queue share: 76.03%
exact duplicate groups: 247
exact duplicate wasted bytes: 6702488
```

## Largest top-level payload areas

- data: 1068 files, 121016103 bytes
- manifests: 181 files, 7650850 bytes
- evidence: 662 files, 6705835 bytes
- sources: 34 files, 2289727 bytes
- legacy_inputs: 11 files, 1922731 bytes
- tools: 83 files, 581612 bytes
- docs: 298 files, 562503 bytes
- handoff: 201 files, 553444 bytes

## Largest exact-duplicate groups

- 2151303 wasted bytes across 2 copies: data/rev0064_source_zip_entry_safety.json
- 1306278 wasted bytes across 2 copies: data/rev0064_source_zip_entry_safety.csv
- 660207 wasted bytes across 2 copies: data/rev0064_source_lane_file_manifest.json
- 352260 wasted bytes across 2 copies: data/rev0064_source_lane_file_manifest.csv
- 226220 wasted bytes across 2 copies: data/rev0044_manifest.json
- 206478 wasted bytes across 2 copies: data/rev0040_manifest.json
- 205142 wasted bytes across 2 copies: data/rev0041_manifest.json
- 180763 wasted bytes across 2 copies: data/rev0068_patch_semantic_inventory.json

## Interpretation

The cube is not source-heavy; it is evidence/history-heavy. The dominant payload is repeated ranked-audit-queue material, followed by exact copies duplicated between `data/`, `evidence/`, `manifests/`, `handoff/`, and `maintainer_artifacts/`.

rev0071 does not delete historical files. It creates a stable inventory and makes future compaction reviewable before removal.
