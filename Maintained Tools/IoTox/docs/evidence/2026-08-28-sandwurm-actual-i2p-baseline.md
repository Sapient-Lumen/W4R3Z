# Sandwurm actual-I2P baseline evidence

Date: 2026-08-28

Status: accepted bounded two-IoTox actual-I2P construction evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`0af4759dc29e610854764064ede21316e5c35277` and identical IoTox binary SHA-256
`2c433ee52fbf9fd15118b95c23d299f0ade772f7047669120ac44b5663b85bad`. Each guest used the
laboratory-only `Tox/I2P-construction` route, the bridge adapter `10.0.0.1:39053`, and the same exact
three-record commitment. Both reached c-toxcore `tcp`, Tox friendship, canonical IoTox session
confirmation, and bidirectional text. The reusable private identity baseline was unchanged.

This closes the first real two-guest packet-containment and baseline application gate. It does not
qualify route loss/recovery, Ratox, sync, anonymity, or the reserved production `tox/i2p` spelling.

## Frozen router and topology

The host supervisor owned two distinct i2pd 2.60.0 processes, three persistent SAM service
Destinations, three exact-target TCP egress shims, and one strict bridge SOCKS-to-SAM adapter. The
compact topology receipt binds:

```text
router executable SHA-256  d5e89b4c2520ae5e3776a9c134b54200061b477f8b388bea60f60b07865753b5
router source-tree SHA-256 5ac86d648c0f211c145ea6686c730a946d593457c6b6189f3bf660884195ce4f
router source files        315
node-record-set SHA-256    a173e1f9455f3e1807cc2cb2acd63596ed7e9d15915a681de5a656963a5e87af
front count                3
topology runtime           596.068 seconds
```

Destination keys remain private. Their three domain-separated b32 commitments are retained in the
topology receipt. Each persistent forward records exactly one creation and one ready outcome with no
loss.

The adapter observed seven successful I2P streams and two initial `denied-stream` outcomes. The
refusals occurred after 6.436 and 9.109 seconds while the initial I2P paths settled; the same two
Destinations subsequently admitted, and every one of the three committed Destinations has a
successful admission. The strict verifier permits only this bounded retry class and rejects unknown
Destinations, other denial outcomes, missing fronts, or an incomplete three-Destination admitted set.

## Packet containment

Both TAP captures contain only TCP to the configured bridge adapter. There are no native UDP,
direct-bootstrap, direct-peer, or alternate IPv4 destination packets:

| Role | IPv4 egress | Sole destination | Capture SHA-256 |
|---|---:|---|---|
| client | 1,054 | `10.0.0.1:39053` | `a0c1efa5a8effcf0bce87502b6a59ceadc8b30220d8441adc93aac06c0c6d7bd` |
| device | 1,164 | `10.0.0.1:39053` | `4aec0fd060056affedb4d9cd1c0fba32a79ad3b5a7aa30e1585a17fba5bf0652` |

Both source-linked VMM chains reached `guest-evidence-observed`. The complete pair rendezvous lasted
603.156 seconds. Each guest independently commits the same I2P node-record digest, network label,
TCP carrier, source revision, product revision, and product binary digest.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.k_vopzf5`. It allocates 1,585,152 bytes
across 18 files including its own manifest, reports `contains_secrets=false`, and omits guest disks,
injected identities, runtime state, the bootstrap secret, router data directories, and persistent
Destination keys. The source-private proof allocated 2,441,994,240 bytes. Both forms independently
return `passed` from the strict verifier.

```text
source-private manifest SHA-256  3b0ae6ac9746471ce44c7b4fdbefeeb897e4384d0292b6ad2cdf7a89f7ae3261
compact pair manifest SHA-256    6040fa79cfd6448cae6680b558390ff4421172446572155c504c56444c7723a7
compact-export SHA-256           e4c516d50c0c7bef9cf09fd7e5fe5c7fee247d5734a1495f6affafe7f69fa563
topology-final SHA-256           5cc36c73deef563ca2224be01c79b237bac8eb02f52adec7651fbd96e13fa3d6
```

Use three explicitly reviewed, currently reachable public numeric Tox TCP records:

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-i2p-construction baseline \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p-construction \
  .sandwurm/lab/pairs/PAIR_ID baseline
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p-construction \
  .sandwurm/exports/pairs/PAIR_ID baseline
```

## Exact nonclaims and next gate

This is one bounded time window on one physical host, two local VMs, two local routers, three public
Tox records, and one router implementation/version. It proves neither anonymity, unlinkability,
timing resistance, availability, independent router operation, a latency SLA, fleet behavior, nor
production suitability.

The next locally actionable I2P gate must keep the bridge listener reachable while removing the SAM
route or exact router/front process, separately observe auxiliary route health and authoritative
c-toxcore loss, recover the same route identity without native fallback, and pass fresh application
traffic. A later gate must bind one private route-member proof and an exact Ratox or sync payload.
