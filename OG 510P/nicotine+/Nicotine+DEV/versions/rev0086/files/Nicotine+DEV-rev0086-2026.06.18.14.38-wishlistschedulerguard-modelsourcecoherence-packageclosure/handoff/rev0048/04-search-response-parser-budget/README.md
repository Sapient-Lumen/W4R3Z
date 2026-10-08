# FileSearchResponse parser-budget series — rev0048 handoff export

Two related parser-budget packets; submit after/alongside source-admission only if maintainer wants parser hardening in the same cycle.

This folder is a minimized maintainer-facing export assembled from the full cube. It intentionally avoids embedding the external upstream source tree. Use the root cube helpers with the separate `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z` source bundle for reruns.

## Contents

- `reports/` — maintainer report and selected fix skeletons.
- `patches/` — selected patch diffs or apply helpers needed by the packet/series.
- `tests/` — fixed-behavior regression artifacts.
- `evidence/` — compact rerun/source-trace evidence needed for review.
- `MANIFEST.sha256` — per-file digest list for this handoff folder.
