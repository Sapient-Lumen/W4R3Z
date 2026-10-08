# Rev0809 audit

## Mission finding

The most important AnonSync invariant is that a successful observation is not
authority. The owner-lock path violated that rule: acquisition produced a row,
but mutation recipients did not receive and validate an exact current
generation. Rev0809 turns the row into local fencing evidence.

## Corrected defect

The parent allowed a paused daemon to outlive its lease, lose ownership, resume,
and reach a checkpoint mutation without a stale-generation check at the
recipient. Caller-selected owner epochs also permitted reuse and did not prove a
strict successor relation.

Rev0809 mints generation one or `stored + 1` under an immediate write
transaction, compare-and-replaces on the prior generation, reloads exact proof,
propagates the capability, and verifies it in recipient transactions. Release
uses the same rule. A focused A→B test proves stale A produces no guarded effect.

## Refactor assessment

The split is by invariant ownership rather than by line count:

- the pure policy owns valid state transitions and capability geometry;
- the focused SQLite owner interprets durable rows, mints/retires generations,
  and validates recipients; and
- the domain owner retains orchestration, schema setup, and transaction/commit
  boundaries.

The policy and focused tests do not link the core monolith. A CMake source-owner
guard prevents the new implementations from being reabsorbed. The existing
scheduler monolith budget was preserved and drove acquisition/release SQL into
the focused boundary.

## Audit and validation results

- Owner-fence source/dependency/placement audit: **25/25**.
- Owner-fence pure policy: **28/28**.
- Owner-fence SQLite recipient: **23/23**.
- Scheduler separation regression audit: **22/22**.
- Full CTest inventory: **86**, all passed in complete bounded ranges.
- Domain model: **592/592**.
- Strict GCC/Clang focused compilation: **8/8** combinations.
- Focused ASan/UBSan: **28/28** and **23/23**.
- Isolated locking diagnostic: **6/6**.
- Write-gate diagnostic: 16 consecutive completed **9/9** passes.

## Correctly limited claim

Stale-owner exclusion is claimed only for compliant checkpoint mutators sharing
one SQLite database/VFS and using the guarded paths. It is not network
consensus, cross-device fencing, trusted time, or Byzantine isolation.

The filesystem reservation prevents a compliant takeover from interleaving
between validation and effect, but does not make file and database state one
crash-atomic transaction.

Released rows still allow empty-capability operation. Sticky ownership is the
highest-value next policy correction.

## Remaining high-value work

1. Sticky ownership with an explicit administrative disable transition.
2. Independent state-machine traces replayed against pure policy and production
   recipient C++.
3. Database/WAL/sidecar/staging/rename/fsync/directory-sync crash cuts with a
   domain oracle.
4. An executable convergence algebra.
5. Disposable process isolation for hostile SQLite artifacts.
6. A privacy, leakage, and key-lifecycle design separated from authentication.

## Claim discipline

No complete instrumented application, leak check, formal proof, remote network
behavior, crash atomicity, convergence algebra, confidentiality, metadata
hiding, anonymity, forward secrecy, or post-compromise recovery is claimed.
