# AnonSync rev0874 research record

The design audit used primary or original technical sources and kept the
resulting claims narrow.

## Linux time namespaces

- Linux `time_namespaces(7)`:
  https://man7.org/linux/man-pages/man7/time_namespaces.7.html
- Linux `proc(5)` and `/proc/thread-self` semantics:
  https://man7.org/linux/man-pages/man5/proc.5.html
- Linux `adjtimex(2)` synchronization/error interface:
  https://man7.org/linux/man-pages/man2/adjtimex.2.html

Takeaway: Linux time namespaces virtualize monotonic/boottime offsets and are
attached to tasks; the calling thread's namespace identity is therefore the
relevant local binding. `CLOCK_BOOTTIME` includes suspend. `adjtimex` supplies
kernel synchronization and error evidence but not cryptographic proof of UTC.

## SQLite serialization

- SQLite transaction documentation:
  https://sqlite.org/lang_transaction.html

Takeaway: `BEGIN IMMEDIATE` starts the write transaction immediately or fails
with `SQLITE_BUSY`. The successful acquisition is the local serialization point
for lease-expiry sampling. Sampling before it cannot be treated as transaction
start time because waiting for another writer can age the sample.

## Fixed operation-start time analogy

- The Update Framework specification:
  https://theupdateframework.github.io/specification/latest/

Takeaway: fixing a workflow's reference time is useful for internal consistency.
TUF's signed-metadata threat model is different; it does not authenticate the
local host clock for AnonSync or justify reusing a pre-lock sample after an
unbounded writer wait.

## Hybrid logical clocks

- Kulkarni, Demirbas, Madappa, Avva, Leone, “Logical Physical Clocks and
  Consistent Snapshots in Globally Distributed Databases”:
  https://cse.buffalo.edu/tech-reports/2014-04.pdf
- Springer conference version:
  https://link.springer.com/chapter/10.1007/978-3-319-14472-6_2

Takeaway: hybrid logical clocks are promising for causality and snapshots, but
they do not by themselves prove a physical lease has expired. A future design
could combine causal ordering with separately owned physical-time evidence.

## Speculative directions

A remote time witness, hardware-/OS-bound checkpoint key, append-only
checkpoint chain, or quorum lease could reduce reliance on one host clock, but
each changes availability, recovery, and key-ownership semantics. An incremental
owner should be differential-tested against the full-history oracle. A durable
clock anchor might eventually become a compact authenticated checkpoint chain,
but compaction must retain enough evidence to explain cumulative drift and every
recovery boundary.
