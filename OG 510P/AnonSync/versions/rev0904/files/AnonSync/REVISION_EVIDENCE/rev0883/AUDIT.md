# rev0883 audit record

## Heart of the mission

AnonSync is an exact-authority accounting system. Canonical evidence and live
capabilities own identity, causality, dispatch, retry, receipt, and visible
effect. C++ wrappers, object addresses, thread IDs, sockets, TLS progress,
filesystem spellings, summaries, and test reports may carry or verify authority;
they must not manufacture it.

Rev0883 applies that rule to no-throw cleanup. A move-only TLS continuation is a
shared authenticated-stream capability, not a byte-count value whose move
silently transfers process/thread authority.

## Severe defect corrected

Rev0882 fenced ordinary record I/O and final `SSL_free()`, but
`complete_record_write_noexcept()` and `poison_noexcept()` changed shared stream
flags without checking the creating process/thread incarnation. An active
continuation abandoned on a foreign thread could therefore mutate
`poisoned_`/`record_write_active_` before final destruction detected the owner
contradiction.

Rev0883 introduces one process-then-thread fail-stop helper and calls it before
completion, poison/abandonment, and SSL release. The public contract names
foreign-thread finish, destruction, and active-target move-assignment. The
runtime test proves the destructor frontier in a child process because the
required behavior is immediate termination without unwinding.

## Audit/refactor finding

The new child-process test increased one exact inherited-process consumer from
one to two spawn sites. Two inventory audits rejected the first complete gate;
a third cross-audit aggregate rejected the next gate. The correction preserved
fail-closed discovery and updated only the exact facts: one raw fork owner, 15
consumer translation units, 27 inherited spawn sites, eight fresh-image
campaigns, and 35 classified process sites.

The TLS structural audit was refactored to one v2 inventory with 32 checks. It
requires the central no-throw fence, process/thread ordering, ordering before
mutation/free, public contract, process-isolated test, package surface, research,
rejected scope, and nonclaims. It remains lexical hygiene, not behavioral proof.

## Rejected waste

A noncanonical mutable workspace acquired a 578-line receive prototype that
changed public APIs, failed its first focused compile, and supplied no matching
runtime matrix. It was rejected rather than repaired opportunistically. This
prevents speculative workspace presence from becoming lineage or review
authority. The receive problem remains important and should return as a
separately designed event-loop state machine.

## Load-bearing evidence

- exact rev0882 parent ZIP reverified 26/26;
- clean GCC 14 Debug graph, 381 fresh actions, final no-work closure;
- complete final registered gate 192/192;
- complete audit-named gate 61/61;
- 5,199/5,199 focused checks in GCC Debug, Clang Release `-Werror`, and GCC
  ASan/UBSan with leak detection and bundled SQLite instrumented;
- 5,940/5,940 mixed stress checks;
- 100/100 targeted TLS runs, 7,500/7,500 checks;
- 509/509 selected source-audit checks across 17 audits; and
- active projection, exact patch, evidence index, manifest, directory verifier,
  and ZIP verifier at publication.

## Largest remaining gap

The sender-side first-prefix path is still not a product-shaped sync service.
There is no single-owner nonblocking receiver loop, resumable WANT state,
durable body/chunk progress, exact receiver payload/effect composition on a
socket, terminal receipt return, or shipped-executable migration. More local
sender guards cannot substitute for this missing end-to-end path.

## Nonclaims

This revision does not claim race freedom, ThreadSanitizer, formal proof,
receiver-loop integration, resumable TLS progress, distributed atomicity, peer
receipt from local write completion, exactly-once remote effect, anonymity, or
externally trusted signed provenance.
