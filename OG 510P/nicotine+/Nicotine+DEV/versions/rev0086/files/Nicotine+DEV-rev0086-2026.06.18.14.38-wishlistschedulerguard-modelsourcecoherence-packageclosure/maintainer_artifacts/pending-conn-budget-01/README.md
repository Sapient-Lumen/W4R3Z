# PENDING-CONN-BUDGET-01 maintainer witness

This directory contains a current-behavior pytest witness for U-181:

```text
Pending PeerInit/GetPeerAddress state can buffer outbound peer messages without per-user or global budgets.
```

Run from an upstream checkout:

```bash
python -m pytest test_pending_peer_connection_budget_reproducer.py
```

or from this cube with an external source tree:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest test_pending_peer_connection_budget_reproducer.py
```

The tests intentionally assert current behavior, not a proposed fix. They cover:

- repeated same-user peer messages while `GetPeerAddress` is pending;
- many distinct usernames creating pending-init and, in master, indirect-token state;
- offline `GetPeerAddress` cleanup behavior;
- socket-cap deferred peer connection buffering.

The result is useful as a regression/hardening witness, but rev0017 keeps it outside the strict/high-priority document because the boundary is availability/backpressure and server-timing sensitive.
