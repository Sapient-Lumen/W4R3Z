# Rev1015 research note

The engineering question was whether the active source projection still needed heap-owned hexadecimal digests and whether a completed source manifest had to remain resident after terminal delivery. It needed neither. A fixed 32-byte digest value is the correct internal owner, and the exact durable checkpoint is sufficient to restore the compact manifest after a lost terminal response.

The synthetic 64-source fixture is deliberately an allocator-boundary proof rather than a process benchmark. The next scale decision should be made from whole-process concurrent-share RSS, page-cache, checkpoint-write, restart-replay, and ENOSPC measurements.
