# rev0016 worklog

## Target

ADDR-CONNECT-01 / U-145 + U-171, with U-40/U-205 aliases and U-189 branch-specific port-validation note.

## Work performed

- Built no-network address-policy probe and maintainer-style pytest witness.
- Ran witness across all three archived source lanes.
- Traced ConnectToPeer/GetPeerAddress source paths and `_init_peer_connection()` address handling.
- Performed hard public-overlap searches for internal/special-use address terms and ConnectToPeer/GetPeerAddress phrasing.
- Pruned aliases into one coherent address-policy family.
- Kept strict document at 3 candidates.
- Selected U-181 as the next adjacent budget/backpressure target.

## Result

```text
github-tag-3.3.10:    9 passed
github-branch-3.3.x:  9 passed
github-branch-master: 9 passed
strict candidates:    3 retained
new strict promotions:0
```
