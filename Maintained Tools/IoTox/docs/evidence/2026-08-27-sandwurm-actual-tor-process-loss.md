# Sandwurm actual-Tor process-loss evidence

Date: 2026-08-27

Status: accepted bounded two-IoTox actual-Tor process-loss/reassignment/recovery evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`ee74a953876b80a1c82a933a64598b4d2d26e889` and identical IoTox binary SHA-256
`70cd90ce57c2d0f69555e3a3f8d116664c47684e517ff33909b9dd68568b2c1a`. Each reused the immutable
private identity baseline and combined a native UDP primary with two authority-private v2 bulk
members. The founding stable-key order assigned the exact client lane-1 member to an independently
supervised Tor process and left the other auxiliary available over native UDP.

The client began the signed-tree pull on that exact Tor member. At 74,034 of 16,777,513 artifact
bytes, after independently capturing authenticated Tor process/control/circuit evidence, the host
sent `SIGKILL` to only the client Tor process group. It did not stop IoTox or invoke the
qualification-only route-worker fault. The client observed exactly one carrier loss and one
reassignment to the other exact auxiliary after 28,348,753,790 ns. Its IoTox route-worker restart
count remained zero.

The host held Tor absent until that reassignment was proved, then restarted the identical Tor
0.4.8.11 binary, configuration, and private data directory. Tor reached bootstrap 100 after
3,491,124,320 ns. IoTox counted exactly one carrier recovery when the actual member became
qualified again. The transfer completed over the replacement member with two stale fenced
terminals, two ready bulk members, no internal qualification fault, and the same signed-tree
activation on both roles.

The tree has three directories, three files, and 16,777,301 content bytes. Its payload SHA-256 is
`4d4d1b014a00448e56f14a5638b05494326003ae805cdd124ab1d55be0a73b97`; artifact and manifest
SHA-256 values are `e3a25daf0e29c4ce25bd87a55a7d5437863a367f804ac551f7c1fe47a877c4a4`
and `ecaaea48dde740c466f550d20ec30f8267008d646326ff37e8b23c9c13f012ad`.

## Process and route observations

The stopped Tor member was
`13E3E4EFA78A92E3A1B41AFF31BE596496903F83383566E1BDD15C02BE7ADC10`, committed by SHA-256
`0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c`. The replacement member was
`478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A`. The pre-loss and recovered
client Tor PIDs were 1,533,763 and 1,587,354; their authenticated control-socket inodes were
5,846,958,482 and 5,846,966,822. The device Tor process remained continuous.

The exact Tor binary SHA-256 was
`63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2`. The client pre-loss,
client recovered, and device continuous observations each reached bootstrap 100, joined the exact
guest source to the operator-supplied Tox target, and selected a three-hop application circuit.
Their authenticated event SHA-256 values are respectively
`e44650197066fcd1853a6d1346eefb75e42353710c761a3731e324deec01f33b`,
`f861b3aec6dba7379577352522ec2baa3879f9f1e7e79cf97eeedb01f415d30a`, and
`6ae1e5fb019d18a0f82b58e02bbd6c2b9578e9188f1186c8f261f5c8bc672977`.

Native UDP and related ICMP are the explicit primary/control class. Every guest TCP packet was
confined to its role-specific local Tor listener or the pinned local Tox relay.

| Role | IPv4 egress | Native UDP | Native ICMP | Local relay TCP | Tor SOCKS TCP | Unexpected | Capture SHA-256 |
|---|---:|---:|---:|---:|---:|---:|---|
| client | 5,333 | 4,468 | 18 | 76 | 771 to `10.0.0.1:39051` | 0 | `8f93b2bc75741a3ea6ba32cb39ca7f3c02796c4369879110dff186f9c935beb3` |
| device | 17,994 | 16,852 | 21 | 61 | 1,060 to `10.0.0.1:39052` | 0 | `56333c6fd961f8a53417738d55f90a02e6240fc7bf369d59b4ecbc1165740b23` |

The complete host span, including image realization, was 525,517,812,748 ns.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.iompvehf`. It allocates 43,450,368
bytes, reports `contains_secrets=false`, and omits guest disks, injected identities, runtime state,
the bootstrap secret, and both Tor data directories. The source-private manifest, compact pair
manifest, process-loss record, and compact-export SHA-256 values are respectively:

```text
100c165460779f0ec9f6080abce3de4c305fe86ff9f7b86eaeca3b7cc51d9b48
e0c1af3e5322b33b71dbe822f6b05eae9e6b5cf58564ed84eb685b21dba5ba34
248987cb4af6ac0f81862ebd11962c9d478c08ac53e806b1ee3596761e580a99
dbb0d12af9a8541c1e82e6456ccd27cde79a7b24632efccf1e6078d528e32b6c
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/lab/pairs/PAIR_ID sync-tree-route-private-actual-tor-loss
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID sync-tree-route-private-actual-tor-loss
```

Both the 2.47 GiB private root and compact export independently returned `passed` from the strict
verifier. The compact verifier reparses the retained guest receipts, three Tor evidence phases,
process-loss record, TAP captures, signed-tree agreement, exact carrier relations, loss,
reassignment, recovery, stale terminals, and zero route-worker restarts.

## Qualification history

The first clean process-loss run passed the full experiment and compact verification. Review then
found that zero route-worker restarts was enforced by the guest but not serialized into the retained
receipt and host process-loss record. Commit `ee74a95` made that relation independently
reverifiable. `pair.iompvehf` is the clean rerun of that stronger evidence contract; the earlier run
is not promoted as accepted evidence.

## Exact nonclaims and next gate

This proves bounded immutable-object failover when one independently supervised actual-Tor carrier
process disappears and later returns. It does not claim anonymity, unlinkability, timing-correlation
resistance, physical-path independence, seamless terminal migration, general public-relay
reliability, or that reassignment to native preserves a privacy property. It is one physical host,
two local VMs, one public Tox record, one Tor build, three observed circuits, one signed tree, and
one finite time window. The next M8 evidence frontier is diversity and duration: multiple reviewed
relays/exits/time windows, a long-running application topology, and adversarial local-proxy behavior.
