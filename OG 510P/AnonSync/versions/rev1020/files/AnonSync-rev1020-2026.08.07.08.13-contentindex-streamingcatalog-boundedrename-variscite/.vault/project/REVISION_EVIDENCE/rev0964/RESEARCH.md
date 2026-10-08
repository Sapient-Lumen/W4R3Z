# Research notes — rev0964

The design is intentionally conservative about directory enumeration. Ordinary POSIX directory iteration is not a point-in-time namespace snapshot, so a count from one pass cannot safely authorize absence after later passes observe a changed membership. Rev0964 therefore treats the first census as a finite work fence, not as a durable snapshot, and turns observed post-census growth into an explicitly incomplete segment.

The selector optimizes the concrete memory cliff rather than pretending to solve huge-tree scanning. Selecting the next K bytewise-smallest names with a bounded max-heap is O(N log K) comparisons and O(K) retained names per pass; it may repeat O(N) enumeration for later batches. A future durable subtree/change-sequence index can remove repeated prefix work, but only after its crash, rename, deletion, and watcher-loss semantics are specified as carefully as the current completed-epoch fence.
