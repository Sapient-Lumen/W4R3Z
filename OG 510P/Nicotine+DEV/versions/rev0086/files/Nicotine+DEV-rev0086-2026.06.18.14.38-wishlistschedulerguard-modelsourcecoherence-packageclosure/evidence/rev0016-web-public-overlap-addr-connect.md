# rev0016 web/public-overlap packet — ADDR-CONNECT-01

## Exact/direct searches checked

No direct public issue match was found for these exact checked strings in the Nicotine+ issue tracker during this pass:

```text
"169.254.169.254"
"ConnectToPeer" "127.0.0.1"
"server-supplied" "peer address"
```

The result is not proof of novelty. It only supports the cube label: candidate no direct public match found, public-adjacent.

## Public-adjacent material

- Official Nicotine+ Soulseek protocol documentation describes `GetPeerAddress` as the server response path for a peer address and `ConnectToPeer` as an indirect connection mechanism.
- Nicotine+ issue #653 contains detailed public connection negotiation logs with `GetPeerAddress`, `ConnectToPeer`, direct/indirect attempts, and a LAN/private `192.168.1.1` accepted incoming connection, showing why blanket private-address rejection would be risky.
- Nicotine+ issue #3631 contains recent connection failure logs and indirect/direct connection symptom context, but not a direct address-class policy report.

## Public-overlap decision

```text
U-171: candidate no direct public match found; public-adjacent.
U-145: candidate no direct public match found; public-adjacent.
U-40/U-205: alias/support only.
U-189: known/upstream-changed backport note.
```
