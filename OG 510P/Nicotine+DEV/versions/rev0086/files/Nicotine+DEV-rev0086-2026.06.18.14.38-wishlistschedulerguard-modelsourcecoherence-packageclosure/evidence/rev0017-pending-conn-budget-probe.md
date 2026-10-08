# rev0017 pending-connection budget probe summary

PENDING-CONN-BUDGET-01 / U-181 was tested with a no-network harness against the three external source lanes.

## Results

| lane | same-user pending msgs | distinct pending users | distinct token count | offline token msgs retained | socket-cap buffered msgs | socket-cap key shape |
|---|---:|---:|---:|---:|---:|---|
| github-tag-3.3.10 | 1500 | 600 | 0 | 0 | 250 | address-keyed-or-other |
| github-branch-3.3.x | 1500 | 600 | 0 | 0 | 250 | init-keyed |
| github-branch-master | 1500 | 600 | 600 | 200 | 250 | init-keyed |

## Interpretation

- Repeated same-user peer messages are appended to a pending `PeerInit` while `GetPeerAddress` is unresolved. The witness used 1,500 messages and observed 1,500 retained pending messages in every lane.
- Repeated distinct users create one pending init per user; the witness used 600 users and observed 600 pending users/inits/messages in every lane.
- In `master`, ordinary initiation creates `ConnectToPeer` token state before address resolution; therefore the same buffered messages also sit behind `_indirect_token_init_msgs` while address resolution is pending. In `3.3.10` and `3.3.x`, token state is not created until the later direct-connect path, so the initial GetPeerAddress-only pending state is narrower.
- An offline `GetPeerAddress(0.0.0.0)` clears `_pending_init_msgs` and emits a `peer-connection-error` containing the buffered message list. In `master`, the indirect-token state still retains the buffered messages until indirect timeout cleanup.
- Socket-cap deferred connections retain the same `PeerInit` and continue accumulating later same-user messages. 3.3.10 keys this deferred state by address; 3.3.x/master key by init object.

## Decision

The behavior is real and reproduced, but rev0017 keeps it outside the strict document. The boundary is peer-message egress availability/backpressure under server timing, address-resolution delay, socket-cap pressure, or local/plugin/UI request fanout; it is not peer-only code execution or file disclosure.