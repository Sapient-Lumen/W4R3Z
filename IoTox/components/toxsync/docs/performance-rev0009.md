# toxsync 0.6.0 / rev0009 performance and memory notes

Five GCC release runs used a 64 MiB basis, a 12,345-byte prefix insertion, 4,096 active objects,
page-cached host storage, and disabled benchmark fsync.

```text
profile                         12 peers        96 peers
availability representation     inline u32      2 x u64/object
scheduler resident median       295,424 B       362,992 B
availability storage            16,384 B        65,536 B
assignment median               3.807 M/s       1.706 M/s
content workspace               655,360 B       655,360 B
peak process RSS median         10,348 KiB      10,348 KiB
```

The dynamic profile therefore added 67,568 retained scheduler bytes for 84 more configured peers.
Its lower assignment rate is expected: candidate selection spans two availability words and a much
larger peer set. The likely dozen-computer deployment stays on the original compact hot path.

A synthetic resource profile requested 4,096 lanes, advertised 8,192, and applied transport,
in-flight, descriptor, command, and memory constraints. The decision was 4,096, limited by the
request. This proves only that the policy has no 32 ceiling; it is not a recommendation to open
4,096 Tox file transfers.

Real c-toxcore, relay, cold-storage, target-board, energy, and thermal results remain absent.
