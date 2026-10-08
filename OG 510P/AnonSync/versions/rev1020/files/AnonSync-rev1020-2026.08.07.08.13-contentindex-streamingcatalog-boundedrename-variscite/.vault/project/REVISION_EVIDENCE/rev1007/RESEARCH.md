# Rev1007 research note

This slice deliberately keeps the projection process-local. Every pulse reopens
and re-proves the digest-named payload, and a restart loses unfinished work. A
4 TiB source still requires 131,072 32 MiB pulses; the default 64-turn stream can
hash at most 2 GiB and the 4,096-turn hard ceiling at most 128 GiB. Same-stream
turn collapse removes repeated handshakes but not disk reads or scheduling cost.

The next scale experiment should compare a fair source-local background
scheduler with a conservative durable source/chunk index on sparse multi-TB
files. Either design must remain bounded, restart-conservative, rooted, and fair
across competing payloads.
