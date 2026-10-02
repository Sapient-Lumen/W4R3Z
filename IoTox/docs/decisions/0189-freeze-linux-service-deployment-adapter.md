# ADR 0189: Freeze the Linux service deployment adapter

Status: accepted construction adapter, 2026-08-27.

## Context

M7 had a complete signed delivery, staging, selection, confirmation, rollback, release-key, and
recoverable-retention lifecycle, but its only payload kind was explicitly inert. Treating that
opaque kind as executable through a new command-line flag would silently reinterpret old signed
bytes and violate the rule that receipt is not execution authority.

A general archive installer or remote command would also multiply authority and path surfaces before
one concrete target contract had been qualified. The first adapter therefore needs one exact native
service image, no remote argv or extraction, a readiness predicate, and deterministic recovery to
the prior signed slot.

## Decision

Assign signed manifest payload kind 2 to linux-service-v1. Update policy v3 binds that exact kind
and requires a positive release-signer policy epoch. Existing policy v1/v2 records remain canonical
only for opaque-slot-v1.

Bind payload kind into signed update state using bytes 11 and 12 of the existing reserved header:
zero retains the exact historical opaque encoding; value 2 names a present confirmed or candidate
Linux service revision. No value 1 encoding is introduced. Old opaque state therefore remains byte
and signature stable, while an old implementation rejects new service state and a new implementation
rejects policy/state kind drift.

Keep persistent slots mode 0400. The adapter reopens and rehashes the exact selected slot into an
anonymous executable memfd, verifies its byte count, digest, descriptor stability, and required
kernel seals, then uses an exact IoTox helper plus fexecve. The helper arms parent-death and
no-new-privileges, creates a new session/process group, requires close_range, removes ambient
descriptors, and supplies only fixed revision metadata plus readiness descriptor 3.

Freeze readiness as IOTOXSR1 followed by release-sequence-u64be. Gate owner-local confirmation on a
live adapter that has emitted that exact record for the exact candidate. Candidate exit,
malformed/closed readiness, or timeout invokes signed rollback and relaunches the confirmed service
through the same sealed-image path. Confirmed service death never lowers the anti-rollback high-water.

Keep remote authority unchanged: peers may stage only through existing install.firmware; apply,
restart, health confirmation, helper choice, and adapter activation remain owner-local.

## Consequences

- Old opaque payloads cannot become executable because configuration changed.
- A persisted update slot never receives execute permission and the executed image cannot be
  modified after sealing.
- There is no archive traversal, remotely supplied argument, environment, command, or pathname.
- Readiness is a signed-release program liveness declaration, not independent hardware attestation;
  the one-use owner health token remains mandatory.
- Same-process-group descendants are terminated with the service. A deployment manager must provide
  whole-cgroup ownership against a payload that deliberately re-sessions.
- Native Linux ELF, dynamic-loader availability, service ABI, and target health semantics are release
  engineering responsibilities.
- A bootable A/B adapter, recovery partition/media, secure boot, physical power cuts, flash wear,
  hardware monotonic state, and representative-hardware evidence remain open.

## Qualification

The owned registry covers policy v3 and manifest/state kind binding, old opaque canonical
compatibility, slot-selection verification, sealed-image launch, helper descriptor/exec handshake,
readiness, malformed inputs, child exit, bounded stop, confirmation gating, candidate failure
rollback, and confirmed-service relaunch. The retained Sandwurm and full compiler/sanitizer evidence
for rev0044 is recorded separately when that matrix is complete.
