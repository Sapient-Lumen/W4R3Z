# Rev0807 online research

This research informs the audit and roadmap. It is not represented as proof that
AnonSync already implements the referenced properties.

## SQLite transaction serialization

**Primary source:** SQLite, *Transaction*  
<https://sqlite.org/lang_transaction.html>

SQLite permits multiple readers but only one simultaneous writer.
`BEGIN IMMEDIATE` starts a write transaction immediately and can fail with
`SQLITE_BUSY` when another writer is active.

**Applied inference:** AnonSync can atomically verify a daemon owner generation
and mutate checkpoint state in one `BEGIN IMMEDIATE` transaction. Writer
serialization alone does not identify which process is authorized; the owner
capability must be checked within that transaction.

## Stale lock-holder requests and sequencers

**Primary source:** Mike Burrows, *The Chubby lock service for
loosely-coupled distributed systems*, OSDI 2006  
<https://research.google.com/archive/chubby-osdi06.pdf>

Chubby discusses the case where a lock holder issues a request, loses the lock,
a successor acquires it, and the old request arrives late. Its lock sequencer
carries lock identity and generation so the recipient can reject stale
requests.

**Applied inference:** AnonSync's owner row is not a complete fence until the
DB-minted owner generation reaches every mutation boundary and is verified by
the recipient transaction. A heartbeat or successful acquisition in the caller
is not equivalent to recipient-side generation validation.

## Small-state protocol verification

**Primary source:** Leslie Lamport, *Specifying and Verifying Systems With
TLA+*  
<https://lamport.azurewebsites.net/pubs/spec-and-verifying.pdf>

TLC explores reachable states for invariants and deadlocks; for a safety
violation it reports a minimal-length error trace.

**Applied inference:** The checkpoint state machine is a strong bounded-model
candidate. Useful variables include daemon owner generation, worker lease,
review state, retry window, action cap, mutation reservation, crash point, and
published file effect. The core invariant is that a stale owner never performs a
mutation or publication, and a terminal-review fence never permits a selected
mutation in the same pass.

## Systematic executable distributed-system testing

**Primary source:** Microsoft Research, *Uncovering bugs in distributed storage
systems during testing (not in production!)*  
<https://www.microsoft.com/en-us/research/publication/uncovering-bugs-in-distributed-storage-systems-during-testing-not-in-production/>

The work argues for systematic controlled schedules and failures over
executable distributed-system implementations, producing small reproducible
traces for subtle bugs.

**Applied inference:** AnonSync should pair an abstract owner/lease model with a
deterministic C++ simulator that controls daemon pause/resume, clock advance,
lock expiry, process restart, request delay, and crash cuts. The same generated
trace should run against the model and production transition functions.

## Bounded crash-consistency exploration

**Primary source:** Jayashree Mohan et al., *CrashMonkey and ACE:
Systematically Testing File-System Crash Consistency*  
<https://www.microsoft.com/en-us/research/wp-content/uploads/2021/10/tos-crashmonkey.pdf>

CrashMonkey/Ace bound workloads and crash after persistence points, then compare
recovered state with an oracle. The bounded persistence-point strategy makes a
large exploration tractable while still finding real faults.

**Applied inference:** AnonSync's crash oracle should enumerate bounded cuts at
SQLite commit, WAL/journal sync, staging-file sync, receipt publication, rename,
directory sync, checkpoint aggregate update, and externally visible materialized
file publication. The oracle must classify all related artifacts together, not
accept SQLite integrity as sufficient domain recovery.

## Research-driven next experiment

A compact two-layer harness would provide the highest leverage:

1. a TLA+ or equally small executable reference model of owner generation,
   worker leases, terminal review, grouped scheduler actions, crash, and
   publication; and
2. a deterministic C++ trace runner using an injected clock and fault schedule.

Initial traces should include:

- old daemon pauses, owner expires, successor acquires, old daemon resumes;
- review and runnable mutation coexist under every action cap;
- a mutation group is larger than the cap;
- owner replacement occurs between planning and mutation transaction;
- database commit succeeds but process crashes before receipt or directory sync;
- receipt publishes but checkpoint aggregate commit is cut; and
- duplicate/reordered retries cross an owner or key epoch boundary.
