# Strict/front handoff export index — rev0048

Rev0048 exports the seven production-gated packets into four minimized maintainer-facing folders. It does not promote new packets and does not embed source trees.

## Filing bundles

### `01-transfer-session-identity` — U-123 transfer-session identity

Single standalone packet. File this separately from broad upload-spoofing language.

Packets: U-123

### `02-peer-primary-election` — PB-01 peer primary-election compatibility

Single standalone packet. File separately from broad username/identity wording.

Packets: PB-01

### `03-search-response-source-admission` — FileSearchResponse source-admission series

Three related source-binding packets; submit as a series or coordinated review set.

Packets: SEARCH-RESP-01A, SEARCH-RESP-01B-BUDDY, SEARCH-RESP-01C-ROOM

### `04-search-response-parser-budget` — FileSearchResponse parser-budget series

Two related parser-budget packets; submit after/alongside source-admission only if maintainer wants parser hardening in the same cycle.

Packets: SEARCH-RESP-PARSE-BUDGET-A, SEARCH-RESP-PARSE-BUDGET-B

## Source boundary

The handoff folders are not a substitute for rerunning tests on a fresh checkout. The packaged cube remains bound to the external rev0003 source snapshot unless a newer snapshot is supplied.

## Verification

- `tools/probe_rev0048_handoff_export.py` verifies exported file hashes and required bundle structure.
- `evidence/rev0048-rev0047-preflight-rerun.json` records the inherited rev0047 preflight rerun against the external source bundle.
