# Rev0976 audit — divergent lineage, checked i64, and regex low-memory re-entry

## Highest-risk finding

Two substantive rev0975 archives diverged from rev0974. The user-linked lineage contained Linux regex-child memory containment; an unpublished sibling contained checked signed-64-bit execution. Publishing either over the other under the same revision would silently discard safety work and make the archive name unreliable.

Rev0976 preserves the linked rev0975 semantics and merges both code lines under a new revision. Git ancestry, revision notes, and package lineage now make that repair inspectable.

## Substantive correction retained: regex peak memory

A CPython regex can finish inside the foreground deadline while allocating hundreds of MiB of native repeat state. The shared finite-timeout child therefore keeps one central 144 MiB post-request headroom default. Linux children lower soft and hard `RLIMIT_AS` after decoding the owned request and before compile/match; allocation failure is a stable `memory-limit` operation and each new request receives a fresh process. Exact substitution geometry is denied before source slicing or output materialization.

## Substantive correction integrated: executable i64 contract

The data model promised signed 64-bit integers while the Python oracle used arbitrary precision. Normal plugin arithmetic could therefore amplify inside one primitive beyond host fuel, fail late in the allocator, and consume operands. Source literals, `to-int`, bytecode JSON, mutable bytecode objects, arithmetic, compiled execution, and plugins now reuse one non-boolean signed-64-bit boundary. Decimal scanning never accumulates beyond the target magnitude. Arithmetic inspects before commit, preserving operands on overflow and zero division. Constant indexes reject Python negative-index semantics.

The portability corpus pins Micromax floor division and paired remainder. Rust/Wasm ports must implement that observable rule instead of using ordinary truncation-toward-zero signed division.

## Audit/refactor

The integration review found two small re-entry weaknesses in the regex protocol. Python booleans could be coerced to one-byte budgets, and the low-memory exception path rebuilt a response mapping before choosing prebuilt bytes. Parent parsing is now centralized and rejects booleans before spawn; the child rejects boolean numeric limits; both the memory-failure mapping and wire envelope are built before request limits are installed.

The checked-i64 re-entry review rejects JSON booleans, host-injected bignums, mutable oversized constants/operands/spans, and negative/past-end constant indexes at import, export, and dispatch.

## Waste removed

- no second revision meaning under one filename;
- no accidental “i64 in docs, bignum in execution” model;
- no allocate-then-reject integer conversion;
- no pop-before-failure arithmetic;
- no per-surface regex memory options, numeric registry, bignum mode, or new worker;
- no threaded-parent `preexec_fn`.

## Residual risk

The regex ceiling begins after request decode, is Linux virtual-address-space policy rather than portable RSS/cgroups, and does not isolate syscalls or crashes. Checked i64 does not bound strings, collections, opaque host values, generic equality, map-key behavior, native calls, total heap, or interpreter compromise. The next isolation decision should start from one real plugin/editor failure transcript.
