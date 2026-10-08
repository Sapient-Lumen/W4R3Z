# Rev0807 audit

## Mission finding

AnonSync's strongest coherent architecture is an evidence-authorized convergence
kernel. Every boundary should distinguish observation from authority and make
that distinction executable through typed inputs, exact relationship checks,
transaction-local validation, bounded resources, and adversarial tests.

The checkpoint scheduler was the right next extraction because it combined a
pure evidence-to-action decision with durable queue loading and mutation side
effects. Keeping those concerns together made exhaustive policy testing
expensive and hid one harmful ordering bug.

## Corrected defect

`stop_on_terminal_review` was enforced after a completed scheduler pass. A pass
could therefore mutate runnable work before the daemon honored a quarantined or
abandoned review row. Rev0807 moves the review decision before execution-key
construction and both mutator calls. The default is fail-safe, and the daemon,
heartbeat, CLI, focused policy, source audit, and durable integration corpus all
bind the decision.

## Refactor assessment

The split follows three different authorities:

- durable queue selection remains in the checkpoint persistence owner;
- pure queue-fact validation, ordering, and bounded grouping live in an
  independently linked policy owner; and
- public orchestration plus mutation dispatch live in the runtime scheduler.

The split is not cosmetically line-based. The pure owner has no SQLite,
filesystem, crypto, clock, or mutation dependency and supports a no-core
exhaustive test. The runtime executor independently checks policy group metadata
before accepting its output as mutation authority.

## Audit results

- Scheduler owner/purity/fence audit: **22/22**.
- Runtime/selftest separation: **9/9**.
- Domain diagnostic separation: **13/13**.
- CLI-advertised versus CTest-registered selftests: **38/38**.
- Full CTest: **83/83**.
- Domain model: **592/592**.
- Pure policy: **1,975,744/1,975,744** assertions.
- Six changed units pass strict Clang 17 and GCC 14 optimized analysis.
- Focused pure policy passes ASan/UBSan with leak detection enabled.

## Compile economics

The remaining domain unit is 511 lines smaller. Its direct GCC compile falls
from 11.06 to 9.69 seconds and from 690,840 to 621,280 KiB peak RSS in this
sample. The scheduler and policy add separate 2.43-second and 0.99-second
compiles. Total serial work therefore rises; the architectural benefit is a
smaller maximum job, parallelism, correct ownership, and an inexpensive focused
proof surface.

## Severe unresolved finding

The daemon owner lock is not yet a recipient-validated fencing token.
`owner_lock_epoch` is caller supplied, replacement does not enforce a monotonic
database generation, scheduler mutators do not carry the owner capability, and
their `BEGIN IMMEDIATE` transactions do not verify the current owner row.

This leaves a pause/expire/reclaim/resume trace in which an old process can
reach a mutation boundary after a successor has acquired the row. SQLite writer
serialization prevents simultaneous writes but does not reject the stale owner.

The exact negative evidence is in
`audits/daemon-owner-fencing-hazard.json`. Rev0807 deliberately does not claim
stale-owner safety.

## Other remaining high-value work

1. Add DB-minted monotonic owner generations and transaction-local fencing to
   every checkpoint mutation and published file effect.
2. Build a small independent convergence and ownership state machine, then run
   generated traces against production C++.
3. Add a crash-cut oracle spanning database, WAL/journal, receipts, sidecars,
   staging, rename, directory sync, and materialized output.
4. Continue reducing raw SQLite interpretation and the remaining 15,329-line
   domain owner by invariant, not line count.
5. Separate authentication/replay evidence from unproved privacy, anonymity,
   forward-secrecy, and post-compromise-recovery claims.

## Claim discipline

Rev0807 claims a complete normal Debug gate and one focused sanitizer lane. It
does not claim a complete instrumented application, formal convergence,
transactional owner fencing, exhaustive crash safety, remote-network behavior,
payload confidentiality, metadata hiding, anonymity, forward secrecy, or
post-compromise recovery.
