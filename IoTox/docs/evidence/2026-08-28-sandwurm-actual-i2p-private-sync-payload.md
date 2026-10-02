# Sandwurm actual-I2P private sync-payload evidence

Date: 2026-08-28

Status: accepted bounded two-IoTox actual-I2P construction evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`a2205b665104d6c82a51cefbe0a3637fec61f506` and identical IoTox binary SHA-256
`1235e79f138f1a2878fffd845db6b541245208e52e1598209c9f639aea76bc77`. Each role retained a
native primary, a native auxiliary, and an independently keyed `Tox/I2P-construction` auxiliary.
Private route-binding v2 admitted the two exact auxiliary members for the remote stable principal.

After both exact members were ready, fixed selection assigned one signed tree pull to the client's
I2P member. The complete 131,369-byte artifact was verified, its HEAD was accepted last, and that
exact token was activated. The carrier commitment equals the client's I2P auxiliary-key commitment;
one role records the attribution and zero reassignments. Native fallback remained available, so this
is stronger than a route-only pass.

This proves one bounded private-member sync payload. It does not enable production `tox/i2p`, prove
anonymity, independently administered routers, byte-level traffic classification, long-term
availability, or objects larger than this exact fixture.

## Exact application result

```text
scenario                         sync-tree-route-private-actual-i2p-payload
primary route                    direct-udp / Tox/native
private auxiliary route          Tox/I2P-construction
ready auxiliary routes           2 per role
private-context roles             2
generated payload bytes           131,072
tree content bytes                131,157
treepack artifact bytes           131,369
tree files/directories            3 / 3
pull attempts/failures             1 / 0
payload-observing roles            1
payload reassignments              0
router/front restarts              0 / 0
```

```text
payload carrier SHA-256  0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c
artifact SHA-256         1561fd522b8dae36ba428a6c4a4decb12636bc9118d781ff5f58ff82349baf16
manifest SHA-256         0e8cf5710cd6c7145281252f9f9b0c9971d0e0e84d8eba64d011fc6f95b7e2cf
HEAD record SHA-256      a918fa4320008a845322d396f7169fe2687c268af06f5dbda1af9358a0a709d6
payload SHA-256          e00495e384dd69c9ad5a850cbde4be69c277e074ae3b17f56942a2681feb7ffe
node-record-set SHA-256  fd68d12122b21347b54259bd263a1740afdc06e3d5ec14aa22b84897c1c44059
```

## I2P topology and containment

The topology binds i2pd 2.60.0, router binary SHA-256
`d5e89b4c2520ae5e3776a9c134b54200061b477f8b388bea60f60b07865753b5`, its 315-file source-tree
commitment, and the source-matched 21-file certificate tree with signed reseed verification. The
server and client routers own their exact SAM listeners plus 28 and 31 established public TCP
remotes. The adapter records one ready generation and 12 admitted exact-Destination streams. All
three fronts record `created -> ready`; none is replaced.

Because the primary and fallback are deliberately native, this cell uses mixed-context containment
rather than a no-native-packet rule:

| Role | IPv4 egress | Native UDP | Native TCP relay | I2P proxy | Unexpected context | Capture SHA-256 |
|---|---:|---:|---:|---:|---:|---|
| client | 5,128 | 3,572 | 60 | 1,486 | 0 | `0d45d760a4a6709db2a4141b178311eb839e715c5f99f02028c57796a62ead84` |
| device | 4,379 | 3,524 | 59 | 786 | 0 | `0255a052f752fe3e6732b37b469a4e911a49c350783d3b09632153cf75791317` |

Every guest TCP packet stays within its configured local context endpoints. The captures span about
106 seconds; the full topology runs 429.650 seconds. This is route-context evidence, not a claim that
packet inspection identifies the encrypted object bytes. Carrier attribution comes from the
authenticated scheduler/receipt join.

## Negative size science

The same topology and zero-reassignment acceptance rule rejected preliminary 4 MiB and 512 KiB
fixtures. Both initially selected the expected I2P member, then recorded one carrier loss and safely
reissued the remaining complete object through native. The routers and fronts remained alive. In the
512 KiB attempt, the busiest client-to-adapter TCP conversation carried about 301 KiB over 100.984
seconds before ending. These diagnostic private roots were cleaned after the result was recorded and
are not qualification artifacts.

The current auxiliary protocol intentionally excludes range frames and reassigns complete immutable
objects. The observation therefore establishes a 128 KiB accepted lower bound and a 512 KiB rejected
upper point for this one construction window—not a universal MTU, throughput, or I2P limit. The next
protocol experiment is bounded digest-bound auxiliary chunks/ranges with signed privacy-class
failover policy, followed by larger-object repetition.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.5xjf2n4d`. It allocates 5,115,904 bytes,
reports `contains_secrets=false`, declares 17 evidence files plus its own export manifest, and omits
guest disks, injected identities, runtime state, bootstrap secret material, router datadirs, savedata,
and Destination keys. Raw and compact verification independently return `passed`.

```text
source-private manifest SHA-256  257e5808fa8dc1181131f2688499b109257a326af30b0ed2b13088dd7f7ca971
compact pair manifest SHA-256    b66b6f2e4ca255a35f41c06bfe15510d38b74d6b51f1dd05a1febdd666d7d6ad
compact-export SHA-256           af595cc0d70628ee039baaa8e1840f3f252bfabb949fb8d89792828e107c60a9
topology-final SHA-256           6d19fdde01b4447c9eb952668d8b3c7939185b7ee349b6805652e63a012a22b5
```

Use three explicitly reviewed, currently reachable public numeric Tox TCP records:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-i2p-payload \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID \
  sync-tree-route-private-actual-i2p-payload
```

The compact exporter has a registered regression that requires actual-I2P scenarios to retain I2P
captures, topology, and audits while excluding Tor artifacts. The accepted compact proof passes the
same strict verifier as its private source.
