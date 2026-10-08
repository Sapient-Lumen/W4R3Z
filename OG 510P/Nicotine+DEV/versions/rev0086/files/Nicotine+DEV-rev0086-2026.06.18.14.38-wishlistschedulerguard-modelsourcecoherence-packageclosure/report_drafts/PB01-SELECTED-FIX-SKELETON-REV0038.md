# PB-01 selected fix skeleton — rev0038

## Invariant

Do not mutate a username/type primary connection binding while it points to an established primary, unless an explicit future generation/election mechanism authorizes the change.

## Minimal patch shape

```python
def _replace_existing_connection(self, init):
    username = init.target_user
    conn_type = init.conn_type

    if username == self._server_username:
        return True

    init_key = username + conn_type
    prev_init = self._username_init_msgs.pop(init_key, None)

    if prev_init is None or prev_init.sock is None:
        return True

    prev_conn = self._conns.get(prev_init.sock)

    if prev_conn is None:
        return True

    if prev_conn.is_established:
        self._username_init_msgs[init_key] = prev_init
        return False

    init.outgoing_msgs = prev_init.outgoing_msgs
    prev_init.outgoing_msgs = []
    self._close_connection(prev_conn)
    return True
```

Caller:

```python
init = msg
if not self._replace_existing_connection(init):
    return None
```

Secondary promotion:

```python
if conn.sock is not None and init.sock is not conn.sock:
    primary_conn = self._conns.get(init.sock)

    if init.sock is None or primary_conn is None or not primary_conn.is_established:
        init.sock = conn.sock
```

## Maintainer review points

- Confirm whether established-primary duplicate direct `PeerInit` should be closed immediately or kept as a secondary. The rev0038 patch closes it by returning `None` from `_process_peer_init_message()`.
- Confirm whether F-connection secondary promotion should ever be allowed while an F primary is alive. Rev0038 blocks generic promotion while the primary is established; transfer-token/session-specific routing remains covered separately by U-123.
- Consider a future explicit generation/election object if more nuanced reconnect semantics are needed.
