# rev0016 ADDR-CONNECT-01 source trace

Source trees are external inventory from the rev0003 bundle and are not embedded in this cube.

## github-tag-3.3.10

```text
pynicotine/slskproto.py:1276-1286
  ConnectToPeer server handler reads msg.user, msg.ip_address, msg.port, msg.conn_type, msg.token, builds PeerInit, and calls _connect_to_peer(username, addr, init, response_token=token).

pynicotine/slskproto.py:1300-1318
  GetPeerAddress server handler pops pending init messages and calls _connect_to_peer(username, addr, init) unless msg.ip_address is 0.0.0.0.

pynicotine/slskproto.py:1694-1728
  _init_peer_connection validates port after optional indirect scheduling, then creates a socket and calls sock.connect_ex(addr).
```

## github-branch-3.3.x

```text
pynicotine/slskproto.py:1356-1366
  ConnectToPeer server handler follows the same server-supplied address to _connect_to_peer path.

pynicotine/slskproto.py:1380-1398
  GetPeerAddress pending-init path follows the supplied address into _connect_to_peer unless offline.

pynicotine/slskproto.py:1776-1810
  _init_peer_connection validates port after optional indirect scheduling, then calls sock.connect_ex(addr).
```

## github-branch-master

```text
pynicotine/slskproto.py:1389-1400
  ConnectToPeer handler validates connection type, builds PeerInit, and calls _connect_to_peer(username, addr, init, pierce_token=pierce_token).

pynicotine/slskproto.py:1416-1434
  GetPeerAddress pending-init path follows the supplied address into _connect_to_peer unless offline.

pynicotine/slskproto.py:1818-1845
  _init_peer_connection validates port before creating a socket, then calls sock.connect_ex(addr).
```
