# Rev1011 research note

This revision is driven by direct allocator measurement rather than a new
index design. At the bounded 8,192-chunk checkpoint frontier, heap-backed
hexadecimal digests create thousands of small allocations even though the wire
record already stores binary SHA-256. Matching the in-process representation to
the existing wire shape removes that fragmentation without widening authority.

The next source-scale gate remains sparse synthetic multi-terabyte measurement
of whole-process RSS, the ordinary completed manifest and offset index,
allocator fragmentation, page-cache pressure, checkpoint write amplification,
restart replay, and owner-turn latency. A global or multi-source chunk index
should not be added before those measurements identify it as the limiting
product edge.
