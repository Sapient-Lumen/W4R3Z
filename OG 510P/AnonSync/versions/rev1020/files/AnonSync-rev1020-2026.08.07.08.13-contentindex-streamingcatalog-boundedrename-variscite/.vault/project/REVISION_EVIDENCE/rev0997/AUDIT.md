# Rev0997 audit

Rev0997 keeps reconciliation protocol generation 7 wire-compatible while removing four avoidable page-sized ownership stages. The source appends one canonical response directly into the final frame, moves that allocation into bounded TLS continuation storage, and releases page vectors before network backpressure. The receiver validates payload fields as views into the retained frame and stages ordinary contiguous ranges directly from those views. Compatibility APIs remain explicit where an owned aggregate is still required.

The two allocation regressions bind complementary shapes: the 8 MiB source fixture permits one final-frame allocation plus bounded auxiliary work, while the 16 MiB receiver fixture requires one page-sized encode allocation, zero page-sized borrowed-decode allocations, and the expected owned-decoder copy differential. These are deterministic allocation-shape proofs, not 64 MiB or multi-terabyte peak-RSS measurements. Source payload objects and the final frame still coexist during encoding; OpenSSL and kernel buffers remain outside the oracle.

The adjacent audit corrected rev0996’s stale visible goshenite/20.48 labels to the actual sealed petalite/20.52 package already bound by its lineage and release gate. It also removed audit-created Python bytecode before recomputing the final 607-file active projection.
