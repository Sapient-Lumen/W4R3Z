# Ratox Agent dispatch source review — rev0018

Date reviewed: 2026-08-17 America/New_York

## Question

What exact upstream and Linux contracts should bound the first live, default-off Ratox Agent
integration, and which security claims must remain out of scope?

## Primary sources

```text
TokTok protocol specification
https://toktok.ltd/spec.html

TokTok c-toxcore source and public headers
https://github.com/TokTok/c-toxcore

Linux openat2 manual
https://man7.org/linux/man-pages/man2/openat2.2.html

Linux no_new_privs documentation
https://docs.kernel.org/userspace-api/no_new_privs.html

Linux seccomp filter documentation
https://docs.kernel.org/userspace-api/seccomp_filter.html

Linux Landlock userspace API
https://docs.kernel.org/userspace-api/landlock.html
```

## Source findings mapped to construction

### Custom-lossless ownership is explicit

c-toxcore exposes custom friend packets through a bounded API and distinguishes local send-queue
pressure from acceptance. IoTox therefore keeps the exact encoded Ratox packet in service-owned
storage until `send_lossless` succeeds. A SENDQ-style resource error is retryable without rollback;
other errors terminate or detach the stale route rather than inventing delivery.

The ordinary owner-thread adapter captures packet vectors by value so a command can cross threads.
That is correct for lifetime, but terminal traffic should not leave released copies in ordinary heap
storage. The Ratox path therefore uses a dedicated sensitive-lossless entry point: one shared command
payload owns the copied packet, every closure copy carries only a shared pointer, and the payload
securely wipes its allocation when the final reference is released on success, cancellation, queue
rejection, or failure. The c-toxcore SENDQ remains outside IoTox's memory-lifetime control.

On ingress, the custom-packet callback's event vector is the final transport-owned copy. Ratox
dispatch keeps it through the metadata-only generic journal update, then an exception-safe scope guard
wipes the backing allocation. The decoded Ratox payload, service replay state, outbound queue, and PTY
buffers have their own explicit wipe points.

Because retry can happen after the authority state changes, exact bytes are not sufficient metadata.
The retained record also preserves whether construction depended on `interactive.terminal`. Successful
admission results and session traffic are rechecked against the same friend/epoch/principal before a
later send; the canonical denial used to reject an unauthorized admission is explicitly marked as not
authority-bound.

Ratox uses packet ID `0xA2`, remains on custom-lossless transport, and is processed only after the
ordinary IoTox transcript handler has established an application-ready epoch. It does not reuse
human text, files, or custom-lossy packets.

### Negotiation must be bilateral and epoch-bound

A local HELLO bit is only an offer. The peer must independently advertise the same bit, and the
mutually confirmed transcript must contain the selected intersection. rev0018 consequently exposes
local support, local requirements, peer support, peer requirements, and negotiated features as
separate runtime facts. Tests freeze the one-sided case as not negotiated.

The local mask is chosen after Ratox's secure construction succeeds and before toxcore starts. It is
immutable after peer admission, so a failed or late local reconfiguration cannot change the meaning
of an existing online epoch.

### Thread-safe objects do not close a multi-object check/effect window

The upstream transport call, the signed ledger, and the peer-authority registry each have distinct
ownership boundaries. None makes an Agent sequence such as "check exact head, then spawn/write/send"
atomic across a concurrent local signed append. rev0018 therefore adds an outer Agent ordering lock
around accepted authority mutation, inbound Ratox admission, bounded PTY service, and retained
transport dispatch. The lock does not change the wire protocol or make the authority ledger own PTY
state; it only establishes whether the old-head Ratox cycle or the new signed head happened first.

### Path controls address resolution, not all filesystem attacks

`openat2` documents beneath/root/no-symlink/no-magic-link resolution controls and their precise
failure behavior. The rev0017 profile/PTY boundary already follows the same security principle with
component-by-component no-follow opens, owner/mode/type/link checks, and open-descriptor authority.
rev0018 does not weaken that boundary or allow the peer to provide a path, argv, environment, or
profile identifier.

The source also reinforces the nonclaim: path-resolution controls do not defend against an attacker
who already controls the daemon UID, writable executable content, or the running process.

### no_new_privs is a one-way privilege constraint, not confinement

The kernel documents `no_new_privs` as preventing `execve` from granting new privilege. It does not
remove already held privilege or constrain ordinary syscalls and filesystem access. IoTox verifies
`no_new_privs`, clears ambient capabilities, applies identity and limits, and keeps that evidence,
but does not label the resulting PTY a complete sandbox.

### seccomp and Landlock are future, separately qualified controls

Seccomp filter mode can restrict syscall execution but requires a deliberately designed policy and
careful interaction with `no_new_privs`. Landlock can restrict filesystem access for a process and
its descendants within the supported ABI. Neither is added opportunistically in rev0018 because an
untested policy can break required terminal behavior or create false assurance. R8 must decide a
reviewed deployment confinement profile, with namespaces and cgroups considered separately.

## Resulting rev0018 boundary

rev0018 adds a live but default-off Agent path with these exact stages:

```text
explicit enable
secure profile-store load and enabled-binding validation
PTY helper/factory and bounded-service validation
immutable pre-network HELLO feature selection
bilateral transcript-confirmed bit-23 negotiation
same-epoch stable-principal authority proof
exact current interactive.terminal decision
serialized exact-head decision and Ratox effect
canonical 0xA2 decode and attachment fencing
bounded Ratox session/PTy service
retained custom-lossless send ownership plus per-packet authority fence
content-free private lifecycle evidence
```

The construction does not prove an operator client, daemon-restart survival, public-network
reliability, two-host latency, complete process confinement, or production readiness.
