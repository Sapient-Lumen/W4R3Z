# ADR 0132: fence synchronization pulls across online epochs

Status: accepted

Date: 2026-08-21

## Decision

An active synchronization pull belongs to one exact authenticated peer online epoch. When that peer
goes offline, the subscriber terminally fails the old job before transport or filesystem cleanup.
It closes admitted receives, discards attempt-scoped staging, finishes signed active-attempt truth,
and fences scheduler reservations. An inability to send a transport CANCEL cannot preserve local
commit authority. Any unresolved local cleanup remains a failed-job tombstone and blocks replacement;
pull admission retries that cleanup without repeating an already attempted transport effect. Late
HEAD, object, offer, and terminal events from the retired epoch remain ineligible.

IoTox does not silently rebind the old job or a c-toxcore file number to a later connection. After a
strictly higher confirmed and authorized epoch appears, the operator may issue a fresh `sync-pull`.
That request receives a new process-local job ID and new FileIds. Already committed immutable objects
remain reusable, but partial transport staging is private attempt state and is not a resumable object.
The fresh pull must independently verify both complete objects and accept the signed HEAD last before
manual exact-token activation.

The Sandwurm `sync-file-disconnect` gate freezes the observable boundary. It begins a rate-shaped
8 MiB pull, waits for positive c-toxcore position and admitted receives, blackholes both guest TAPs
until both peers report offline, and requires the subscriber's old job to be failed with no live
receive, staging, accepted HEAD, or activation. Only after both peers confirm a higher epoch does the
client explicitly retry and converge. Both peers must first retain one higher confirmed and
authorized epoch for 50 consecutive 100 ms samples. An early scientific cell proved that a first
confirmed callback can flap again after qdisc restoration; it is connection truth, not yet a stable
bulk-admission point.

## Consequences

- Connectivity recovery and transfer continuation are separate facts. A recovered Tox session does
  not authorize an old file handle.
- A first confirmed reconnect is not sufficient admission evidence after a hard partition. The
  laboratory requires a bounded five-second same-epoch stability window before bulk retry.
- The first complete-object slice performs safe whole-object retry after disconnect. It does not yet
  claim byte-range continuation or reuse of partial staging.
- Verified immutable objects committed before loss can still eliminate work on a later pull. Partial
  unverified bytes cannot.
- Status retains the failed old job until explicit retry supersedes it, preserving a content-free
  explanation of the boundary.
- This rule composes with explicit cancellation: both terminally fence local commit eligibility
  before best-effort transport control and cleanup.

## Evidence

The owned subscriber check admits both object receives, injects one transport-cancel failure, retires
the exact epoch, requires terminal failure, two at-most-once cancellation effects, empty staging and
signed attempt truth, and then requires cleanup settlement plus a new job ID on a higher epoch. The
strict Sandwurm verifier has a positive and negative
`sync-file-disconnect` fixture. Genuine direct-UDP and forced-TCP observations now pass at clean
source commit `4f051fe6ed37e438858af7de21becaa3d528474d`; exact bindings, scientific failures, and nonclaims
are retained in `../evidence/2026-08-21-sandwurm-sync-disconnect.md`. The evidence does not turn
whole-object retry into a byte-range-resume claim.
