# Rev0839 next work

## P0 — authenticate lifecycle evidence

Define an authenticated heartbeat envelope bound to the exact checkpoint/session,
durable owner generation, service instance, process-incarnation observation, schema,
key epoch, monotonic sequence, and final/release evidence. Keep signature validity
separate from authorization. Add replay, substitution, downgrade, truncation, key-
rotation, and forged-denial-of-service corpora.

## P0 — own the live process reference where supported

Prototype a daemon/monitor boundary that obtains a pidfd at process creation and holds
it for the owner generation. Compare it with the current reopen-and-observe design.
Specify fallback behavior for old Linux kernels, procfs restrictions, containers, PID
namespaces, and permission failures. Do not treat fallback failure as process death.

## P0 — Windows and namespace validation

Run the Windows creation-FILETIME branch under native CI, including access-denied,
exited-process, PID-reuse, and handle-wait cases. Add Linux PID-namespace and procfs
mount-option tests. The current cloudtainer exercised Linux `/proc` with `pidfd_open`
returning `ENOSYS`, not the pidfd or Windows branches.

## P1 — narrow the heartbeat serializer surface

`encode_sync_daemon_heartbeat_document_or_throw` still receives large domain option and
result structures through the internal umbrella. Introduce a small
`HeartbeatPublicationView` containing only validated publication fields. This would
reduce recompilation and make authority ownership visible at the type boundary.

## P1 — monotonic suspicion and clock rollback

The stale horizon uses epoch time. Add a clock-suspicion model that records boot/clock
context, rejects backward movement and implausible jumps, and distinguishes operator
wall time from monotonic elapsed time. Preserve a conservative path after reboot, where
monotonic counters cannot be compared directly.

## P1 — cross-resource crash-cut oracle

Enumerate cuts around durable owner renewal/release, heartbeat temp creation, write,
file sync, rename, directory sync, and restart. Verify the combined database + heartbeat
protocol, including stale temporary files and finality. SQLite VFS fault injection is a
model for the database half; AnonSync needs a domain oracle spanning every artifact.

## P1 — checked-in quiescent validation driver

Replace ad hoc shared-container command streams with a tested driver that owns a unique
work root and process group, records the active projection before each gate, excludes
interrupted evidence, and publishes by no-replace atomic rename only after package
verification. The rev0839 evidence records why this is not mere build convenience.

## P2 — executable convergence and privacy models

Continue the larger mission: define each durable transition's algebra under duplicate,
reordered, lost, partitioned, retried, concurrent update/delete, restart, schema epoch,
and key epoch traces. In parallel, publish a threat/leakage matrix and design payload
confidentiality, device enrollment, key rotation/revocation/recovery, forward secrecy,
post-compromise recovery, metadata minimization, and secure erasure.
