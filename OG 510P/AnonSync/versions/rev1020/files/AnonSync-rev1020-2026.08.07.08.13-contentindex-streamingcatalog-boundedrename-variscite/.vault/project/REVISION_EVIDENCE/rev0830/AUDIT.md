# Rev0830 audit — durable transition is not identical to replay authority

## Mission-level finding

AnonSync’s heart remains evidence-authorized convergence. A transition may be
replayed, merged, published, or recovered only when the owner of that invariant
can name the exact evidence that survived concurrency, failure, and restart.

Rev0829 gave the reset plus immutable receipt one C++ protocol owner. The
remaining weakness was semantic rather than structural: the owner exposed a
Boolean `durable_reset_observed()`. That merged two states which have different
safe actions:

1. the exact request-derived identity is durably established; and
2. a durable boundary was crossed, but the identity associated with it is
   contradictory or cannot be re-established.

The second state cannot safely mint automatic replay authority.

## Corrected state machine

The public protocol error now carries a tri-state durable-evidence enum,
separate failure phase, and separate recovery action. Its private constructor
validates the permitted product of those states:

| Durable evidence | Permitted recovery |
|---|---|
| `NotDurable` | `None` |
| `ExactRequestDurable` | `ReplayExactRequestToFreshReceiptPath` |
| `DurableIdentityIndeterminate` | `ResolveDurableIdentityBeforeRecovery` |

Publication effects are present only for the typed publication phase. A
reported reset outcome is present only after a durable frontier and is named
`reported_reset_outcome` to prevent callers from confusing the implementation’s
report with independent recovery evidence. Every nonempty expected receipt
identity is validated as lowercase SHA-256.

## Independent promotion rule

The ambiguous frontier classifier performs a fresh production inspection of the
ledger. Promotion to `ExactRequestDurable` requires the request path, exact
parent/database object identity, and deterministic receipt identity all to
match. Inspection failure and every mismatch remain indeterminate.

Both ambiguous paths call the same classifier. This was refactored deliberately:
a mapping duplicated in two catch blocks would recreate the possibility that a
post-commit exception and a contradictory normal return gain different recovery
authority over time.

## Behavioral proof rather than token proof

The combined runtime corpus now includes three complementary traces:

1. a reset observer throws after commit; exact independent reopen permits
   fresh-path recovery and preserves the nested cause;
2. a normal reset result is contradicted while durable identity remains exact;
   only independent reopen promotes it; and
3. a normal result is contradicted while a competing durable identity is
   installed before binding; replay is denied, no receipt is published, no temp
   is left, and the competing identity is visible in the error chain.

A fourth trace changes durable identity during the reset owner’s own
post-commit verification, proving the indeterminate classification through the
typed durable-outcome exception path as well.

The oracle passes **462 checks**. This closes the exact false-authority trace,
not merely the enum spelling.

## Structural obligations

- SQLite reset audit: **99/99**;
- reset receipt audit: **42/42**;
- reset protocol audit: **29/29**;
- crash-frontier audit: **19/19**;
- atomic publication audit: **39/39**;
- aggregate: **228/228**.

The protocol audit now requires the Boolean API to be absent, the shared
classifier to be called by both ambiguous paths, path/object/identity binding to
be explicit, both exact and indeterminate runtime mutations to exist, and the
CLI’s distinct non-replay status to remain present.

## Remaining severe boundary

The application-selected frontier model still assumes SQLite’s VFS and storage
contract. SQLite’s own testing documentation describes fault-injecting VFS
implementations, one-shot and persistent I/O errors, simulated incomplete and
out-of-order writes, process crashes, reopen, and integrity verification. The
next high-value work is therefore not another catch classifier. It is a custom
AnonSync VFS/crash oracle that joins the database’s recovered domain state to
the receipt publisher’s typed state at every operation cutpoint.

## Claim boundary

The tri-state result says what recovery action the application may authorize
from the evidence it can presently verify. It does not prove that the kernel,
filesystem, VFS, drive cache, or storage device honored durability semantics.
It is not a cross-resource atomic commit protocol and not a distributed
convergence proof.
