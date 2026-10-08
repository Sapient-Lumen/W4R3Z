# Audit — rev0967

Rev0967 makes the bounded owner causal-version inventory completely browsable. The owner can bind a query to one canonical path, choose a page size from 1 through 1,024, and continue after the exact active superseded operation at the previous page tail. Missing, malformed, visible, or out-of-path cursors fail closed. Every page remains an independent observation carrying its own replica generation, visible-state digest, and payload-snapshot digest.

The adjacent complexity audit found that rev0966 bounded response storage but not model work: global inspection performed a whole-model path lookup for each active operation, while long same-path histories selected visible heads through pairwise candidate comparisons. Rev0967 performs one sorted traversal of borrowed operation pointers, groups each path once, aggregates maximum causal coverage per actor, and tests each operation dot once. A 258-operation differential regression binds the optimized result to the public pairwise definition.

The first refactor accidentally introduced `std::function` at the public causal-model boundary. The complete registry caught that architectural regression. The final interface is a compile-time borrowed visitor with non-executable private projection helpers, and a non-copyable visitor regression proves callbacks are neither copied nor type-erased.

A speculative protocol-generation-3 branch was rejected and removed. Metadata-only transfer of a superseded operation was not crash-safe under operation-ID page ordering: a partial pull could make the predecessor temporarily visible without any remaining obligation to transfer its payload. Protocol generation 2 and operation-before-bytes remain intact until durable staging or causally safe ordering exists.

Mechanical evidence binds a 20-file binary-aware patch reconstructed 20/20 against sealed rev0966, the 568-file active projection, 227/227 structural checks, all 258 GCC registry tests, independent 39/39 GCC product tests, focused 386-check folder-owner, 113-check local-control, and 98-check network-model suites, a fresh 238-edge Clang ASan/UBSan product graph, and all 39 sanitizer product tests without a retained diagnostic.

The boundary remains narrow. This is deterministic causal browsing of bytes that happen to remain retained. It is not a wall-clock timeline, retention promise, version pin, quota, garbage collector, conflict-copy policy, batch or directory restore, rename identity, GUI, or protocol for peers missing deliberately collected old payloads.
