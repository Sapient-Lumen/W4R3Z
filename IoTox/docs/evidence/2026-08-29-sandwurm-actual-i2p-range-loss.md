# Sandwurm actual-I2P range-loss evidence

Date: 2026-08-29

Status: accepted bounded live-range loss, fail-closed cleanup, and explicit fresh recovery evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`9af199fb227acd16a101f7686b2c644244354c9c` and identical IoTox binary SHA-256
`a64e17d381e9ee7bf24c9596d163169afafcde4c6b79d77eea48369f646a885e`.
The client first accepted a native 4 MiB basis, then pinned its generation-2 successor to
`fail-closed tox/i2p-construction`. After 86,373 bytes of the concrete 1 MiB range bundle arrived,
the host stopped only the client i2pd process. IoTox retired the carrier receive, removed all range
staging state, blocked the old job, and made no native reassignment.

A distinct router process reused the same private datadir. SAM generation two returned and the same
signed auxiliary recovered without an IoTox worker restart. The old job stayed fenced until explicit
cancellation. A distinct fresh job fetched the complete 1 MiB range through the same carrier, reused
the other 3 MiB from the verified basis, reconstructed the exact generation-2 artifact, accepted its
linked HEAD last, and explicitly activated it. This closes ADR 0228's bounded fresh-recovery gate; it
does not claim reuse of failed partial bytes.

## Exact lifecycle

```text
source revision                    9af199fb227acd16a101f7686b2c644244354c9c
product revision                   rev0045
artifact bytes                     4,194,304
manifest bytes                       786,496
range bundle bytes                 1,048,576
positive pre-fault position           86,373
verified basis bytes reused        3,145,728
fresh range bytes fetched          1,048,576
old client router PID                1435215
new client router PID                1451397
router/SAM fault hold              68.166 seconds
loss observation                   29.263 seconds after stop
route recovery                     39.276 seconds after router replacement
carrier losses                     1
blocked fail-closed jobs            1
route recoveries                    1
worker restarts                     0
reassignments                       0
old job explicitly cancelled       true
replacement job distinct           true
replacement carrier identical      true
range staging entries after loss    0
```

The process-local job IDs remain in the content-free host record and client receipt. The carrier is
also retained as SHA-256 commitment
`0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c`.
The target artifact is
`a9c0a0a26d2c01cf541e0d959cf3e8bed2f4aefcafaa713b5d1c104903a7a715`; its manifest is
`575e41d269c20e5669d7d873999a9e7fdaf455eac3420f41e2b1b94273d7db93`, and accepted HEAD token is
`d33125d9c857dfc7ddb855e093e2768312c6f1a1aeba5ee1ffc8d8c7988fd253`.

The adapter listener remained reachable while SAM was absent, generation-one loss was audited, and
seven connection attempts were denied specifically because SAM was unavailable. Generation two
then admitted all three committed fronts. This makes the fault a router-path outage rather than an
IoTox process, guest, bridge-listener, or signed-route mutation.

## Packet containment

Both guests intentionally retain native protected traffic beside the I2P auxiliary. All proxy-bound
TCP stays confined to `10.0.0.1:39053`; neither capture contains an unexpected context packet.

| Role | IPv4 egress | Native UDP | Adapter packets | Unexpected | Capture SHA-256 |
|---|---:|---:|---:|---:|---|
| client | 12,256 | 8,238 | 3,869 | 0 | `d89e2d1ae5b5ac916fefca575d741dd4a3adb911223ca6f5216b21e9b456f57c` |
| device | 15,134 | 11,056 | 3,940 | 0 | `809d0b058860a373349c0bce173c69dbb017a508dec8b1c2f8ef6a40e82a1189` |

The topology retains the pinned i2pd 2.60.0 binary/source/certificate commitments, three unchanged
Destination commitments, exact router-owned SAM listeners/public socket summaries, one client-router
replacement, zero service-front replacement, and no unknown adapter outcome.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.a9zwongf`. It allocates 26,558,464 bytes
across 19 files, reports `contains_secrets=false`, and omits bootstrap secret state, guest disks,
injected identities, and runtime state. The source-private proof allocates 2,498,297,856 bytes. Both
independently returned `passed` from the strict verifier. After that independent check and compact
export, the guarded workspace cleaner removed the source-private VM root together with seven rejected
diagnostic roots, reclaiming 18.5 GiB; the compact proof was reverified afterward and is retained.

```text
source-private manifest SHA-256  f671bedc19a96cc4b127a7ba8ce7b98205e926e079ad73e7cfb6ded25478a6af
compact pair manifest SHA-256    3b6e5208d6ce88a754adfc373819df8cafd09b5d9c48377dc38126764d02834e
compact-export SHA-256           5ccedee163128b8a30b6dc1ff901771439e243a90144dc556f0c20a71a6d853c
fault record SHA-256             3cfa94a7bd93c0a41155d5f57fa6e7ebd4c1c7dc2605ed88e8f1e22ea97cd72b
topology-final SHA-256           fd3ce987d9582d4e5b4015b41ea73294f00f0a53e8632ab00462e493d4da2c7f
client receipt SHA-256           cdd897271e275814a4983a2df154bda07e8c5fd192b00cb706ecf9ab02305662
device receipt SHA-256           c558782c2ce0333b26e357f01b1cb29b8078df26838d0a60555305cfed4a04f5
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-file-range-actual-i2p-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/lab/pairs/PAIR_ID sync-file-range-actual-i2p-loss
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID sync-file-range-actual-i2p-loss
```

## Nonclaims and next gates

The failed 86,373-byte prefix was discarded. This proof therefore qualifies safe explicit fresh
recovery, not same-job continuation or cross-carrier/process byte resume. It also does not qualify
production `tox/i2p`, anonymity, timing resistance, independent administration, fleet behavior,
larger distributions, repeated/very-late loss, or a performance bound. Those remain deliberate
separate experiments.

## Qualified manifest-reuse optimization

ADR 0229 repeats the complete gate from clean commit
`704a3c72fdb7e3e6ef9f05ed12ad12608430e91e` as `pair.ip5q0at9`. Both guests run identical binary
SHA-256 `3f09780dc67293c7ec62ca2bf55be91d80e6ca8b8ae1964ebac95b4bc4a559a6`.
The first concrete range reached 71,292 bytes before router loss and was completely discarded. After
the exact member recovered and the old job was explicitly cancelled, the distinct job reported one
requested object, two committed objects, and `manifest_reused_locally=true`. It did not refetch the
786,496-byte manifest; it fetched only the complete 1,048,576-byte range, reused 3,145,728 basis
bytes, reconstructed the same 4,194,304-byte artifact, accepted the same generation-2 HEAD, and
explicitly activated it.

```text
source revision                    704a3c72fdb7e3e6ef9f05ed12ad12608430e91e
binary SHA-256                     3f09780dc67293c7ec62ca2bf55be91d80e6ca8b8ae1964ebac95b4bc4a559a6
proof ID                           pair.ip5q0at9
pre-fault range position           71,292 / 1,048,576 bytes
replacement requested objects      1
replacement committed objects      2
manifest reused locally            true (786,496 bytes)
range fetched / basis reused       1,048,576 / 3,145,728 bytes
old recovery object bytes          1,835,072
new recovery object bytes          1,048,576
reduction                          786,496 bytes / 42.86%
fault hold                         65.625035767 seconds
loss observation                   26.778382389 seconds
route recovery                     39.269659872 seconds
carrier losses / reassignment      1 / 0
route recoveries / worker restarts 1 / 0
```

The source-private proof allocates 2,500,288,512 bytes. The compact secret-free export at
`.sandwurm/exports/pairs/pair.ip5q0at9` allocates 23,199,744 bytes across 19 files. Both independently
returned `passed` from the strict verifier. After export, the guarded cleaner's exact dry run named
only the 2.3 GiB source-private root; applying that scope deleted it. The compact proof was reverified
afterward, remains retained, and a second dry run reports zero candidates.

```text
source-private manifest SHA-256  4c91dc615fcd06929dea3f86f58b6debaff8c71f0e374ad11e33926e9fa84e2b
compact pair manifest SHA-256    421ae6f8a176291632b48223690b03f995267b5367de07daf34e7eed455b287f
compact-export SHA-256           8e001cc5c06e44d732ce2813adacb3a2f059ff84540959c879dbb8684c4742fa
fault record SHA-256             d6dda35f7bf99a7d8ce7d0daf38b568666fed97a7ffcfd54ab0ee4a2747dc5ef
topology-final SHA-256           b8165e8e6f5cc10d86eb45c16c2c6cdb6d805fe419a770fe4fc4e8cd2dc76e73
client receipt SHA-256           30bc0db22eab05ddab3198975c51f180889bb7587338e53dbda62a3375cf5aa0
device receipt SHA-256           97391e44a44345934488fd9325ced2fe2d871cc6c2630d69a9b1d81fbc50c682
client TAP capture SHA-256       0632dbaef4ce8bbbc2372a9978b5700cd4edc2b3f04a8ed98c1b60f4753b7a83
device TAP capture SHA-256       b40a82ce21b791575e9f9ad59e371c3141de3db2378562c7253ceca0de7ca004
```

This result qualifies exact immutable prerequisite reuse. It remains deliberately separate from
failed-range-prefix reuse, same-attempt continuation, restart-persistent staging, production I2P,
anonymity, independent administration, fleet behavior, or a latency/throughput SLA.
