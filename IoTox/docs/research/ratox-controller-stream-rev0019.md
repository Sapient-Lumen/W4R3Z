# Ratox private controller stream source review — rev0019

Date: 2026-08-17 America/New_York

## Question

How can the existing default-off Ratox host boundary expose an operator terminal without weakening
network authority, losing byte-order truth, or turning a local pathname race into stream takeover?

## Sources rechecked

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/accept.2.html
https://man7.org/linux/man-pages/man3/termios.3.html
https://man7.org/linux/man-pages/man2/ioctl_tty.2.html
```

The Linux Unix-domain socket documentation establishes the relevant pathname, permissions,
`SOCK_SEQPACKET`, message-boundary, ordering, and peer-credential behavior. `accept4` supplies atomic
close-on-exec/nonblocking flags for accepted descriptors. `termios` and terminal-ioctl documentation
supply the local raw-mode and window-size behavior. These sources define platform behavior; they do
not audit or approve IoTox.

## Applied construction

rev0019 keeps finite administrative local control and terminal streaming separate. The new
`terminal.sock` is owner-private, same-user authenticated, single-attachment, message preserving, and
inode-safe across stale reclamation and shutdown. A canonical 32-byte local header and strict
packet-direction rules remain mandatory even though the kernel preserves records.

A pure controller state machine owns exact route/principal fencing, attachment identity, input/output
replay windows, immutable retained transport packets, cumulative acknowledgements, and bounded
ordered events. Agent code performs the live join only after current transcript negotiation and
remote-principal authentication. Client-only activation creates no profile resolver or PTY factory.

The one-binary client restores local terminal state through scoped ownership, propagates window size,
acknowledges output only after local write, and exposes explicit close/detach escapes. Local disconnect
requests detach rather than manufacturing an exit.

## Security conclusions

- Socket permission bits are not used as the only identity check; `SO_PEERCRED` is required.
- Stale socket cleanup is an ownership-and-inode transaction, not an unconditional unlink.
- Friend number is only a current route handle; resume remains bound to the authenticated principal
  and exact session ID.
- Replay memory is finite and sequence-aware; overlap is byte-compared before acceptance.
- Terminal bytes do not enter persistent runtime evidence.
- Client enablement does not imply host process capability.

## Remaining evidence gates

Separate-process controller replacement, daemon restart, route flap and queue-pressure scenarios;
full two-peer physical-host terminal streaming; long soak under loss/reconnect; and production support
policy remain outside this construction revision.
