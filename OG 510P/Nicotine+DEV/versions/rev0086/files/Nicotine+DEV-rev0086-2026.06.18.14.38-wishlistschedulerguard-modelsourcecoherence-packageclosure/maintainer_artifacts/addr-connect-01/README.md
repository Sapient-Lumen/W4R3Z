# ADDR-CONNECT-01 maintainer artifact

File:

```text
test_peer_address_policy_reproducer.py
```

Run from an upstream checkout:

```bash
python -m pytest test_peer_address_policy_reproducer.py
```

Or from elsewhere:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest test_peer_address_policy_reproducer.py
```

This is a **current-behavior witness**, not a proposed fixed-behavior test. It verifies that server-supplied addresses in `GetPeerAddress` and `ConnectToPeer` reach the outbound peer socket path. It also preserves compatibility baselines: `0.0.0.0` is offline, port zero does not open a direct socket, and LAN/private addresses are recorded as legitimate compatibility cases rather than automatically bad.
