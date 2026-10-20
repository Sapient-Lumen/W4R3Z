# ADR 0104: reconcile synchronization duplicates after uncertain commit

- Status: accepted and implemented
- Date: 2026-08-20
- Scope: exact retries after guarded local root commit uncertainty
- Depends on: ADR 0103

## Context

An atomic root rename can land before a later filesystem synchronization error is reported. ADR 0103
correctly leaves the signed successor pending in that case. An exact retry then observes the new root
as a duplicate. Returning the duplicate immediately would preserve correct content but leave the
guard pending indefinitely.

## Decision

1. Exact duplicate publication, accepted-HEAD, activation, and retention-pin operations reconcile the
   actual four-root head against the signed guard before reporting the duplicate.
2. An unpin retry whose record is already absent performs the same reconciliation before returning
   its idempotent false result.
3. Rejected stale, forked, unauthorized, malformed, or conflicting operations do not gain permission
   to repair state merely because they reached a mutation entrance.
4. Inject both uncertainty sides: failure before root replacement and failure after a real root
   replacement. Require the same request to recover and leave a committed guard with no pending head.

## Consequences

- Idempotent retry is now also crash-state cleanup, not just result equivalence.
- A read-only reachability pass continues to classify pending state without signing or repairing it.
- Actual I/O fault matrices and quarantine/GC containment remain later gates.
