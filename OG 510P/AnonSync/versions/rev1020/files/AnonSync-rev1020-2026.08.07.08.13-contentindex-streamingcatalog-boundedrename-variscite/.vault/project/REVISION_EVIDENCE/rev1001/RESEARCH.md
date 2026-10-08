# Rev1001 research note

The retained design deliberately avoids an unbounded persistent chunk index. It trades repeated bounded source work for predictable memory and storage. A future multi-terabyte optimization may add a bounded durable fingerprint summary or generation-scoped index, but it must preserve exact inode reproof, final whole-file SHA-256 authority, selective-sync boundaries, and conservative invalidation when independently opened owners or other processes publish payloads.
