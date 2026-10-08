# ADDR-CONNECT-01 / rev0016 — server-supplied peer addresses and outbound connection policy

## Canonical scope

```text
Canonical lead: U-171
Support path:   U-145
Alias/support:  U-40, U-205
Backport note:  U-189
```

This pass works the address/connect family as an audited hardening cluster, not as a strict/front-lane promotion.

## What rev0016 proved

A maintainer-style current-behavior witness was run against all three archived source lanes:

```text
github-tag-3.3.10:    9 passed
github-branch-3.3.x:  9 passed
github-branch-master: 9 passed
```

The witness monkeypatches `socket.socket` and records attempted `connect_ex()` targets. It does not open real network connections.

### GetPeerAddress pending-request path

For a local pending peer request, a server `GetPeerAddress` response with the target username drove a direct outbound connection attempt to the supplied address in all checked lanes:

```text
127.0.0.1:631       -> connect_ex attempted
169.254.169.254:80  -> connect_ex attempted
203.0.113.10:2234   -> connect_ex attempted
192.168.1.24:2234   -> connect_ex attempted; compatibility baseline, not a proposed reject
0.0.0.0:2234        -> no connect; offline baseline preserved
198.51.100.20:0     -> no direct connect; port-zero ordering differs by lane
```

### ConnectToPeer unsolicited-server-request path

For a server `ConnectToPeer` message with no local pending state for the claimed peer, the checked lanes attempted outbound peer sockets to the supplied address:

```text
127.0.0.1:631       -> connect_ex attempted
169.254.169.254:80  -> connect_ex attempted
192.168.1.24:2234   -> connect_ex attempted; compatibility baseline, not a proposed reject
```

## Source-shape summary

The source trace follows these functions in `pynicotine/slskproto.py`:

```text
3.3.10:
  _initiate_connection_to_peer: 754
  _connect_to_peer:             781
  _connect_to_peer_indirect:    827
  ConnectToPeer handler:        1276
  GetPeerAddress handler:       1300
  _init_peer_connection:        1694; port validation at 1710; connect_ex at 1727

3.3.x:
  _initiate_connection_to_peer: 806
  _connect_to_peer:             833
  _connect_to_peer_indirect:    879
  ConnectToPeer handler:        1356
  GetPeerAddress handler:       1380
  _init_peer_connection:        1776; port validation at 1792; connect_ex at 1810

master:
  _initiate_connection_to_peer: 822
  _connect_to_peer:             870
  ConnectToPeer handler:        1389
  GetPeerAddress handler:       1416
  _init_peer_connection:        1818; port validation at 1828; connect_ex at 1845
```

## Impact boundary

This is **not** peer-only unauthenticated RCE. It is a malicious Soulseek server, active MITM, compromised server-response stream, or malicious test-server boundary.

The meaningful hardening question is not “can an address field reach connect?” It can. The meaningful question is how to prevent server-driven connection storms or special-use-address probes while preserving real-world Soulseek connectivity.

## Fix-shape guardrails

Avoid these incoherent changes:

```text
- Do not blanket-block every private/RFC1918 address.
- Do not merge address-class policy with PB-01 primary-election/generation-binding.
- Do not turn invalid-port handling into a compatibility break for ordinary direct/indirect fallback.
```

Prefer this shape:

```text
- Reject invalid ports before indirect scheduling on 3.3.10/3.3.x if backporting.
- Add an explicit address-class policy for loopback, link-local, multicast, unspecified, documentation, reserved, and broadcast-like classes.
- Keep LAN/VPN/private-address compatibility behind configuration, known-local-network context, or explicit allowance.
- Add per-source/per-user/per-window budgets for server-driven ConnectToPeer and GetPeerAddress-driven connection attempts.
- Emit a clear log reason when a special-use address is dropped or allowed by compatibility policy.
- Add regression tests for loopback, link-local, LAN/private baseline, 0.0.0.0 offline baseline, port zero, and ordinary public routable addresses.
```

## Strict-lane decision

No promotion in rev0016. Keep ADDR-CONNECT-01 in the audited/ranked backlog as a verified hardening packet and compatibility-sensitive maintainer test candidate.
