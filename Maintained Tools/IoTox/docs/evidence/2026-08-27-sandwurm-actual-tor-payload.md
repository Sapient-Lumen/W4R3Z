# Sandwurm actual-Tor payload-attribution evidence

Date: 2026-08-27

Status: accepted bounded two-IoTox actual-Tor payload evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`38aa432679e4f470d459d441d10b01669ad45b5b` and identical IoTox binary SHA-256
`1fd3b7753e2fccf6ee0829bb13dc9e7c7a66057442926132bce35d5b964ab53d`. Each reused the immutable
private identity baseline and combined a native UDP primary with two authority-private v2 bulk
members. The founding stable key ordering placed the exact lane-1 bulk identity on Tor; the gate
failed closed unless that key remained the fixed scheduler's first eligible member.

The client completed its exact signed-tree pull with `carrier=auxiliary`, `state=complete`, and
carrier-key SHA-256
`0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c`. That value equals the
client receipt's independently committed Tor auxiliary key. The job recorded zero auxiliary
reassignments. Initial pull admission succeeded on its first attempt, so the evidence-bearing
admission fields are `attempts=1`, `failures=0`, and an empty first-error digest.

The tree contains three directories, three files, and 4,194,389 content bytes. Its payload SHA-256
is `374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`; artifact and manifest
SHA-256 values are `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` and
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`. Both roles reported two
ready bulk routes, the same accepted HEAD, explicit activation, and identical tree commitments.

The client and device used separate Tor 0.4.8.11 processes, data directories, authenticated control
sockets, cookies, source-only SOCKS policies, and circuit populations. The exact Tor binary SHA-256
was `63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2`; both workers used only
the operator-supplied public Tox record:

```text
144.217.167.73:33445:7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C
```

Each role recorded two guest-source streams, two successful exact-target streams, and one distinct
three-hop `CONFLUX_LINKED` circuit. The complete host span, including image realization, was
620,010,890,108 ns.

## Packet and Tor observations

Native UDP and related ICMP are the explicit primary/control class. Every guest TCP packet was
confined to its role-specific local Tor listener or the pinned local Tox relay.

| Role | IPv4 egress | Native UDP | Native ICMP | Local relay TCP | Tor SOCKS TCP | Unexpected | Capture SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---|
| client | 6,056 | 3,506 | 14 | 67 | 2,469 to `10.0.0.1:39051` | 0 | `af074bfbbd682734e2db112058444a942612793743caa94d238767a41f18a7cc` |
| device | 8,228 | 3,806 | 15 | 66 | 4,341 to `10.0.0.1:39052` | 0 | `8ccccebad4de667b177e8049533665c1da5546eac86f0d365771f0bf826d3099` |

The client and device authenticated Tor event SHA-256 values are
`38fd8e8f77bc7a434f89466eac5cf7a09f2ab9847fa52dde66bc9cfbc579128d` and
`a8bc3ed0fa29ac070868a2133a0ec324cbd74fd4ac153fa5aa6fda528d318f42`. The selected circuit-path
commitments are `dd73da93d67030dda5073ed4cf563e0e2e4cfea841e79fdd3c5864d55e71dfd6` and
`aa225e846025b58f19364a12cf9521033d64379a3fb7a06357558d427009be32`.

## Qualification history

The first application run completed the Tor-carried job, but a host runner defect replaced loaded
guest receipts with digest-index entries before aggregate-manifest construction. Strict verification
correctly rejected that malformed summary. Commit `7a92bcc` moved aggregation behind digest-indexed
receipt reloads and added an offline regression.

The next clean run reached two ready route sets and a signed publication but received one transient
local `sync-pull` rejection before a job ID existed. The old harness discarded stderr and aborted.
Read-only recovery from a copy-on-write clone of the journal-dirty stopped disk proved the Agent did
not crash. Commit `38aa432` added a 120-second idempotent admission window and exact attempt/failure/
first-error-digest evidence. The accepted run then succeeded on the first attempt. Neither earlier
run is promoted as accepted evidence.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.lzsyitvy`. It allocates 16,257,024
bytes, reports `contains_secrets=false`, and omits guest disks, injected identities, runtime state,
the bootstrap secret, and both Tor data directories. The source manifest, compact pair manifest,
containment record, and compact-export SHA-256 values are respectively:

```text
97fbc9770e22780667f09ab93c780010eadabd250677f792846c8b6198c1acb3
daeb0894e9b218cf97f3285d09f70d265a6de51a1d1a14cf3a3a07233c9fad6e
9b9fdf813e95d30a490f64775c4811691bf5ab8e5b5d5931adc2f1cb8caca678
511e3e4680a8dda20720304237f8412e063c65459bfbb63a954783dd95f94d21
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor-payload \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/lab/pairs/PAIR_ID sync-tree-route-private-actual-tor-payload
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID sync-tree-route-private-actual-tor-payload
```

Both the 2.4 GiB private root and compact export independently return `passed` from the strict
verifier. The compact verifier reparses the retained guest receipts, Tor STREAM/CIRC and process
commitments, configurations, TAP captures, signed-tree agreement, exact carrier relation, zero
reassignment, and admission evidence.

## Exact nonclaims and next gate

This proves IoTox assigned the complete immutable-object job to a member whose Tox transport was
independently bound to Tor. It is one physical host, two local VMs, one public Tox node, one Tor
build, two circuits, one signed tree, and one finite time window. It does not prove anonymity,
timing unlinkability, correlation resistance, physical path independence, public relay reliability,
representative exits, goodput distributions, adversarial-proxy behavior, or long-duration service.

Actual Tor process loss did not occur during the accepted transfer. The next gate must interrupt the
exact Tor carrier after positive object progress, observe member withdrawal without direct leakage,
and separately qualify either bounded reassignment or same-member restart/retry. Multiple public
nodes, exits, and time windows remain mandatory before any wider routed-privacy claim.
