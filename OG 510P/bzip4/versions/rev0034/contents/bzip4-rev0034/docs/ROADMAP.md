# bzip4 durable roadmap after rev0034

## Priority law

```text
90% compatible compression/decompression speed and binary operability
 8% bounded memory, concurrency, and Datacube admission policy
 2% ratio preservation / jackpot-only research
```

Final size is always measured, but a modest ratio loss is acceptable when it
buys a large, repeatable speed gain under the same memory limit. A feature that
slows either direction is presumed rejected unless it closes a mandatory safety
or compatibility gap.

Each session's cubes are a rotating target cohort. They are discovery and
external-validation data, not permanent semantic training data. Promotions
must survive a later unseen session.

## Immediate work, ranked

1. **Controlled current-libsais branch.** Import a precise current revision,
   re-audit every local bzip3/bzip4 safety patch, and compare old/new BWT and
   inverse-BWT behavior under Clang and GCC. Exact block bytes, degenerate-input
   coverage, sanitizer gates, and both-direction speed are mandatory.
2. **Datacube admission profile.** Make source-budget room, carry source and
   notices, authenticate a profile/build identity, bind stored/plain hashes and
   limits, define unsupported-reader behavior, add carrier mutation canaries,
   and prove source-only whole-file rebuilding. Start with
   `datacube-capsule-speed-v1` for the current capsule shape.
3. **Broaden the compiler-fair baseline.** Repeat matched Clang and GCC tests on
   the next rotating cohort, scalar/2/4/8 lanes, per-cube and combined streams,
   a second machine if available, and equivalent durability accounting.
4. **PGO and code layout.** Train on one cohort and evaluate on a different
   unseen cohort. Compare ordinary O3, IPO, PGO, and PGO+LTO without changing
   encoded bytes.
5. **Retained Datacube operation.** Link the library or retain a service/pool so
   process startup and state construction do not dominate 1–3 MiB capsules.
6. **Cycle-level giant-block diagnosis.** Attribute the 256 MiB decode timeout
   to a specific loop/cache surface before considering any profile above 4 MiB.
7. **Runtime ISA dispatch.** Add a portable baseline plus exact-semantics
   x86-64 CRC32C and safe comparison variants. Forced-baseline tests are
   required.
8. **Whole-process memory receipts.** Pair exact codec-arena admission with
   process/cgroup HWM, stacks, staging, page cache, and embedding-process limits.
9. **Destination-aware I/O.** Remove copies or scans only when elapsed time
   proves a win. Preserve pinned input, complete preflight, and durable atomic
   publication.
10. **Fuzzing and independent decode.** Expand frame/carrier fuzzing and assess a
    small independent bounded decoder for admission assurance.

## Explicitly deprioritized

### Dictionaries and training

The zstd proxy improved size while slowing compression about 22% and
decompression about 12%. Reopen only if a prepared read-only dictionary makes
both directions faster on unseen rotating data after charging dictionary bytes
and memory. Current forecast gives this less than a 20% chance.

### Datacube-specific parsing in the codec

Do not teach the BZ3v1 hot path about AI prose, filenames, ZIP paths, project
names, or today's object layout. Generic BWT, entropy, CRC, scheduling,
compiler, and I/O work survives structural change.

### Deduplication and a new format

The exact repeated-payload signal was too small relative to probe work for a
speed-first format change. Cross-block history, structural splitting,
deduplication, dictionaries, and transform selection stay dormant absent a
large, cheap measured win.

## Promotion gates

A compatible speed change must record exact reconstruction, byte identity at
the same block split, encode/decode time, final size, process HWM, charged codec
workspace, compiler/flags/lanes/block/host, rotating-cohort coverage, and a later
unseen-session witness. GCC, Clang, ASan/UBSan, ThreadSanitizer,
poisoned-workspace, manifest, source-closure, and fresh-extraction gates remain
mandatory.

Datacube integration additionally requires carried source/notices, stable
profile identifiers, raw/plain identities, complete predecode bounds, old-
reader failure semantics, mutation canaries, and exact source-only rebuilding.

## Stopping rules

Reject or defer an idea when it slows either direction without closing a safety
gap; wins only on a named specimen; depends on uncommitted content heuristics;
spends the cloudtainer ceiling rather than preserving headroom; introduces
unbounded allocation/work; changes bytes without a new contract; or enlarges
the trusted decoder for a marginal ratio gain.
