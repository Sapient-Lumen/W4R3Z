# Rev1005 research note

This revision did not alter the wire generation or introduce a background scheduler. It applies the narrowest useful receiver-side optimization: exact-inode continuation under the existing global lease, a bounded local pulse, and an exact deferred-hash path after the pulse is spent. Multi-terabyte measurement remains the decision gate for moving the durable journal obligation into a receiver-local scheduler or prioritizing source-side manifest construction and a durable bounded chunk index.
