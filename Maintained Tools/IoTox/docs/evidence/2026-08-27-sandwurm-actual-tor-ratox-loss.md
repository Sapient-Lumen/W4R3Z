# Sandwurm actual-Tor Ratox process-loss evidence

Date: 2026-08-27

Status: accepted bounded two-IoTox actual-Tor terminal process-loss, detach, and explicit-resume
evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`08baaba59f4f51c8b900c7a4041a4a02a0934e9b` and identical IoTox binary SHA-256
`70cd90ce57c2d0f69555e3a3f8d116664c47684e517ff33909b9dd68568b2c1a`. Both primary agents used
strict `Tox/Tor` through separate host Tor processes and the one operator-supplied public numeric
Tox record. The private fixture was used only for deterministic identity handoff; neither guest TAP
contains traffic to it.

The controller opened one authority-bound echo PTY, completed a heartbeat and byte exchange, then
released the attachment. The host captured authenticated Tor process/control/STREAM/CIRC evidence
and sent `SIGKILL` only to the client Tor process group. After 2.204 seconds, the already-running
Ratox probe missed its two-second heartbeat deadline while c-toxcore still reported carrier `tcp`
and the session remained confirmed. Authoritative offline and the typed local `unavailable` outcome
arrived after 27.379 seconds. The device then reported exactly one live/running PTY, zero attached
sessions, and the same session detached; neither IoTox daemon nor guest restarted.

The host restarted the identical Tor 0.4.8.11 binary, configuration, and private data directory.
Tor reached bootstrap 100 after 2.418 seconds under a distinct PID and authenticated control-socket
inode. Once the peer was authority-capable at online epoch 3, the controller explicitly resumed
only the prior session. The session commitment and process incarnation were unchanged; attachment
generation, accepted input sequence, and output sequence each advanced from 1 to 2. A new
heartbeat and byte exchange completed. No new PTY, automatic migration, stale attachment, sequence
reset, or route-health-derived session transition satisfied the gate.

## Lifecycle observations

| Observation | Accepted sample |
|---|---:|
| Initial heartbeat / PTY / render | 0.530 / 0.637 / 0.000112 s |
| Heartbeat warning after Tor loss | 2.204 s |
| Authoritative offline after Tor loss | 27.379 s |
| Tor restart to bootstrap 100 | 2.418 s |
| Recovery release to authenticated route ready | 89.443 s |
| Route ready to explicit resume OPENED | 1.784 s |
| Recovered heartbeat / PTY / render | 1.240 / 1.056 / 0.000065 s |

These are observations from one public-network time window, not protocol deadlines or an SLO. The
long route-ready interval includes c-toxcore's public-network reconnection and authority handshake;
Tor bootstrap alone was already complete. The heartbeat warning remains intentionally advisory:
only the later authoritative carrier event changed the session to offline.

The pre-loss and recovered client Tor PIDs were 2,060,846 and 2,243,633; their control-socket
inodes were 5,847,049,673 and 5,847,069,974. The device Tor PID 2,087,011 remained continuous. All
three authenticated phases reached bootstrap 100, bound the exact guest source to
`144.217.167.73:33445`, and selected a three-hop `CONFLUX_LINKED` application circuit. Their event
SHA-256 values are respectively
`11df2626886bcb007024c80686915537fb8b9a02080c77aa90c993dfe4035ad1`,
`38227981a43443127d05b7434ec3a5262c3e80a8bbb9316080c83dd098ae4869`, and
`81747cf9f68e6aad3b5da30dd7612a5c00b2114ea1086a9d49370847f302f708`.

## Packet containment

The exact Tor binary SHA-256 was
`63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2`. Every captured guest IPv4
egress packet was TCP to its role-specific local Tor listener. Both captures contain zero native
UDP, direct bootstrap, direct relay, or peer packets.

| Role | IPv4 egress | Sole destination | Capture SHA-256 |
|---|---:|---|---|
| client | 1,010 | `10.0.0.1:39051` | `a864a6c93639d9ddb25c4616145ab70f4ab3b1622cabe5d4b9e3f132eb2b6925` |
| device | 1,066 | `10.0.0.1:39052` | `fede7f24ef2f649bbaecf327c6b42f2753a538925c42b3e4e9cc898a1962d42c` |

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.2waqdpgk`. It allocates 1,728,512
bytes, reports `contains_secrets=false`, and omits guest disks, injected identities, runtime state,
the bootstrap secret, and Tor data directories. The source-private manifest, compact pair manifest,
process-loss record, and compact-export SHA-256 values are respectively:

```text
7d7388c1dac4654d6841817438c395ce2f63a751c607457f98d27dc8a6ba151b
bda41ff0b1661518b392082e650b0401910fada4ffaac04a850befb9ec2e4fe8
bde5c0b26619a7047e1b4774131dd9fda5dcdca473c2a9e300b3c4f59f27d446
c0ea99c32e491ff6dd4fd0d2b891e28942088b62058d98cb5b17803aace3e0e6
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/lab/pairs/PAIR_ID ratox-route-actual-tor-loss
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/exports/pairs/PAIR_ID ratox-route-actual-tor-loss
```

Both the 2,569,691,136-byte private root and compact export independently returned `passed` from
the strict verifier. The verifier reparses the three Tor phases and two pcaps, joins their process,
control, source, target, and timing identities to the frozen Ratox lifecycle, and independently
checks the detached host PTY, exact session/incarnation, higher epoch, generation/sequence advance,
zero IoTox restarts, and strict route containment. The complete guest rendezvous span, including
image realization and public-network waits, was 949,962,356,866 ns.

## Exact nonclaims and next gate

This proves one bounded terminal detach and explicit resume when an independently supervised
actual-Tor carrier process disappears and returns. It does not claim anonymity, unlinkability,
timing-correlation resistance, physical-path independence, automatic resume, transparent route
bonding, roaming between route identities, client-side prediction, screen-state convergence, or a
public-network recovery SLA. It is one physical host, two local VMs, one public Tox record, one Tor
build, three observed circuits, one fixed echo profile, one process loss, and one finite time
window. The next M8 frontier is diversity and duration: repeat the frozen gate across reviewed
relays/exits/time windows, then add long-running PTY/output retention and adversarial local-proxy
behavior without granting route-health observations authority over session state.
