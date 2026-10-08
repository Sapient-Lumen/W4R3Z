# rev0763 handoff

## Authority invariant

Canonical envelope bytes are durable authority. A redundant queue/parent projection is never independently authoritative: all canonical-derived fields must agree before read, claim, completion, recovery, reconciliation, or operator projection may use the row. Contradiction is evidence; it is not silently normalized or repaired.

## Concrete revision surface

- Typed unverified/verified projection boundary and field-level, value-free contradiction classification.
- Checked SQLite decoder for storage class, NULL, signedness/range, digest length, and column index handling.
- Repeatable structural inventory of direct SQLite extraction, schema ownership, claim tuples, canonical decoding, transactions, and potentially sensitive diagnostics.

## Validation truth

Required gate passed: **false**.
Recorded required failures: guard_configure=None, guard_build=None, guard_test=None, guard_direct=None, guard_asan_configure=None, guard_asan_build=None, guard_asan_test=None, main_configure=None, main_build=None, main_ctest=None.
Missing required records: guard_configure, guard_build, guard_test, guard_direct, guard_asan_configure, guard_asan_build, guard_asan_test, main_configure, main_build, main_ctest.

The conservative static inventory reports **76** direct SQLite extraction locations outside its narrow allowlist. Some may be legitimate unrelated decoders; each is an explicit review item, not proof of a vulnerability.

## Next correctness step

Make the existing raw persisted-row constructor private and route every authority-bearing query through the verified factory. Then bind each projection contradiction to the immutable reconciliation incident ledger and add restart/crash tests around claim and completion. Once that compile-time choke point exists, tighten the structural allowlist to zero unreviewed authority-bearing extraction paths.

After the read boundary is complete, return to the cross-resource spool protocol: temporary write, file sync, atomic rename, parent-directory sync, SQLite receipt commit, and acknowledgement, with a crash oracle at every edge.
