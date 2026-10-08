# Rev1008 research note

The source scheduler removes network-turn coupling but intentionally does not solve
restart cost or completed-manifest memory. A cold 4 TiB payload still requires 131,072
32 MiB local pulses, restart loses unfinished source projection work, and the completed
manifest and offset index remain O(chunk count).

The next scale experiment should measure sparse multi-terabyte payloads and large trees:
resident memory, allocator fragmentation, page-cache pressure, pulse throughput, owner
latency, restart loss, chunk-index rebuild, and controlled ENOSPC. A durable source
projection or paged manifest should be added only when those measurements identify the
dominant cost.
