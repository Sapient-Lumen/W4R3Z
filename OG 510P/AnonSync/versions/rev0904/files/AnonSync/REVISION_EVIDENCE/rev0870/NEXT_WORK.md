# Next work after AnonSync rev0870

## 1. Add receiver-side idempotency and an authenticated receipt envelope

The sender now fences local attempts, but timeout and crash can still duplicate
network delivery. Build a receiver owner keyed by authenticated operation ID and
sender epoch, commit admission/result exactly once, and return a signed or
channel-bound receipt that proves the receiver's durable outcome. Keep the local
claim capability distinct from that remote protocol object.

## 2. Make point reads fast without deleting the O(history) oracle

Use the schedule index to select the first ready intent under a bounded query,
then revalidate that candidate against exact local state. Incrementally update
digests/projection or maintain a separately attested scheduling view. Run every
optimized path differentially against the current full restore until randomized,
crash, migration, and tamper campaigns establish equivalence.

## 3. Give time and lease extension explicit authority

Define monotonic-time behavior, restart reconstruction, wall-clock rollback and
jump policy, maximum in-flight age, bounded heartbeat/extension, worker death,
and administrative recovery. A clock may authorize reclaim for liveness; it
must never independently authorize settlement.

## 4. Authenticate operation and membership authority

Bind canonical operation bytes to folder epoch, actor key, actor epoch,
membership epoch, and algorithm suite. Specify rotation, revocation, recovery,
compromised devices, old-epoch rejection, key loss, and retained evidence versus
current trust verdicts.

## 5. Exercise two actual replica processes

Create an authenticated two-process vertical slice with bounded anti-entropy,
exact operation requests, sender claims, receiver idempotency, and remote
receipts. Crash at claim commit, send, receiver admission, receiver commit,
receipt publication, sender settlement, retry release, and migration.

## 6. Bind payload materialization

Commit chunk identities and final content digest in the operation envelope.
Verify bytes before filesystem-visible publication and prove database/filesystem
recovery cannot expose a file without its exact committed operation or retain an
operation whose payload ownership is silently lost.

## 7. Add causal stability and retention lifecycle authority

Define checkpoint certificates, compaction, tombstone collection, old-replica
rejoin, revoked-history service, and reserved recovery capacity. Current heads,
local visibility, age, lease expiry, or sender settlement must never authorize
history deletion by themselves.

## 8. Measure physical work and privacy leakage

Bound SQLite pages, WAL/checkpoint growth, filesystem blocks, payload staging,
RSS, allocation, CPU, and wall time. Add hard work ceilings before exposing the
full oracle to remote input. Model identity, membership, graph shape, path,
pressure, retry timing, receipt linkage, padding, forward secrecy, and
post-compromise recovery as first-class privacy concerns.
