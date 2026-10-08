# P0002-D008 runtime-gap / name-resolution audit — rev0032

Current head: `P0002-D008`  
Draft: `poems/P0002/draft_008.md`  
Packet: `poems/P0002/material/source_material_packet_008.json`  
Judged predecessor: `P0002-D007` / `revise_not_promote`

## Main risk addressed

`P0002-D007` had finally escaped datum numbers, but it became a clean source-defined metaphor. The riskiest unfinished work was not more packet coverage; it was whether the repeatedly failed live reach could become literary material without inventing a live reading.

## Change made

D008 keeps the Station Datum / first tide staff pressure and makes the local runtime gap visible in the poem body:

```text
In the cloudtainer,
I ask for latest water.

Name resolution failed.
```

The body contains no NOAA name, no datum table, and no numeric tokens. The packet carries exact source/API/runtime detail.

## Refactor

`tools/check_external_material_pressure.py` now supports `runtime_gap_policy.mode = local_runtime_gap_anchor`. The new guard requires body strings tied to the failed local attempt, requires disclosure strings that block live-value inference, checks a registered local runtime snapshot, and blocks body phrases that would imply a current value.

## Source basis

- NOAA Station Datum / first tide staff definition: `WEB-0116`, snapshot `SNAP-REV0032-STATION-DATUM-DEFINITION`.
- NOAA Marine Inspection Office tide gage/staff location: `WEB-0120`, snapshot `SNAP-REV0032-BENCHMARK-SUPERSEDED`.
- NOAA CO-OPS `date=latest` API scope: `WEB-0114`, snapshot `SNAP-REV0032-API-DOCS`.
- Local failed cloudtainer pull: `LOCAL-0006`, snapshot `SNAP-REV0032-LOCAL-LIVE-ATTEMPT`.

## Non-claim

This audit does not promote D008 and does not claim poem quality. It only records the literary risk taken and the validator guard added to prevent regression or live-data overclaim.
