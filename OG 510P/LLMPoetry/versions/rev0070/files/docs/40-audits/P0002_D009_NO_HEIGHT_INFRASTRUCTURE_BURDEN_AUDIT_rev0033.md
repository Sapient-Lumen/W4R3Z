# P0002-D009 no-height / infrastructure-burden audit — rev0033

Current head: `P0002-D009`  
Draft: `poems/P0002/draft_009.md`  
Packet: `poems/P0002/material/source_material_packet_009.json`  
Judged predecessor: `P0002-D008` / `revise_not_promote`

## Main risk addressed

`P0002-D008` made the local runtime gap visible, but it also made the infrastructure failure too legible: cloudtainer, host, DNS, and path vocabulary began to dominate the poem's surface. The risk was not insufficient traceability. The risk was that the poem would become a clever error-message lyric with good receipts.

## Change made

D009 keeps the Station Datum / first tide staff anchor and the failed live reach, but compresses the infrastructure burden out of the poem body. The body no longer says `cloudtainer`, `host`, `DNS`, `NOAA`, `API`, or `date=latest`. It says:

```text
I asked for today's water.

The name did not resolve.

No value came back.
No wet number.
```

The receipt layer still carries the exact local failure and the API scope. The poem body carries only the absence pressure.

## Refactor

`tools/check_external_material_pressure.py` now supports `infrastructure_burden_policy.mode = runtime_gap_infrastructure_burden_cap`. The new guard caps infrastructure diction in the poem body, requires place/water anchors, and preserves the no-live-reading disclosure in packet space.

The same checker was also corrected so historical runtime-gap packets do not have to keep their local snapshots marked as supporting the current head. Earlier packets remain valid history; only the current-head runtime packet must point to a current-supporting local runtime snapshot.

## Source basis

- NOAA Station Datum / first tide staff definition: `WEB-0116`, snapshot `SNAP-REV0033-STATION-DATUM-DEFINITION`.
- NOAA Marine Inspection Office tide gage/staff location: `WEB-0120`, snapshot `SNAP-REV0033-BENCHMARK-SUPERSEDED`.
- NOAA CO-OPS `date=latest` API scope: `WEB-0114`, snapshot `SNAP-REV0033-API-DOCS`.
- Local failed cloudtainer pull: `LOCAL-0007`, snapshot `SNAP-REV0033-LOCAL-LIVE-ATTEMPT`.

## Non-claim

This audit does not promote D009 and does not claim poem quality. It records a literary compression attempt and a validator guard intended to prevent return to infrastructure overexposure or live-data overclaim.
