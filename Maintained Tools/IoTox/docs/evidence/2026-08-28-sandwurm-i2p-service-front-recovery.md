# Sandwurm actual-I2P service-front recovery evidence

Date: 2026-08-28

Status: accepted bounded two-IoTox actual-I2P construction evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`d39027274cc0d6072a4c018078601caea357c006` and identical IoTox binary SHA-256
`2c433ee52fbf9fd15118b95c23d299f0ade772f7047669120ac44b5663b85bad`. After both established a
canonical application session through `Tox/I2P-construction`, the host stopped all three
server-side persistent service-front processes while preserving both i2pd routers, both SAM
listeners, the bridge adapter, and the exact private Destination-key files. Both guests observed
authoritative offline. Three distinct replacement processes loaded the same Destinations, after
which both guests confirmed a higher session epoch and received fresh text from the other guest.

This closes one service-process replacement window. It does not enable production `tox/i2p` or
qualify anonymity, independent routers, long-term availability, a private route-member payload, or
fleet behavior.

## Frozen topology and socket attribution

```text
router executable SHA-256     d5e89b4c2520ae5e3776a9c134b54200061b477f8b388bea60f60b07865753b5
router source-tree SHA-256    5ac86d648c0f211c145ea6686c730a946d593457c6b6189f3bf660884195ce4f
router source files           315
certificate-tree SHA-256      2274a8c3af138da62a37d45e6c3f9f2b775a3df07ca80452ded3f44a3cf1ff89
certificate files             21
reseed signature verification true
node-record-set SHA-256       fd68d12122b21347b54259bd263a1740afdc06e3d5ec14aa22b84897c1c44059
front count                   3
topology runtime              759.074 seconds
pair rendezvous               761.076 seconds
```

The exact `/proc/PID/fd` socket-inode join proves that server router PID 1843043 owns its loopback
SAM listener and 33 established public TCP remotes; client router PID 1843044 owns its SAM listener
and 32 established public TCP remotes. The export retains only counts and domain-separated
remote-set SHA-256 commitments. The service-front supervisor preserves those exact live process
objects through replacement; it never invokes router recovery.

## Exact fault and application lifecycle

```text
adapter SAM generation 1 ready
all three committed Destinations admitted
both guests online at authenticated epoch 1
front PIDs 1843085, 1843288, 1843300 terminated
both routers, SAM listeners, adapter listener, and egress shims remain live
both guests observe authoritative c-toxcore offline
front PIDs 1856071, 1856111, 1856147 start
all three private Destination keys load without identity drift
adapter remains on SAM generation 1
all three committed Destinations admitted after recovery
both guests online at authenticated epoch 2
client receives device fresh text; device receives client fresh text
```

The replacement interval is 68,615,045,586 ns. The adapter records 19 admitted streams, zero
denials, and all three commitments before and after recovery. Each initial forward audit contains
exactly `created, ready`; each replacement audit contains exactly `loaded, ready`; no front records
loss or creates a new key.

## Packet containment

| Role | IPv4 egress | UDP | Direct bootstrap | Direct peer | Capture SHA-256 |
|---|---:|---:|---:|---:|---|
| client | 1,509 | 0 | 0 | 0 | `2472284b02742d50af568d024b46f28886da755a77ac0b4f9ae9e3ac6e5ff6df` |
| device | 1,033 | 0 | 0 | 0 | `1e5714caa9c9c1a1e4f4a0b70a426debd0cb82b80a2c070cb1cd8719f2abdae1` |

The sole IPv4 destination in each capture is `10.0.0.1:39053`. No native Tox fallback appeared
during the outage or recovery.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.6rrdsdc_`. It allocates 1,613,824 bytes
across 20 declared evidence files plus its own manifest, reports `contains_secrets=false`, and omits
guest disks, injected identities, runtime state, the bootstrap secret, router datadirs, savedata,
and persistent Destination keys. The source-private proof allocated 2,459,967,488 bytes. Both forms
independently returned `passed` from the strict verifier.

```text
source-private manifest SHA-256  bb981984e73a72945337a0ac231b3f6ce16bf929f238f68d975755afa5b376f2
compact pair manifest SHA-256    18e224c08075823a3df5892af3e66ca0f15007ed9aaa7894484e3b36adb6ffef
compact-export SHA-256           0a64ca6c320d9b177e6d95133d004d9dc3e66ebfb21a4e1e88c3b47a0dda9a55
topology-final SHA-256           204d6276b18ce7be5da93b51fa827f20cceab4d80b82dfb526eb3f275fdb3977
```

Use three explicitly reviewed, currently reachable public numeric Tox TCP records:

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-i2p-construction i2p-service-restart \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p-construction \
  .sandwurm/exports/pairs/PAIR_ID i2p-service-restart
```

## Exact nonclaims and later gate

This is one bounded time window on one physical host, two local VMs, two local routers, three public
Tox records, and one router implementation/version. The next locally actionable I2P gate is the
already-planned private route-member proof carrying one exact authority-bound Ratox or sync payload.
Later record/time repetition remains necessary before any availability claim.

ADR 0219 later accepts that next layer for one 131,369-byte signed tree with zero reassignment while
native fallback remains ready. It does not retroactively add payload evidence to this fault proof or
qualify larger privacy-pinned objects.
