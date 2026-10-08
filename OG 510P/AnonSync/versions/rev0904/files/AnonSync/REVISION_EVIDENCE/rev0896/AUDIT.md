# AnonSync rev0896 audit

## Heart of the mission

Exact authorized history and live owned capabilities remain the authority. The
product may summarize durable state, but summaries must never create authority.
Rev0896 is valuable because it gives the product spine a status surface that is
computed by existing owners and causal model restoration rather than by an
unreviewed parallel database reader.

## Correction made

The severe product gap after rev0895 was observability: the executable could
enqueue, publish membership, send once, and serve once, but could not report the
condition of the replica it had just touched. `anonsync_replica status` now
reports replica, outbox clock/lease, payload, effect, and anchored membership
cutpoints. The process proof validates that report in the queued, settled
sender, and published receiver states.

## Refactor/audit scope

The C++ refactor deliberately stayed small: status summary structs/functions,
JSON boolean emission, clock health naming, and paired option validation. The
important design constraint is that status is a composition of owners, not a new
schema authority. The helper boundaries keep the command readable and make the
zero-clock high-water case conservative.

## Waste and forward correction

The full Debug suite eventually passed, but the build required resumed
invocations in this cloudtainer. That reinforces the earlier build-waste
finding: a narrow executable change still has a large compile/test fan-out. This
can be corrected gradually by consolidating target structure, moving legacy
self-test material farther from product builds, and making product-spine checks
cheap enough to run by default while retaining full registry verification for
release sealing.

## Remaining gaps

The largest missing piece is now the bounded durable operational loop: status,
claim, send/serve, recovery, shutdown, clock recovery, and retry scheduling need
one owner-driven runtime. Directory/tombstone/rename semantics, reachability and
crash-safe garbage collection, chunking/resume, indexed performance, SQLite
3.53.4 acquisition, and privacy/anonymity layers remain explicitly unclaimed.
