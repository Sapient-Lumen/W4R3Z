# ADDR-CONNECT-01 maintainer report skeleton

## Summary

Server-supplied peer-address messages can drive outbound peer socket attempts to special-use addresses. `GetPeerAddress` does this for locally pending peer requests, and `ConnectToPeer` can do this as a server request without local pending state.

## Boundary

This is malicious-server / active-MITM / compromised server-response-stream hardening, not peer-only unauthenticated code execution.

## Current behavior witness

`maintainer_artifacts/addr-connect-01/test_peer_address_policy_reproducer.py` currently passes on 3.3.10, 3.3.x, and master. The test replaces sockets with a fake socket and asserts current behavior.

## Compatibility note

Do not blanket-reject private addresses. LAN/VPN/private peer routes appear in real connection flows. Recommended remediation should distinguish loopback/link-local/reserved/special-use addresses from legitimate local-network routes and should be configurable or context-aware.

## Suggested regression plan

- Current-behavior witness first.
- Fixed-behavior tests for loopback/link-local/special-use handling.
- Compatibility tests for LAN/private route allowance.
- Invalid-port ordering test for 3.3.x/3.3.10 backport work.
- Per-user/per-window budget tests for server-driven connection requests.
