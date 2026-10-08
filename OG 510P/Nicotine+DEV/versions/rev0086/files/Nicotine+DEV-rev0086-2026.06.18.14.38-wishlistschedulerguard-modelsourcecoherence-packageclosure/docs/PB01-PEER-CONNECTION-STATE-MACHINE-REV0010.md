# PB-01 peer-connection state-machine proof — rev0010

## Scope

This revision focused on the peer-connection binding cluster:

- **U-168** — incoming direct `PeerInit` can replace an existing peer/distributed connection using only the claimed username and connection type.
- **U-176** — a secondary peer/distributed/file connection can be promoted to primary on post-init traffic without a generation/source election check.
- **U-165** — PierceFireWall token handling is used only as supporting context for one valid secondary-P setup path.

The work used the externally inventoried rev0003 source bundle only as an analysis input. The full source trees are intentionally not embedded in this compact cube.

## Result

The rev0010 state-machine probe passed on all three source lanes:

| lane | U-168 P replace | U-168 D replace | U-176 P promote | U-176 D promote | U-176 F promote | PierceFireWall secondary P promotes |
|---|---:|---:|---:|---:|---:|---:|
| github-tag-3.3.10 | True | True | True | True | True | True |
| github-branch-3.3.x | True | True | True | True | True | True |
| github-branch-master | True | True | True | True | True | True |

This is enough to upgrade PB-01 from a vague peer-binding cluster into one concrete strict/front-lane report-candidate. It is still not production-ready disclosure text: the proof is handler/state-machine level, and a maintainer-grade regression should be derived before external use.

## U-168 observation

The probe established a primary connection for a victim username and then delivered a new incoming direct `PeerInit` that claimed the same username and connection type. In every lane, P and D replacement reproduced. The old primary was closed/removed, the username/type init mapping moved to the incoming connection, and a queued outgoing message attached to the old init could be sent on the replacement connection.

Practical interpretation: the replacement rule is claim-keyed by username plus connection type, not by a durable source/generation election.

## U-176 observation

The probe attached a secondary connection to the same init object and delivered post-init data. In every lane, secondary promotion reproduced for P, D, and F. The old primary remained open, but `init.sock` moved to the secondary socket.

Practical interpretation: the post-init promotion rule is broad. It is not limited to a deliberate reconnect/failover election.

## PierceFireWall support path

The P-connection subprobe installed a valid indirect token table entry, accepted a `PierceFireWall` connection as secondary while a direct primary was still active, then processed an ordinary peer message on the secondary. In every lane, the secondary became `init.sock` after that post-init message. This makes U-165 supporting context for PB-01, but not a standalone first report in this revision.

## Coherence decision

PB-01 is merged, not split:

- **PB-01a / U-168**: direct incoming `PeerInit` replacement by claimed username/type.
- **PB-01b / U-176**: secondary post-init primary promotion.
- **U-165**: indirect/PierceFireWall context and possible precondition; not standalone until token/source-binding evidence is stronger.
- **U-171**: server-supplied address validation; related but separate.
- **U-181**: pending-message buffering/backpressure; related but separate.

The merge avoids a bad fix set such as “never replace PeerInit” plus “close every secondary connection.” A compatible fix likely needs one connection generation/election model used consistently by direct PeerInit, indirect PierceFireWall, file-transfer F sockets, and distributed D parent/child transitions.

## Status

- Strict document: **promoted as PB-01 report-candidate**.
- Production-ready disclosure text: **no**.
- Best next lead: build a maintainer-grade unit/regression from `tools/probe_rev0010_pb01_connection_state_machine.py` and validate legitimate reconnect/fallback compatibility.
