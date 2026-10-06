# Related-work research pass 017 — priority fairness and resume-legible governance

Revision: rev0028

This pass asks what BrowserRT should steal from systems that survive overload without letting one source of work dominate everyone else.

## Sources consulted

No external code was imported. These are pattern sources only.

- Kubernetes API Priority and Fairness: classify work into priority levels and flows; protect critical classes; avoid starvation from noisy clients inside a priority class.
- Kubernetes APF enhancement notes: flow schemas, priority levels, concurrency pools, queues, and borrowing language are a useful planning vocabulary for BrowserRT lanes.
- Efficient Fair Queuing using Deficit Round Robin: variable-cost work can be scheduled fairly with per-flow deficits and simple round-robin mechanics.
- Linux Completely Fair Scheduler documentation: fairness is not one queue; it is accounting, runnable entities, and explicit tradeoffs about latency versus fair share.
- SRE Handling Overload: overload handling must include graceful degradation and load shedding; the system must keep functioning under pressure rather than pretend overload will not happen.

## Stolen ideas

### Flow identity matters

A BrowserRT task should eventually carry a `flowId` or equivalent identity. The runtime needs to distinguish three small producers from one noisy producer, even when all use the same priority.

### Priority is not fairness

Priority protects critical work. Fairness prevents same-priority starvation. These are related but different. BrowserRT needs both nouns.

### Variable cost must be accounted

A queue of one huge task is not equivalent to a queue of one tiny task. Deficit-style accounting gives the cube a cheap baby proof for variable-cost dispatch without claiming production scheduling.

### Rejections are part of correctness

A good scheduler proof must include no-mutation rejection. Bad admission decisions must not leak credit, consume budget, change queue length, or silently mutate flow state.

### The office needs a respect surface

Future sessions will not have full memory of prior intent. They need a concise office manual that says: what this project is, what it is not, what has proof, what remains non-claim, and how to earn the next rung.

## What enters rev0025

- `PriorityFairScheduler` as a deterministic DRR-style baby scheduler.
- `scheduler:priority-fairness-proof` as a release-tier proof.
- `docs/20-architecture/priority-fairness-frontier.md`.
- `docs/40-validation/priority-fairness-slice.md`.
- `docs/00-meta/future-session-office-manual.md`.
- `docs/00-meta/non-claims-and-goals-charter.md`.

## Non-claims

- No exact Kubernetes APF implementation.
- No exact DRR, WFQ, CFS, or SRE policy implementation claim.
- No production scheduler claim.
- No preemption, deadlines, cross-lane fairness, or multi-threaded contention proof.
- No performance claim.
