# GWTC md5 manifest anomaly custody audit

## Decision

rev0361 retains the compact GWTC-5 Zenodo v2 `md5sums.txt` checksum manifest locally as a custody/integrity map, not as a mirror of the bulky candidate-data payloads and not as route support. The retained file is:

`payload-snapshots/REF-0629-GWTC5-O4B-CANDIDATE-DATA/md5sums.txt`

The manifest row remains capped as acquired public-record custody only. No route score, evidence-unit score, empirical-delta authority, decision outcome, forecast realization, public-record credit, or observed-sector recovery state changes.

## What is materially new

rev0358 recorded GWTC-5 component md5s from Zenodo. rev0359 pinned the custody row to exact Zenodo v2 identity. rev0361 adds the compact integrity map itself and makes it executable under lint:

- local SHA-256: `f399f3272e76c5a0e8425850f855226b8e2e90cb4fcdab0356e65848e58b3efa`
- upstream component md5 for `md5sums.txt`: `b4cd957ad366580271f74c202bdd2e0a`
- retained byte size: `616644`
- retained line count: `4953`
- valid md5 entries parsed: `4952`
- declared upstream malformed lines: `1`

The retained manifest's valid component-entry extension counts are:

| Extension | Count |
|---|---:|
| `.fits` | 1657 |
| `.hdf5` | 1 |
| `.json` | 1657 |
| `.txt` | 301 |
| `.xml` | 1336 |

## Upstream anomaly handling

The official retained `md5sums.txt` file ends with one partial final line, `1e1801fb242d8d5a40bb`, which is not a valid `md5 filename` pair. Because the retained file's md5 equals Zenodo's file-listing md5 for `md5sums.txt`, rev0361 treats this as a declared upstream checksum-manifest anomaly rather than as local corruption.

That decision is intentionally narrow. Lint allows the anomaly only because `SOURCE-SNAPSHOT-MANIFEST.json` records the exact line number, line-content SHA-256, and reason. Any undeclared malformed line, changed malformed-line content, wrong malformed-line count, local SHA-256 drift, byte/line-count drift, or local file mismatch against a recorded upstream component checksum fails source-snapshot validation.

## Refactor boundary

`tools/source_snapshot_manifest.py` now distinguishes three checksum-manifest facts that used to be blurred together:

1. the local retained file identity, checked by SHA-256/byte-size/line-count;
2. the upstream component identity, checked by the source file's published md5/sha256 when present;
3. the semantic structure of the manifest, checked by per-line checksum syntax, safe relative paths, declared entry counts, optional extension counts, and exact declared malformed-line replay.

This is not registry expansion for its own sake. The point is to avoid the dangerous shortcut where a compact upstream integrity file is either trusted wholesale despite malformed content or silently cleaned into something that was never actually published.

## Negative replay

`tools/source_role_negative_replay_tests.py` now includes a declared-anomaly mutation case. It mutates the known malformed final line while updating the generic local SHA-256, byte-size, line-count, and matching upstream component md5 metadata. The source-snapshot evaluator must still fail on the declared malformed-line content hash. That proves anomaly custody is not merely file-hash custody.

## Next custody boundary

Further compact-retention passes should follow the same pattern: keep bulky payloads external, retain only small integrity/control files when useful, validate exact local and upstream identity, and refuse to normalize upstream anomalies unless the exact anomaly is declared and replayed.
