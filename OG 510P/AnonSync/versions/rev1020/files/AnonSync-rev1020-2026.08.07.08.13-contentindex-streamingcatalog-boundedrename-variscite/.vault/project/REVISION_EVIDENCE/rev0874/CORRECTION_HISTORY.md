# AnonSync rev0874 correction history

The interrupted rev0874 workspace contained a substantial owned-clock
implementation, but CMake, audits, and the verifier still named the retired
rev0873 time fence. That assurance-graph mismatch was corrected first.

A deeper audit then rejected the initial pre-lock sampling optimization. The
sample could wait behind another SQLite writer and authorize a receipt after its
real expiry. Authoritative sampling was moved inside the immediate writer
transaction after complete restore. A deterministic contention probe now pins
that ordering.

The same audit rejected pairwise-only drift checks. Repeated small legal steps
could cumulatively launder an unbounded discontinuity. A durable
initialization/recovery anchor now bounds cumulative forward step and realtime
lag.

The Linux identity binding was tightened from process-leader namespace lookup to
`/proc/thread-self/ns/time`. Exact schema-v4 migration fixtures were added after
the migration audit found direct rev0873 retry-provenance coverage missing.

Finally, release prose was corrected not to claim that final directory/ZIP
verifier reports are embedded inside the immutable artifact they attest. Those
reports are post-seal external evidence by construction.
