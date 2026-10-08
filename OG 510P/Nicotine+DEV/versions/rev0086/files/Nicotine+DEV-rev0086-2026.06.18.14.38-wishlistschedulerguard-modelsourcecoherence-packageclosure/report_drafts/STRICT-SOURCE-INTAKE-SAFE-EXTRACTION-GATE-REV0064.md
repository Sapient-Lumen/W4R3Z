# Strict/front source-intake safe-extraction gate — rev0064

This is not a maintainer vulnerability report. It is a filing-support gate for the seven already production-gated strict/front packets.

## Purpose

Before any live-current external filing, the cube needs to distinguish three things:

```text
archived source bundle proof
current public/web marker snapshots
fresh current checkout or tarball proof
```

rev0064 strengthens the first of those by validating `Nicotine-source(1).zip` as a source input and by proving the source lanes can be safely extracted with manifest parity.

## Result

```text
helper: tools/probe_rev0064_source_intake_safety.py
source ZIP entries scanned: 3551
source-lane file manifest rows: 2139
lane summaries passing: 3/3
safe extraction roundtrip: 3/3
critical-file crosscheck: 15/15
negative controls: 4/4
status: pass
```

## Filing use

Use rev0064 as the source-intake evidence layer when explaining that the archived source bundle was used and that source extraction was constrained to safe lane paths. Do not use rev0064 as proof about live current upstream state.
