# Sandwurm actual-Tor adversarial-boundary evidence

Date: 2026-08-28

Status: accepted bounded two-IoTox actual-Tor/Ratox adversarial-boundary evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`05a025e2b8809622bf821c807da89652b2bc8b14` and identical IoTox binary SHA-256
`70cd90ce57c2d0f69555e3a3f8d116664c47684e517ff33909b9dd68568b2c1a`. Each primary agent used
strict `Tox/Tor` through its own bridge-bound adversarial interposer and its own loopback-only Tor
0.4.8.11 SOCKS endpoint. Both Tor processes reached the operator-supplied public numeric Tox record
`205.185.115.131:33445` on qualifying three-hop application circuits.

After one authority-bound Ratox echo PTY completed its first heartbeat and byte exchange, the host
created only the client interposer's explicit hold file. The interposer kept the accepted guest and
Tor TCP streams open but stopped relaying their bytes. While the hold was active:

- the same bridge listener remained reachable;
- a new numeric SOCKS5 CONNECT through that listener, interposer, Tor, and the exact Tox target
  succeeded;
- the Ratox heartbeat missed after 2.578 seconds while c-toxcore still reported carrier `tcp` and
  the authenticated session remained `confirmed` at online epoch 2;
- c-toxcore did not report authoritative offline until 27.241 seconds after the hold began; and
- the device retained the exact live PTY detached, with zero controllers attached.

The host then removed only the hold file. Tor PID/control-socket inode, interposer PID/listener inode,
both IoTox daemons, both guests, and the remote PTY all remained unchanged. The client reached a new
authenticated online epoch after 6.231 seconds and explicitly resumed the exact session and
incarnation 1.637 seconds later. Attachment generation and input/output positions advanced exactly
from 1 to 2; post-resume heartbeat and terminal byte `B` completed.

This closes the local-deception question: a reachable SOCKS listener, a successful target CONNECT,
open TCP sockets, and healthy Tor control are useful observations, but none is c-toxcore carrier,
Ratox heartbeat, session, detach, or resume authority.

## Exact attribution and containment

The client interposer recorded three admitted chains: two guest application chains and the explicit
during-hold host probe. It recorded three relay-hold observations and zero denials. The device
interposer recorded two guest chains, no hold, and zero denials. Every chain binds its client source,
exact public target, interposer upstream source port, and role-local Tor SOCKS destination. The
strict verifier joins every upstream source port to an authenticated Tor `STREAM NEW` event for the
same exact target and to built three-hop `GENERAL` or `CONFLUX_LINKED` circuit evidence.

| Role | Interposer | Tor SOCKS | Admitted chains | Guest chains | Hold observations |
|---|---|---|---:|---:|---:|
| client | `10.0.0.1:39051` | `127.0.0.1:39151` | 3 | 2 | 3 |
| device | `10.0.0.1:39052` | `127.0.0.1:39152` | 2 | 2 | 0 |

Both TAP captures contain only TCP to the role's bridge interposer, with zero native UDP, direct
bootstrap, direct relay, or direct-peer packets:

| Role | IPv4 egress | Sole destination | Capture SHA-256 |
|---|---:|---|---|
| client | 803 | `10.0.0.1:39051` | `ff117287f7092879d60e6513ee1c0e7ad6b41b1bc0bfcd1aac9a9c374d3ff341` |
| device | 1,509 | `10.0.0.1:39052` | `925c5acba2a1b28c520dda4a5da3a179244a533c46a6012cac8a1d2c7ec628ed` |

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.vx6z0csh`. It allocates 1,953,792
bytes, reports `contains_secrets=false`, and retains 37 independently inventoried files while
omitting guest disks, injected identities, runtime state, the bootstrap secret, and Tor data
directories. The private proof allocates 2,551,435,264 bytes. Both forms independently return
`passed` from the strict verifier.

The source-private manifest, compact manifest, adversarial-boundary record, Ratox lifecycle, and
compact-export SHA-256 values are respectively:

```text
b59b4ea710a5bf3668c9103e4fa84b95731288af33f7ad2e2f7dddef834e8d1e
1c0dc67484422cf187bcb9d38e1bebf7438d279dc1463337502b6f21893a313c
ace069e015c9e5b76672855c4920d12612f10199a377e6b10067b139dc815f8a
5e38a0de247965c22ce6fbf10623a64c3d215d4c8b8802e87db0db432183b410
6b87d9c2e199add8e82038a79a3832850601f677cd27bbf0741d5ac6b5a5d257
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-adversary \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/lab/pairs/PAIR_ID ratox-route-actual-tor-adversary
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/exports/pairs/PAIR_ID ratox-route-actual-tor-adversary
```

The verifier reparses the append-only interposer audits, authenticated Tor control events and
inventories, process/socket identities, both TAP captures, Ratox heartbeat and controller captures,
the detached host snapshot, exact resume lifecycle, VMM chains, reusable-identity invariance, and
compact file inventory.

## Exact nonclaims and next gate

This is one bounded fault on one physical host, two local VMs, one public Tox record, one Tor build,
one interposer implementation, one echo profile, and one time window. It proves neither anonymity,
unlinkability, timing-correlation resistance, exit diversity, public-relay reliability, automatic
terminal migration, a latency SLA, constrained-hardware suitability, nor fleet behavior.

The next locally actionable M8 science was repetition in later time windows with explicit Tor path
population accounting and reviewed relay records. ADR 0210 subsequently closes deterministic
accounting over the seven retained compact proofs while keeping independently reviewed exit and
separated-time claims open. I2P construction and voluntary bootstrap/relay stewardship remain
separate open roadmap gates.
