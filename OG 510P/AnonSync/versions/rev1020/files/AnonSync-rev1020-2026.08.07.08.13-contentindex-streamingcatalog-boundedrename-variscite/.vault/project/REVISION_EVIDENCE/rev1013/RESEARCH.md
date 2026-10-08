# Rev1013 research note

Allocator instrumentation separated the retained compact-cache improvement from the remaining cache-cold publication cost. Rev1012 had already reduced retained state to one fixed 40-byte record per chunk, but materializing or receiving the released wire manifest still allocated one heap string for each of 8,192 digest texts. A strict 32-byte value preserves canonical validation and exact hexadecimal serialization while moving the entire sequence into one vector allocation.

The next honest scale gate is process measurement, not another representation claim: sparse multi-terabyte files and trees should be exercised under RSS, allocator, page-cache, restart, throughput, disk-amplification, selective-sync, concurrent-share, and ENOSPC instrumentation. The remaining single-manifest sequence is bounded and materially smaller, but it is not constant memory and does not establish a whole-device budget.
