# IoTox cloudtainer build report — rev0037

- **Version:** 0.37.0
- **Revision:** rev0037
- **Codename:** Memory Work Swap IRQ Freeze Citadel
- **Linked outer revision:** rev0024
- **Qualified implementation commit:** `1393ebf20f7359fde593d2f668779c30d598914b`
- **Qualified implementation tree:** `9751725d90d02505506e2612cf75ae63f19ca733`

## Result

rev0037 extends the descriptor-pinned delegated cgroup-v2 teardown boundary with four additional
classes of content-free session evidence: cumulative memory work from `memory.stat`, swap allocation
outcomes from `memory.swap.events`, freezer duration from `cgroup.stat.local`, and IRQ/SOFTIRQ stall
time from `irq.pressure` where the running kernel exposes that interface.

Each new session leaf pins and verifies every available outcome file before payload attachment. A
configured memory or swap policy makes `memory.stat` mandatory, and a finite swap ceiling makes
`memory.swap.events` mandatory. Newer local-freeze and IRQ-pressure interfaces remain independently
optional capabilities so an older kernel cannot be mistaken for a supported interface that measured
zero. Any present interface must parse and begin at an exact zero baseline before the payload enters
the cgroup.

The bounded flat-key parser requires `pgfault` and `pgmajfault`, accepts `pgscan` plus `pgsteal` only
as one complete reclaim tuple, and accepts `pswpin` plus `pswpout` only as one complete swap tuple.
The swap-event parser requires `high`, `max`, and `fail`; `fail` is retained without claiming whether
the allocation failed because of global swap exhaustion or the cgroup maximum. The local-stat parser
requires `frozen_usec` while accepting unrelated future canonical counters. All parsers reject
malformed spacing, duplicate keys, noncanonical or overflowing integers, partial tuples, truncation,
and oversized records.

The PSI grammar is shared without sharing the wrong semantic requirement. CPU, memory, and I/O PSI
continue to require `some`; the dedicated IRQ parser requires the current kernel's `full` row and does
not fabricate a nonexistent IRQ `some` metric. Rolling averages are validated but not retained.

After recursive `populated=0`, and before exact pinned-inode removal, IoTox reads all outcome
descriptors once. A failure in any available outcome interface marks the entire session observation
incomplete; no successful subset is aggregated. Complete observations saturatingly retain page
faults, major faults, pages scanned and reclaimed, pages swapped in and out, swap high/max/fail
events, freezer microseconds, and IRQ-full microseconds together with independent capability counts.
Seventeen new totals are projected only through the owner-private runtime status surface. No path,
command, terminal, peer, profile, device, payload, rolling sample, or per-session label is retained.

The local terminal profile and wire format remain canonical v5. This revision changes observation,
not admission or enforcement: it adds no swap policy beyond the existing ceiling, no PSI trigger,
continuous sampler, adaptive resource controller, causal attribution, or service-level claim.

## Validation summary

- GCC 14.2 Debug warnings-as-errors: all 18 configured CTest entries completed; 15 passed, three
  named controller-capability skips, and zero failed.
- GCC 14.2 Release warnings-as-errors: all 18 configured entries completed; 15 passed, three named
  controller-capability skips, and zero failed.
- Clang 17 Debug warnings-as-errors: all 18 configured entries completed; 15 passed, three named
  controller-capability skips, and zero failed.
- Clang 17 ASan plus UBSan: all 33 configured sharded entries completed; 30 passed, three named
  controller-capability skips, zero failed, and no sanitizer diagnostic.
- GCC 14 ThreadSanitizer: all 33 configured sharded entries completed; 30 passed, three named
  controller-capability skips, zero failed, and no race diagnostic.
- Clang libFuzzer: all eleven configured targets completed 5,000 runs each, including the extended
  terminal-cgroup grammar target.
- Host-linked Argon2: all 18 configured entries completed; 15 passed, three named capability skips,
  and zero failed.
- Mutorr preservation: all 20 configured entries completed; 17 passed, three named capability skips,
  and zero failed.
- Exclusive Agent/session stress: 100/100 exact repetitions passed against one discovered registry
  shard.
- Direct owned registry: 351 fixture-aware checks, zero failures.
- Product identity: the binary reports `IoTox 0.37.0 rev0037`.
- Source-linked standalone attempt: stopped before compilation with curl exit 6 because the construction
  container could not resolve `download.libsodium.org`; the exact attempt and exit are retained, and no
  c-toxcore/libsodium/Argon2 source-linkage result is claimed.
- Qualified source `git diff --check`: pass. Every tracked shell script passes `bash -n`; `git fsck`
  passes; tracked symlink entries, sensitive-looking history paths, and tracked private-key markers
  are zero.

The three named controller-intensive routes stop with CTest skip code 77 because the construction
container does not delegate preactivated memory, CPU, or I/O controllers to child cgroups. Those
skips are not reported as positive controller-enforcement results.

## Focused proof surface

Parser tests freeze reordered complete current records, older records without optional tuples,
future numeric keys and PSI classes, exact totals, and rejection of missing mandatory fields,
partial reclaim or swap tuples, duplicates, malformed spacing, malformed decimals, unterminated or
oversized records, noncanonical integers, and overflow. Aggregate tests prove independent
capability counts, one-shot duplicate suppression, all-or-nothing incomplete outcomes, exact sums,
and unsigned saturation for every new counter. Runtime-tree tests freeze all seventeen new
owner-private status fields.

The real-kernel lifecycle oracle creates a fresh private session leaf, attaches a child, faults in
4 MiB of anonymous memory after attachment, and compares the final pinned `memory.stat`,
`memory.swap.events`, `cgroup.stat.local`, and `irq.pressure` records with the one-shot teardown
outcome wherever each interface exists. On this Linux 6.18.35 construction host, page-fault evidence
is positive. `cgroup.stat.local` is available and a real freeze/unfreeze cycle yields positive
`frozen_usec`. `irq.pressure` is absent in the container view, so no positive live IRQ PSI result is
claimed. The swap-event interface is compared exactly, but this run does not deliberately exhaust
swap or claim a positive swap-failure event.

## Research and construction evidence

Construction rechecked the current official Linux cgroup-v2 and PSI documentation on 2026-08-19.
The kernel contract defines `memory.stat` as flat-keyed and explicitly warns consumers to key-lookup
rather than depend on position; documents page-fault, reclaim, and swap page counters; defines swap
`high`, `max`, and causally ambiguous `fail` events; defines `frozen_usec` as cumulative time between
freezing and thawing without requiring arrival at the fully frozen state; and exposes per-cgroup
IRQ/SOFTIRQ PSI through `irq.pressure`. Current kernel state definitions expose IRQ `full`, not an IRQ
`some` class.

The applied source review is
`docs/research/memory-work-swap-irq-freeze-kernel-accounting-rev0037.md`; ADR 0088 freezes capability,
parser, zero-baseline, teardown, aggregation, privacy, and nonclaim boundaries. Revision-owned
transcripts, exact source identity, source URLs, exit records, checksums, and prebuilt smoke evidence
are retained under `artifacts/rev0037/` after artifact refresh.

## Nonclaims

rev0037 does not continuously sample memory, swap, freezer, or IRQ state; register PSI triggers;
adapt admission or resource limits; infer why a page fault, reclaim, swap failure, freeze, or IRQ
stall occurred; convert swap page counts to physical I/O or durable-media evidence; distinguish global
swap exhaustion from `memory.swap.max` in the `fail` counter; treat `frozen_usec` as command runtime;
attribute any counter to a command, file, peer, terminal, profile, or device; persist session outcomes
across daemon restart; protect against root or an equivalent delegated co-writer; qualify a target
kernel fleet; establish a genuine public-Tox two-peer Ratox session; complete physical-host R7
qualification; provide an independent security audit; or establish production readiness.
