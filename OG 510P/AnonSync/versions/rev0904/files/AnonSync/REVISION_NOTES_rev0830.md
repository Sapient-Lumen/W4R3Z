# AnonSync rev0830 — tri-state durability, reopen binding, replay fence

Rev0830 closes the highest-risk recovery-authority gap left by rev0829. A
reset/receipt failure no longer answers the question “is it durable?” with one
Boolean. It distinguishes three materially different states:

- `NotDurable`: no durable reset outcome was established;
- `ExactRequestDurable`: the exact request-derived reset transition is known to
  be durable; and
- `DurableIdentityIndeterminate`: a durable frontier was crossed, but the
  current ledger identity cannot be bound to that exact request.

Only `ExactRequestDurable` authorizes replay of the exact digest-pinned request
to a fresh absent receipt path. The indeterminate state authorizes identity
resolution, not replay.

## Severe audit correction

Rev0829’s protocol owner correctly replaced caller choreography, but its public
error reduced durable evidence to `durable_reset_observed()`. A contradictory
returned result was handled after the reset call had completed, so the protocol
classified it as durable and granted automatic replay. That conclusion was too
strong: crossing the SQLite commit frontier proves that *some* transition may
be durable, not that the durable identity still names this exact request.

The dangerous trace is now executable:

1. the reset commits and returns normally;
2. returned result evidence is contradicted before protocol binding;
3. the durable ledger identity changes before independent inspection; and
4. the old Boolean model would have recommended exact replay.

Rev0830 classifies that trace as `DurableIdentityIndeterminate`, emits recovery
`ResolveDurableIdentityBeforeRecovery`, returns CLI exit status 4, and does not
attempt receipt publication. The independently reopened competing identity is
retained in the nested diagnostic chain.

## One classifier, two ambiguous paths

Both ambiguous post-commit paths now enter one internal classifier:

- `SqliteReplayLedgerResetDurableOutcomeError`, including observer or
  post-commit verification failure; and
- contradiction between the reset result and the original request.

The classifier reopens the ledger through the production inspection owner and
requires all of the following before promoting recovery authority:

- the normalized ledger path is still the exact request path;
- the current parent/database object identity matches the request’s
  `SqlitePathIdentity`; and
- the current durable `ledger_instance_id` is the deterministic receipt digest
  for the exact request.

A mismatch or inspection failure produces the indeterminate state. No catch
block owns a second copy of the exact/indeterminate mapping. The protocol error’s
private constructor also rejects invalid phase/evidence/recovery combinations
and now requires every nonempty expected receipt identity to be lowercase
SHA-256.

`ExactRequestDurable` means the exact transition is known to have committed. It
does not claim that unrelated later state cannot advance after that transition;
replay remains safe because the reset operation is digest-pinned and
idempotently recognizes its deterministic receipt.

## Audit and refactor

The CLI no longer has a durable Boolean. It renders the durable-evidence enum,
the reset implementation’s explicitly non-authoritative
`reported_reset_outcome`, typed recovery action, expected receipt digest, and
publication effect. Exit status 3 is reserved for exact-request recovery; exit
status 4 is a fail-closed automation fence for indeterminate identity.

The deterministic internal seam can now mutate returned reset evidence between
reset return and request binding. It is not part of the public production API.
The runtime oracle covers both directions:

- contradictory return plus an unchanged ledger is promoted only after an exact
  independent reopen; and
- contradictory return plus durable identity drift is denied replay authority.

A separate post-commit observer trace proves the same indeterminate result for
the reset owner’s typed durable-outcome exception path. The combined frontier
oracle increased from **442** to **462** checks.

## Validation on the frozen source

- exact rev0829 parent: ZIP **25/25**, directory **21/21**;
- GCC 14 Debug all-target build: passed; final dependency closure: no work;
- complete CTest inventory in one uninterrupted invocation: **116/116**;
- focused reset/protocol gate: **8/8**;
- reset oracle: **68/68**;
- protocol/crash-frontier oracle: **462/462**;
- focused structural audits: **228/228**;
- Clang 17 warnings-as-errors and ASan/UBSan focused results are recorded in
  `REVISION_EVIDENCE/rev0830/validation/` and the release gate; and
- the final directory and ZIP are verified against the exact manifest and
  active implementation projection before publication.

## Claim boundary

This independent reopen is an application-level evidence rule, not a proof over
arbitrary storage behavior. It does not enumerate every SQLite VFS `xWrite`,
`xSync`, `xTruncate`, `xDelete`, lock, shared-memory, WAL, journal, torn-write,
reordered-unsynchronized-write, kernel-crash, power-loss, or dishonest-storage
outcome. It also does not create a transaction spanning SQLite and an arbitrary
receipt file.

The Linux process/frontier tests do not prove Windows behavior. Hostile SQLite
artifacts are still interpreted in the long-lived process. Distributed
convergence, payload confidentiality, anonymity, metadata hiding, key lifecycle,
and secure erasure remain unproved.
