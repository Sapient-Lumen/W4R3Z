# Rev1010 audit

Rev1010 makes source-side content-defined manifest preparation restart-durable
without introducing a global chunk index. The bounded private checkpoint binds
the exact store identity, retained causal operation, payload inode observation,
chunking parameters, rolling chunker state, resumable hashes, and completed
chunks. A fresh process can resume unfinished work and can reuse a completed
manifest without rereading payload bytes.

The adjacent audit corrected two concrete defects: inode replacement now revokes
an in-process durable frontier before comparing a lower valid successor, and a
failed final checkpoint publication is retried from peer-free owner discovery.
The retained record remains below 384 KiB and the existing 8,192-chunk frontier
covers the protocol's 4 TiB payload ceiling at the 512 MiB maximum chunk size.
Interrupted validation killed by a stale guard was excluded and all release
claims were reproduced on later authoritative GCC and Clang trees.
