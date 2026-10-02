# ADR 0285: add owner-local Ratox operations without changing Ratox v1

Status: accepted, 2026-09-01.

## Context

Ratox v1 already carried a bounded interactive PTY, explicit detach/resume, and authenticated close,
but the owner had to hand-author canonical profile records and learn a retained session ID from the
interactive banner. There was no read-only host capability probe and redirecting stdin into
`iotox terminal` immediately detached instead of behaving like a useful batch attachment.

These are operator-surface gaps, not reasons to revise the peer protocol. The remote must still be
unable to choose a profile, executable, arguments, environment, working directory, or forwarding
target.

## Decision

The binary now provides the canonical profile-store commands frozen in `future-cli-contract.md`:

```text
terminal-profile-list              terminal-profile-show PROFILE_ID
terminal-profile-template PROFILE_ID
terminal-profile-lint PATH         terminal-profile-install PATH
terminal-profile-remove PROFILE_ID
terminal-profile-bind PRINCIPAL_PUBLIC_KEY_HEX PROFILE_ID
terminal-profile-unbind PRINCIPAL_PUBLIC_KEY_HEX
```

Store commands require the same explicit `--ratox-profile-store PATH` and optional expected-owner UID
used by host activation. Templates are valid, disabled baseline profiles running `/bin/false`; an
owner must deliberately review the record, select the fixed executable, and enable it. Every
mutation starts from a complete strict store load, writes a private inode atomically, synchronizes
the containing directory, and strictly rereads the complete store. Removal refuses a referenced
profile. A running PTY already owns an immutable resolved profile and generation, so later store
mutation cannot alter that session; the Agent loads changes only at its next activation.

`host-capabilities [--ratox-cgroup-root PATH]` performs read-only host inspection plus isolated child
probes. It distinguishes unavailable, available/read-only, delegated, probe-denied, and live-proved
pidfd, seccomp, MDWE, Landlock, cgroup-v2, controller, PSI, and resource-interface states. The
default cgroup path is the caller's exact unified-hierarchy membership, not the hierarchy root.

The local control protocol advances from v1.47 to v1.48 and allocates operations 106 and 107 for:

```text
terminal-sessions [PEER_PUBLIC_KEY_HEX]
terminal-close SESSION_ID_HEX [PEER_PUBLIC_KEY_HEX]
```

The list is a content-free view of the one controller session currently retained by this Agent; it
is not an inventory of every inbound PTY hosted for other peers. Close requires the exact retained
session and optional peer identity. An attached session queues the existing authenticated CLOSE. A
detached session first performs the existing higher-epoch authenticated RESUME and queues CLOSE only
after attachment succeeds. Route or authority failure remains a typed failure and never degrades to
an unauthenticated kill.

`terminal ... --batch` and `terminal-resume ... --batch` skip local raw-mode and operator banners.
On local stdin EOF they inject one PTY EOT byte, retain the attachment, stream output, and return the
remote exit status. Batch does not accept a command line. A fixed program that does not interpret
PTY EOT or terminate can remain live; the operator must choose a batch-suitable profile or impose an
external deadline.

Ratox peer packet `0xA2`, Ratox v1 frame bytes, terminal socket v1 packets, profile v5 bytes, profile
selection, authority checks, and replay semantics are unchanged.

## Consequences

An owner can now create and validate the exact local policy, bind it, discover the retained session,
close it through the authenticated lifecycle, and use a pipeline-friendly terminal attachment from
one binary. This moves routine Ratox operation closer to forced-command SSH ergonomics without
adding arbitrary exec, forwarding, SSH compatibility, automatic resume, or daemon-independent PTY
supervision.

Remaining work is deployment qualification: positive delegated-cgroup/PSI outcomes on named target
kernels, long reconnect/leak/PTY soaks, independent security and operations review, and an explicit
production activation decision. `run-check` and canonical file-backed Agent configuration remain
separate operator work.
