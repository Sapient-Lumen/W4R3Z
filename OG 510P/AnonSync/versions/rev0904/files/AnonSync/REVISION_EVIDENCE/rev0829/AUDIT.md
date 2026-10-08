# Rev0829 audit — one owner for durable reset and immutable evidence

## Mission-level finding

The heart of AnonSync is evidence-authorized convergence: an observation becomes
authority only after the invariant owner verifies the exact request, object,
process incarnation, namespace, owner generation, durable outcome, and remaining
recovery action. Rev0828 proved selected crash frontiers, but the application
still had two protocol owners: the CLI manually sequenced the pieces while the
test manually reproduced almost the same sequence.

That duplication was not harmless glue. It allowed recovery semantics to depend
on a local Boolean and catch order rather than on a type whose states are
validated together. The highest-leverage refactor was therefore not another
SQLite helper; it was removing protocol authority from the caller.

## New protocol owner

`sqlite_replay_ledger_reset_receipt_protocol.cpp` now owns the whole
application-level transition:

1. normalize the ledger and receipt paths;
2. reject every SQLite ledger-family path and existing hard-link alias;
3. derive the deterministic reset receipt identity;
4. render canonical receipt bytes and prepare a create-new immutable publication
   before the destructive transition;
5. execute the reset;
6. verify that returned prior state, normalized path, receipt/new identity,
   reason digest, connection owner generation, and state-advance flags are
   consistent with the request and expected receipt;
7. consume the exact prepared publication capability; and
8. return a directory-synced publication result or one validated typed error.

The error constructor is private and reached through an internal access class.
It rejects impossible combinations between failure phase, durable observation,
reset outcome, receipt digest, publication effect, and recovery action. This
prevents callers from manufacturing replay authority.

## Severe false-proof finding

`SqliteReplayLedgerResetDurableOutcomeError` was `final`, did not derive from
`std::nested_exception`, and was passed to `std::throw_with_nested`. The standard
helper can only create its nested wrapper by deriving from a suitable non-final
class. The final type was therefore thrown unchanged and the active exception
was lost.

The existing audit checked the spelling `throw_with_nested` and consequently
reported a property the executable did not have. Rev0829 repairs the type and
adds a runtime chain traversal that must find the injected post-commit cause.
The protocol oracle performs the same check for reset and publication failures.
This replaces token evidence with behavioral evidence.

## Choreography and waste removed

`runner.cpp` no longer owns canonical rendering, prepared-publication lifetime,
a durable-outcome Boolean, or phase-dependent catch translation. It calls one
protocol function and renders the typed failure. The crash/frontier test enters
the same implementation through one internal deterministic observer seam.
Public production callers do not receive observer hooks.

A focused link failure also exposed an undeclared dependency: the protocol used
reset implementation and documents through transitive edges. CMake now declares
reset and atomic-publication as public contract dependencies, documents and
SHA-256 as private implementation dependencies, and configure-time guards
prevent linking the focused oracle through `anonsync_core_lib`.

## Oracle coverage

The 442-check oracle proves the following application-owned states:

- preparation failure leaves the database, unrelated inode, and bytes intact;
- stale reset intent fails before durability and creates no receipt or temp;
- postcommit reset failure carries `Committed`, deterministic receipt identity,
  nested root cause, no attempted publication, and exact fresh-path replay;
- each of eleven publication failures carries the exact typed outcome/residue,
  nested cause, reset outcome, receipt identity, and replay action;
- process exit at each corresponding publication frontier reopens into a state
  classified by the same production implementation;
- replacement parents and competing final objects fail closed; and
- unknown residue or a first immutable publication is preserved rather than
  deleted or overwritten.

## Structural obligations

- SQLite reset audit: **99/99**;
- reset receipt audit: **42/42**;
- reset protocol audit: **24/24**;
- crash-frontier audit: **19/19**;
- atomic publication audit: **39/39**;
- aggregate: **223/223**.

The new source, headers, test path, audit, target, and package requirements are
all active release obligations.

## Remaining correctness edge

The current owner has a Boolean answer to “did the reset return a durable
outcome?” A contradictory result-binding failure after a normal reset return is
classified conservatively as post-durable and replay-authorized. The next model
should be tri-state: not durable; exact-request durable; or durable target
identity indeterminate/contradictory. Automatic replay must not be authorized in
the third state until independent inspection proves which durable identity won.

## Claim boundary

This is an application protocol over two resources, not a cross-resource atomic
transaction. It does not enumerate failures inside SQLite VFS operations or the
storage stack. The process oracle is Linux-specific. Hostile databases are still
interpreted in the long-lived process, and no distributed merge or privacy
protocol is established here.
