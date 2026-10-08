# Heartbeat publication boundary

```text
broad daemon options/result
          |
          | one exact mapping owner (3 option + 61 result fields)
          v
SyncDaemonHeartbeatPublication  [owning, frozen]
          |
          | validate exact value
          | classic-locale integer formatting
          | reject > 65,536 bytes
          v
heartbeat JSON bytes
          |
          | atomic file publication
          v
bounded reader using the same 65,536-byte constant
```

The codec cannot name the broad options/result types. The adapter depends on the codec;
the codec has no core back-edge. The publication is not authenticated authority; it is
a value boundary that makes validation and emission refer to the same state.
