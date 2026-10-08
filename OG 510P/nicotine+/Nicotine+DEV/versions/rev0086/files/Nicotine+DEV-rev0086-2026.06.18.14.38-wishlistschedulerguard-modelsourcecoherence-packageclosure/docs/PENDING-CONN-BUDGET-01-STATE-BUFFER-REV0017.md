# PENDING-CONN-BUDGET-01 / U-181 — pending peer-message buffer budgets

## Decision

**Audited-backlog verified, not strict-promoted in rev0017.**

The behavior is real across all checked source lanes, but the strongest boundary is availability/backpressure under server timing, address-resolution delay, socket-cap pressure, or local/plugin/UI fanout. It is not peer-only code execution, file disclosure, or a stronger provenance invariant than the existing strict PB-01 report-candidate.

## Source lanes checked

```text
github-tag-3.3.10
github-branch-3.3.x
github-branch-master
```

## Current-behavior proof

The maintainer-style witness is:

```text
maintainer_artifacts/pending-conn-budget-01/test_pending_peer_connection_budget_reproducer.py
```

It passed in all lanes:

```text
github-tag-3.3.10: 4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

The no-network probe records:

```text
evidence/rev0017-pending-conn-budget-probe.jsonl
evidence/rev0017-pending-conn-budget-probe.md
```

## Proven behavior

### Same-user pending `GetPeerAddress` growth

Repeated same-user peer messages sent while the peer address is unresolved reuse the same pending `PeerInit` and append to `init.outgoing_msgs`.

The witness sent 1,500 same-user peer messages and observed 1,500 retained pending messages in every lane.

### Global pending user growth

Repeated distinct usernames create one pending-init bucket per username. The witness sent one peer message to each of 600 usernames and observed 600 pending users, 600 pending init objects, and 600 retained messages in every lane.

In `master`, ordinary initiation also creates `ConnectToPeer` token state before address resolution, so the same 600 buffered messages are also reachable through `_indirect_token_init_msgs`. In `3.3.10` and `3.3.x`, this token state is not created until the later direct-connect path.

### Offline cleanup behavior

An offline server address response clears the `_pending_init_msgs` bucket and emits a `peer-connection-error` event containing the buffered messages.

In `master`, the corresponding indirect-token state remains after the offline address response and still retains the buffered messages until the indirect timeout path clears it.

### Socket-cap deferred connection growth

With a cached peer address and `_num_sockets >= MAX_SOCKETS`, the same `PeerInit` is held in `_pending_peer_conns`. Later same-user peer messages continue appending to its `outgoing_msgs` list. The witness used 250 messages and observed 250 retained messages in every lane.

`3.3.10` keys the deferred state by address. `3.3.x` and `master` key it by init object.

## Impact boundary

This is a peer-message egress/backpressure issue. The plausible trigger conditions are:

- local user actions that issue many peer-bound requests while address resolution is delayed;
- plugins or UI workflows that fan out browse/info/queue requests;
- server/MITM/test-server timing that delays or orders `GetPeerAddress`/connection responses;
- socket-cap pressure that defers direct connection attempts.

The proof does **not** demonstrate peer-only arbitrary memory exhaustion, code execution, or unauthorized file access.

## Fix-shape notes

A coherent fix should not drop legitimate Soulseek direct/indirect fallback behavior. It should add bounded accounting around queued peer egress state:

```text
- per-user pending init/message count budget;
- global pending init/message count budget;
- pending-message byte budget if message payloads are non-empty;
- TTL/generation cleanup for address-resolution and indirect-token state;
- deterministic rejection/error event when budgets are exceeded;
- compatibility tests for ordinary browse/info/download workflows and direct/indirect fallback.
```

Do not merge this into PB-01. PB-01 is about **who owns a primary connection**. PENDING-CONN-BUDGET-01 is about **how much outbound work may accumulate while no usable connection exists**.
