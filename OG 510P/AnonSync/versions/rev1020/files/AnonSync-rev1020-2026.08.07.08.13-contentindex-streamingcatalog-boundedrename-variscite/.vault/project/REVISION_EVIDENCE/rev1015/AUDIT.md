# Rev1015 audit

Rev1015 removes the last string-backed digest frontier from in-progress content-defined source preparation. One maximum active source now retains one 327,680-byte vector of 8,192 fixed 40-byte records rather than 8,193 allocations and 860,160 requested bytes. Binary SHA-256 completion no longer creates a transient digest string.

The adjacent lifetime refactor publishes the bounded checkpoint candidate in place and releases a completed compact manifest only after terminal frame assembly, descriptor release, and exact durable-checkpoint reproof. Lost-response replay restores from that checkpoint without rehashing source bytes.

The 64-source fixture proves exactly 20 MiB of record storage and 64 vector allocations. It is not a whole-daemon RSS result and does not include SQLite, page cache, TLS, descriptors, directory scans, route buffers, allocator fragmentation, or backpressure.
