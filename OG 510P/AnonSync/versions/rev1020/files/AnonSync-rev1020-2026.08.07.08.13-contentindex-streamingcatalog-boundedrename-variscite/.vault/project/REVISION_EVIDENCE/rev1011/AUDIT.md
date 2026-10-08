# Rev1011 audit

Rev1011 compacts the one bounded restart-durable source-manifest checkpoint
introduced by rev1010. Each completed chunk is represented in process by one
64-bit extent and one fixed 32-byte SHA-256 array. The checksum-framed v2 wire
image, rooted payload authority, publication cadence, exact inode proof,
restart scheduler, and ordinary protocol manifest are unchanged.

A sealed-rev1010 allocator probe measured 8,192 allocations and 532,480
requested bytes after reserving a maximum 8,192-record vector, and 8,193
allocations / 860,160 requested bytes to copy it. The retained rev1011 test
requires zero post-reserve construction allocations and one contiguous
327,680-byte allocation for the copy. Exact active, complete, and maximum
wire-image lengths and SHA-256 values remain byte-for-byte compatible with
rev1010.

The adjacent refactor preserves move ownership at the conversion boundary:
the fresh completion path decodes each existing hexadecimal digest into the
compact checkpoint and then moves that same string into the ordinary protocol
manifest. The loop intentionally remains mutable; making it const would restore
an 8,192-string copy. This revision does not claim solved whole-process RSS,
cold multi-terabyte hashing, ordinary completed-manifest memory, or a global
chunk index.
