# rev0867 audit: retained-evidence budget and admission atomicity

## Mission

AnonSync's core mission is not file copying. It is **evidence-authorized,
crash-consistent, bounded convergence**: replicas that retain the same
authorized canonical evidence and trust state should derive the same visible
state, while malformed input, missing dependencies, forks, duplicate delivery,
crashes, and resource pressure must never silently gain authority.

rev0865 and rev0866 made the in-memory reference model evidence-complete and
arrival-independent. rev0867 corrects the next severe mismatch: those revisions
bounded one envelope and one operation count, but did not bound the cumulative
canonical material retained across active, pending, and quarantined evidence.
At the prior defaults, `10,000 * 4 MiB` authorized 41,943,040,000 bytes, exactly
39.0625 GiB, before map, vector, string, allocator, index, WAL, or payload
overhead.

## Implemented correction

`SyncReplicaModelLimits` now has three independent retained-evidence ceilings:
canonical envelope bytes, causal-context entries, and exact predecessor IDs.
Defaults cap canonical evidence at 256 MiB and both structural collections at
1,000,000 entries. Each aggregate ceiling must be at least its corresponding
single-envelope ceiling, so a policy cannot advertise a valid envelope that no
empty model can retain.

One semantic validation traversal now computes the exact canonical envelope
size. Remote admission validates and measures a new envelope, preflights all
three cumulative totals with overflow-safe subtraction, then inserts and
projects. The three counters publish only in the final no-throw commit section.
Local mint performs the same preflight before publishing local counter
authority. Restore consumes its durable state by value, validates and charges
each envelope while moving it into the canonical map, rejects over-budget state
before publishing a model, and then reprojects every node.

Exact duplicate replay is a special idempotent path. When a retained immutable
operation is byte-for-byte equal, admission returns `Duplicate` before canonical
re-encoding or hashing, performs zero allocations in the injected-allocation
probe, and consumes no additional budget. A same-ID nonidentical value still
runs full validation and is rejected as a digest collision boundary.

A validation hot path was also refactored: causal-context ordering now keeps a
non-owning pointer to the preceding actor instead of copying its `device_id` on
every entry. The SQLite sidecar source audit no longer hard-codes an exact count
of Python tests; it verifies a minimum and hermetic parity, so adding a new
registered audit does not break an unrelated ownership proof.

## Executable evidence

All 168 registered GCC tests pass in two deliberate lanes: 167/167 in the
parallel registry excluding the declared serial integration owner, followed by
the isolated `anonsync_core_sync_domain_model_selftest`, which reports 611/611
internal assertions. The 167-test lane includes all 50 registered source audits.
Repeatedly launching that serial owner immediately after the complete parallel
lane can stall in CTest's wrapper in this cloud container; the isolated CTest
invocation and direct executable both terminate cleanly. The evidence therefore
does not claim one uninterrupted CTest process.

The four focused executables report 2,068 checks under GCC, Clang 17 Release
with `-Werror`, and GCC ASan/UBSan with leak detection and halt-on-error:

- 67 network/model checks over 44 generated operations;
- 1,288 canonical codec, hash-graph, projection, reverse-chain, wide-fan-in, and
  differential-oracle checks;
- 688 allocation-atomicity checks over 180 local and 158 remote throwing
  allocation cutpoints, including all three retained counters and zero-allocation
  exact duplicate replay; and
- 25 aggregate-budget checks spanning active, pending, quarantined, duplicate,
  restore, local mint, byte, context-entry, and predecessor-ID boundaries.

Clang's static analyzer reports no diagnostics across the changed model, codec,
allocation-fault test, and aggregate-budget test translation units. The full GCC
all-target build completes and a subsequent Ninja invocation performs zero
compile or link steps. The focused aggregate source audit passes 20/20 and the
refactored SQLite sidecar audit passes 105/105.

## What this does not prove

This is a bounded C++ reference model. It does not yet prove that production
persistence, transport, payload materialization, authentication, or anti-entropy
use the same cutpoint. The budgets are local safety brakes, not garbage
collection, causal stability, fairness, or global validity. A replica that has
no local capacity must not teach peers that otherwise valid evidence is
cryptographically invalid.

The accounting deliberately charges canonical envelope bytes and structural
entry counts. It does not equal process RSS, allocator overhead, indexes, SQLite
pages, WAL growth, payload chunks, decompression expansion, or network work.
Those require separate owners and ceilings.

## Highest-priority gaps

1. Build the production SQLite transaction owner that atomically reserves a
   local dot, persists exact canonical bytes and parent edges, updates the
   projection/head cut, and appends outbox intent.
2. Add authenticated actor signatures, membership/key lifecycle, epoch rotation,
   revocation, and durable anti-rollback authority.
3. Distinguish `valid-but-capacity-blocked` from malformed/quarantined evidence;
   add bounded retry and backpressure rather than consensus-by-local-RAM.
4. Replace oracle-scale full reprojection and complete-evidence exchange with
   incremental projection, compact fork proofs, delta/Merkle anti-entropy, and
   checkpoint certificates.
5. Define causal stability and compaction before deleting evidence; bind any
   checkpoint to exact authorization and retained fork knowledge.
6. Add per-principal and unknown-identity quotas. A global byte ceiling alone
   does not prevent one identity—or an unbounded stream of fresh identities—from
   monopolizing the budget.

## Lineage

The source patch changes ten active files, adds two of them, and applies cleanly
to the exact rev0866 archive. A fresh replay matches all 327 active files
byte-for-byte with zero missing, extra, or mismatched paths. Parent ZIP and
extracted-directory verification pass 26/26 and 22/22 respectively.
