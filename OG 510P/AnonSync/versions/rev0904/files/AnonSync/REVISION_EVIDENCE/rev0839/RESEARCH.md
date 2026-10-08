# Rev0839 research: process identity, liveness, and authority

## Primary references

- Linux `/proc/<pid>/stat`: https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
- Linux `pidfd_open(2)`: https://man7.org/linux/man-pages/man2/pidfd_open.2.html
- Linux procfs documentation: https://docs.kernel.org/filesystems/proc.html
- Microsoft `OpenProcess`: https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess
- Microsoft `GetProcessTimes`: https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes
- SQLite crash testing: https://sqlite.org/testing.html
- SQLite VFS fault-injection surface: https://sqlite.org/vfs.html
- Chandra and Toueg, *Unreliable Failure Detectors for Reliable Distributed Systems*: https://doi.org/10.1145/226643.226647

## Design conclusions

Linux documents field 22 of `/proc/<pid>/stat` as the process start time after boot.
Combining that value with the boot UUID makes PID reuse and reboot observable without
pretending the tuple is secret or authoritative. A pidfd is a stronger live kernel
reference and is pollable, but `pidfd_open` can still fail or be unavailable. Rev0839
therefore treats it as optional race narrowing and returns typed indeterminate outcomes
instead of silently converting observation failure into permission.

Windows exposes process creation time through `GetProcessTimes` after obtaining a
process handle. Rev0839 includes that implementation path, but this Linux cloudtainer
neither compiled nor executed it; the release gate explicitly blocks a Windows claim.

A heartbeat is an application-level failure detector. Timeouts can suspect a paused,
partitioned, overloaded, clock-skewed, or alive process. Failure-detector theory says
that liveness conclusions require assumptions about timing and communication. The
project should continue to express a stale deadline as suspicion, not proof. Durable
owner generation remains the mutation boundary; process incarnation only adds a
fail-closed observation before admitting a replacement daemon.

## Speculation

The strongest local design may be a monitor that holds a pidfd from process creation,
not one reopened from a document PID. The monitor could bind that kernel reference to
the durable owner generation and publish a small authenticated transition when the
process exits. That still would not solve remote partitions, host reboot, or monitor
failure, but it would remove the reopen race on supported Linux kernels.

Heartbeat authenticity is the next major gap. Because the document can be forged, an
attacker with write access can currently cause denial of service by publishing plausible
non-final evidence. A MAC or signature must be bound to session, checkpoint, owner
generation, service incarnation, process observation, schema version, and a monotonic
sequence or epoch. The verifying key lifecycle must not create a second untracked
source of authority.

Longer term, the process/lifecycle work should feed a deterministic convergence model.
A daemon takeover is one transition in the replicated state machine, and should be
classified by commutativity, idempotence, causality, epoch compatibility, and required
coordination. Cross-resource crash tests should cut between database owner updates,
heartbeat publication, directory sync, and external effects, then check one domain
oracle rather than only SQLite structural validity.
