# PB-01 production-ready maintainer report draft — rev0038

## Title

Peer primary election can be replaced by claimed `PeerInit` username/type and by secondary post-init traffic

## Summary

Nicotine+ currently allows two related primary-election transitions in `pynicotine/slskproto.py`:

1. A later incoming direct `PeerInit` for the same username and connection type can replace an already-established primary P/D connection and inherit queued outgoing messages.
2. A secondary P/D/F connection sharing the same `PeerInit` object can become primary after ordinary post-init activity, because the generic secondary-handling block assigns `init.sock = conn.sock` while the established primary is still alive.

The compatibility-sensitive part is that direct and indirect Soulseek connection attempts can legitimately race. The proposed regression therefore preserves first direct connections, valid PierceFireWall fallback, replacement of an unestablished direct attempt, and secondary promotion after the primary is gone. It only blocks replacement/promotion while an established primary remains alive.

## Affected area

```text
pynicotine/slskproto.py
_replace_existing_connection()
_process_peer_init_message()
_process_conn_incoming_messages()
```

## Reproducer

Add the regression file:

```text
maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py
```

Run from outside a checkout:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q test_peer_connection_primary_election_fixed_regression.py
```

Current archived source result:

```text
github-tag-3.3.10:   6 failed, 5 passed
github-branch-3.3.x: 6 failed, 5 passed
github-branch-master: 6 failed, 5 passed
```

The five passing cases are compatibility baselines. The six failing cases are the fixed PB-01 invariants.

## Expected behavior

- A first valid direct P/D `PeerInit` should become primary.
- A valid PierceFireWall with no direct primary should become primary.
- A valid PierceFireWall should be able to replace an unestablished direct attempt.
- A secondary should be able to become primary after the previous established primary is closed.
- A later direct `PeerInit` should not replace an already-established primary or inherit queued messages solely by claiming the same username/type.
- A secondary P/D/F connection should not become primary merely because it sends ordinary post-init traffic while an established primary remains alive.

## Actual behavior

Current source replaces the established primary in the later direct `PeerInit` cases and promotes the secondary in the P/D/F post-init cases.

## Selected fix shape

The attached rev0038 patch skeleton implements an established-primary guard:

- `_replace_existing_connection()` returns a boolean and rejects replacement when the existing username/type mapping points to an established primary connection.
- `_process_peer_init_message()` closes the new claimed direct connection when replacement is rejected.
- The secondary-promotion block checks the current primary and promotes only when no established primary remains.

Patched-lane result:

```text
github-tag-3.3.10:   11 passed
github-branch-3.3.x: 11 passed
github-branch-master: 11 passed
```

## Compatibility notes

The patch does not reject all secondary connections. A valid PierceFireWall secondary can stay open behind an established direct primary. It simply cannot take over `init.sock` until the established primary is absent, removed, or not established. This preserves the direct/indirect race behavior while preventing implicit primary stealing.

## Public overlap

Public protocol documentation confirms the direct/indirect PeerInit/PierceFireWall model, that PeerInit's token is zero/ignored today, and that only one active P connection to a peer is expected. Public GitHub issues show connection-lifecycle adjacency, but this cube did not capture an exact public duplicate of the specific established-primary replacement plus secondary-promotion chain.
