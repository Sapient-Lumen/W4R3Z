# Native crash-ledger GC

Crash-ledger GC separates soft profiling cleanup from hard native fault memory.

rev0088 makes active native faults sticky:

- hard faults cannot be dropped;
- quarantine/fallback/crash evidence must be preserved;
- insufficient retention budget causes a hold, not deletion;
- clean soft evidence can be compacted;
- GC proposals are previous-linked and fork/replay checked.

The aim is to prevent a restart or cleanup pass from rediscovering a bad native artifact as if it were fresh.

The active code is `src/i2p_dht_lab/nativecrashgc.py`.
