# Rev1012 research note

Direct allocator measurement showed that the ordinary completed source cache, not only its restart checkpoint, retained one heap allocation per chunk digest plus a second cumulative offset vector. A fixed-width cumulative record preserves exact range lookup and released wire semantics with one contiguous vector.

The next honest scale gate remains sparse synthetic multi-terabyte whole-process measurement: RSS, allocator fragmentation, page-cache pressure, checkpoint write amplification, restart replay, pulse throughput, transient wire materialization, complete scans, disk amplification, route latency, and controlled ENOSPC. A global or multi-source index remains unjustified before those measurements.
