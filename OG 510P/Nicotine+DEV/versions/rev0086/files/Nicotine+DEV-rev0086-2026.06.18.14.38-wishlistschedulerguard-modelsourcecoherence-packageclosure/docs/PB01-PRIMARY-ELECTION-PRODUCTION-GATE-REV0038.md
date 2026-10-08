# PB-01 primary-election production gate — rev0038

## Scope

PB-01 covers two previously merged strict/front findings:

- **U-168**: a later incoming direct `PeerInit` can claim an existing username plus connection type and replace an established primary P/D connection, inheriting queued outgoing messages.
- **U-176**: a secondary P/D/F connection sharing the same `PeerInit` object can become primary after ordinary post-init activity because `_process_conn_incoming_messages()` assigns `init.sock = conn.sock` whenever it observes traffic on a secondary.

U-165 / PierceFireWall remains support context. The rev0038 gate deliberately preserves valid indirect fallback instead of treating every secondary connection as hostile.

## New fixed regression

```text
maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py
```

The regression has 11 cases:

```text
5 compatibility baselines:
- first valid direct P/D PeerInit becomes primary;
- valid PierceFireWall with no direct primary becomes primary;
- valid PierceFireWall can replace an unestablished direct attempt;
- secondary fallback can become primary after the established primary is closed.

6 fixed PB-01 invariants:
- later direct P/D PeerInit does not replace an established primary or migrate queued messages;
- secondary P/D/F post-init activity does not promote over an established primary;
- valid PierceFireWall secondary does not promote over an established direct primary after a peer message.
```

## Result matrix

| Scenario | github-tag-3.3.10 | github-branch-3.3.x | github-branch-master |
|---|---:|---:|---:|
| current source + fixed regression | 6 failed / 5 passed | 6 failed / 5 passed | 6 failed / 5 passed |
| selected patch + fixed regression | 11 passed | 11 passed | 11 passed |
| selected patch + rev0011 current witness | 6 failed / 4 passed | 6 failed / 4 passed | 6 failed / 4 passed |

The old current witness intentionally inverts under the selected patch because those six cases assert the behavior being removed. The four compatibility cases in the old witness still pass.

## Selected fix shape

The selected patch is intentionally narrower than a full architectural generation object:

1. `_replace_existing_connection(init)` now restores and keeps the existing username/type mapping when the mapped primary connection is already established, returns `False`, and lets `_process_peer_init_input()` close the new claimed direct connection.
2. Existing replacement remains allowed when the previous socket is absent or not established, preserving direct/indirect race compatibility.
3. The generic secondary-promotion block now checks the current primary connection. It promotes only when `init.sock` is absent, missing from `_conns`, or points to a non-established connection.
4. A secondary that receives traffic while an established primary is alive remains secondary; the code logs the event instead of mutating `init.sock`.

## Production decision

PB-01 is promoted from strict report-candidate to **production-gated maintainer packet** in this cube. External filing/review remains outside the cube. The selected patch is a minimal maintainer-reviewable shape; a larger future refactor could still introduce explicit connection generations, but the rev0038 regression states the invariant that should survive either implementation.
