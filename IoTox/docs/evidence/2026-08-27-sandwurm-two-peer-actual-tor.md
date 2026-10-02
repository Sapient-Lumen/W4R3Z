# Sandwurm two-peer actual-Tor evidence

Date: 2026-08-27

Status: accepted bounded two-IoTox actual-Tor auxiliary-route evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`be88fd842e9c2168e0252cc1841df9cd94b6e578` and identical IoTox binary SHA-256
`1fd3b7753e2fccf6ee0829bb13dc9e7c7a66057442926132bce35d5b964ab53d`. Each reused the immutable
private identity baseline and constructed one native UDP primary, one native UDP bulk member, and
one independently keyed strict Tor/TCP bulk member under a stable device principal.

The client and device Tor members used separate Tor 0.4.8.11 processes, data directories, control
sockets, cookies, source-only SOCKS policies, and circuit populations. Both Tor processes used
binary SHA-256 `63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2` and the exact
operator-supplied Tox record:

```text
144.217.167.73:33445:7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C
```

Authenticated extended Tor control events joined each exact guest source through `NEW` and
`SUCCEEDED` to that target. Each role recorded two source streams, two successful streams, and a
distinct three-hop `CONFLUX_LINKED` circuit. The processes had distinct PIDs and control-socket
inodes and each retained a nonempty commitment to its own public TCP remote set.

Both roles then reported authority-private v2 mixed-context operation with two ready bulk members,
synchronization authority, accepted HEAD, explicit activation, and the same signed tree. The tree
contains three directories, three files, and 4,194,389 content bytes. Its payload SHA-256 is
`374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`; artifact and manifest
SHA-256 values are `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` and
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`.

The complete host span, including image realization, was 409,086,343,774 ns.

## Packet and Tor observations

Native UDP and related ICMP are an explicit non-contained control class. Every guest TCP packet had
one of two permitted local destinations: the role-specific Tor listener or pinned local Tox relay.

| Role | IPv4 egress | Native UDP | Native ICMP | Local relay TCP | Tor SOCKS TCP | Unexpected packets | Capture SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---|
| client | 3,588 | 2,934 | 21 | 50 | 583 to `10.0.0.1:39051` | 0 | `a580441fae6b4c1d9689636af200e2d34c49c0f8d2aef294e580463424491a6b` |
| device | 3,116 | 2,530 | 7 | 48 | 531 to `10.0.0.1:39052` | 0 | `e665a394044e171cf8ada5857aa2b5435d78c1b1d0bb6e9710866d732542adae` |

The client and device Tor event SHA-256 values are
`8a7cd53b595e8451d7c81564f1d0e12ef9c3571bd5f47fdd4c22e52e4dab9e4e` and
`6a7616d8a3cfc707095348a50931c77a6e16dee45a0897b48b35dd84e5addf07`.
The selected circuit-path values are retained only as SHA-256 commitments, respectively
`c8bd10952f7474ee30560377c5e0b9cec9c72c5fad2e00fd95c9f5926e703234` and
`79880ec018ca0431e2d5abd17813c964dd673c640e917de2c255f103c1cad6d0`.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.2mycvy9n`. It allocates 3,764,224
bytes, reports `contains_secrets=false`, and omits guest disks, injected identities, runtime state,
the bootstrap secret, and both Tor data directories. Its source manifest, compact pair manifest,
containment record, and compact-export SHA-256 values are respectively:

```text
509f94aa802c9e034c59f26f31581cb0bdf5450f64f86fec43bf6f56a7fd170d
783aa1696206ae237a7117a3f5e770e35f6aac565da109d166e0e4e5f8b5ab23
9da768a5de0a16ab7e944ffef7bbaa97c63bb12a2a5a03060bb6ee411c576a03
bd5b7d2aadad068461c32ee7b93b066eae65efd24d5ded5151e11e0c21e2c92c
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/lab/pairs/PAIR_ID sync-tree-route-private-actual-tor
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID sync-tree-route-private-actual-tor
```

Both the 2.3 GiB private root and compact export independently returned `passed` from the strict
`iotox.sandwurm-pair-verification.v0` verifier. The compact verifier independently reparses the raw
Tor STREAM/CIRC, bootstrap, circuit-status, configuration, TAP, and normal pair-receipt evidence.
Its negative fixture changes the client target and must be rejected.

## Exact nonclaims and next gate

This is one physical host, two local VMs, one public Tox node, one Tor build, two circuits, one
signed tree, and one finite time window. Separate Tor processes on one host are not physical path
independence. This does not prove anonymity, timing unlinkability, correlation resistance, public
relay reliability, representative exits, malicious-proxy resistance, long-duration behavior,
cross-route failure recovery, I2P, or a production default.

The cell proves the Tor member's Tox association and private-v2 application proof became ready in
the same topology that converged the tree. It does not retain a scheduler attribution proving the
4,194,389 object bytes themselves crossed the Tor member rather than the parallel native member.
The next scientific gate must force or directly attribute the payload to Tor, then repeat Tor
loss/recovery without allowing the native member to satisfy the affected transfer.
