# ADR 0284: separate synchronization confidence from backup trust

Status: accepted, 2026-09-01.

## Context

The founding-machine roadmap is complete and the bounded IoTox/Resilio shadow passes. That result
answers whether IoTox can synchronize its supported regular-file model under the named construction
conditions. It does not answer whether an operator can recover after every synchronized device
faithfully propagates an authorized deletion, damaged content, compromised authority, or an
operator mistake.

The founding operator keeps true backups of the drives, including the IoTox development machine,
and explicitly does not yet want precious data to depend on IoTox. The repository needs to preserve
that distinction after the excitement of a passing synchronization gate.

## Decision

IoTox synchronization is never described as a backup by itself. A true backup must be independently
versioned and restorable after total loss or compromise of every IoTox namespace member. At least
one backup copy must be outside the write and deletion authority of the IoTox synchronization
principals it protects.

Repository completion and precious-data trust are separate decisions:

- the current accepted use is disposable or noncritical synchronization, and important working data
  only when an independently restorable backup already exists;
- an operator's real backup satisfies a necessary containment condition but does not expand IoTox's
  filesystem, crash, security, performance, or deployment evidence; and
- recommending IoTox for precious working sets requires the explicit graduation gates in
  `docs/sync-trust-graduation.md`. Those gates are product hardening, not a reopening of the completed
  founding roadmap.

No status output, successful sync, checkpoint, pin, CAS object, conflict copy, quarantine directory,
or retained branch may be labeled an independent backup. They share some combination of authority,
storage, implementation, or failure domain with the live namespace.

## Consequences

The product can honestly say that it now replaces an incumbent synchronization path inside its
bounded model while also saying that precious originals need independently tested recovery. A
propagated deletion is correct synchronization, not proof of backup failure.

Future operator UX should make unsupported filesystem entries, unresolved conflicts, repair state,
capacity, and backup assumptions visible. It must never infer that a mounted snapshot, another
writable peer, or merely retained CAS history is independent enough to protect the user.

