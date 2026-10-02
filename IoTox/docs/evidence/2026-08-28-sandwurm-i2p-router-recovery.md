# Sandwurm actual-I2P router recovery evidence

Date: 2026-08-28

Status: accepted bounded two-IoTox actual-I2P construction evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`5428058b36b802ad4b3ff731c394aa6774fb09f0` and identical IoTox binary SHA-256
`2c433ee52fbf9fd15118b95c23d299f0ade772f7047669120ac44b5663b85bad`. After both established a
canonical application session through `Tox/I2P-construction`, the host killed only the client i2pd
router. The strict adapter stayed reachable while SAM was absent, both guests reached authoritative
offline, and a distinct router process reused the exact private datadir. Both guests then confirmed
a higher session epoch and received fresh text from the other guest.

This closes the first real two-guest I2P router-loss and application-recovery gate. It does not
enable production `tox/i2p` or qualify anonymity, independent routers, a service-front replacement,
private route membership, Ratox, sync, or an availability SLA.

## Frozen router trust and topology

The topology used the same two pinned routers, three persistent address-preserving fronts, three
exact-target egress shims, and strict bridge adapter as ADR 0216. Fresh router bootstrap additionally
selected and receipted the certificate bundle embedded in the exact source:

```text
router executable SHA-256     d5e89b4c2520ae5e3776a9c134b54200061b477f8b388bea60f60b07865753b5
router source-tree SHA-256    5ac86d648c0f211c145ea6686c730a946d593457c6b6189f3bf660884195ce4f
router source files           315
certificate-tree SHA-256      2274a8c3af138da62a37d45e6c3f9f2b775a3df07ca80452ded3f44a3cf1ff89
certificate files             21
reseed signature verification true
node-record-set SHA-256       a173e1f9455f3e1807cc2cb2acd63596ed7e9d15915a681de5a656963a5e87af
front count                   3
topology runtime              865.869 seconds
pair rendezvous               869.738 seconds
```

Each persistent service front records exactly one creation and one ready outcome with no loss. Raw
Destination names and keys remain private; only their three domain-separated commitments appear in
the export.

## Exact fault and application lifecycle

The accepted topology and bilateral guest receipts establish this sequence:

```text
adapter SAM generation 1 ready
six streams admitted; all three committed fronts represented
both guests online at authenticated epoch 1
old client router PID 1658175 terminated
bridge adapter listener reachable; client SAM listener absent
adapter generation 1 lost
both guests observe authoritative c-toxcore offline
new client router PID 1687953 starts over the same datadir
adapter SAM generation 2 ready
six streams admitted; all three committed fronts represented
both guests online at authenticated epoch 2
client receives device fresh text; device receives client fresh text
```

The router remained absent for 68,990,525,160 ns. Eight connection attempts were rejected as
`denied-sam-unavailable`; no unknown Destination or denial class appeared. The final accepted run
happened to reopen all three fronts, although the frozen rule needs only two committed admissions
after recovery because bilateral higher-epoch application traffic is the stronger liveness proof.

## Packet containment

Both TAP captures contain only TCP to the configured bridge adapter:

| Role | IPv4 egress | UDP | Direct bootstrap | Direct peer | Capture SHA-256 |
|---|---:|---:|---:|---:|---|
| client | 1,307 | 0 | 0 | 0 | `e47b7ef74925492d8999d52dd11a625a8668b7d9574999592ca2400613ef2053` |
| device | 1,440 | 0 | 0 | 0 | `555ffd7653615d402c0facfd7ef2ec329a439032803216f1990a16f6b10316bd` |

The sole IPv4 destination in each capture is `10.0.0.1:39053`. The route did not silently fall back
to native Tox during either the outage or recovery.

## Rejected attempts that changed the gate

The accepted proof follows four useful rejected runs:

1. The first live fault reached listener-positive/SAM-negative state and then found an undefined
   runner probe name. The runner now uses the existing numeric TCP probe.
2. The next run completed router and session recovery, but one guest exited immediately after its
   local text send while its peer had not yet received it. A bilateral receive barrier now prevents
   either guest from finishing early.
3. A fresh router bootstrap crossed the former 420-second limit while obtaining network data. The
   topology now selects the source-matched 21-certificate bundle, verifies signed reseed material,
   and applies one aligned 840/900-second startup policy through its child SAM tools.
4. The next run passed bilateral higher-epoch text but finalization rejected 81 bounded outage
   attempts and only two redundant post-recovery fronts. The evidence rule now preserves the
   meaningful invariants: bounded known denials, complete pre-fault population, committed
   generation-two admission, and bilateral application recovery.

All rejected source-private roots were removed with the guarded workspace cleaner after diagnosis.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.v_11i2me`. It allocates 1,761,280 bytes
across 18 files including its own manifest, reports `contains_secrets=false`, and omits guest disks,
injected identities, runtime state, the bootstrap secret, router datadirs, savedata, and persistent
Destination keys. The source-private proof allocated 2,462,814,208 bytes. Both independently return
`passed` from the strict verifier.

```text
source-private manifest SHA-256  864b8b69b81209d74c6e8452aeb5b123da57d2a1f310282fcd224e9a97f872b1
compact pair manifest SHA-256    10dda1d60381e89571472dd78112849f9f3676a6b3e1bca547bd08cd93014ba1
compact-export SHA-256           837832523da01fad32ef74f25c170337ab30bb4cb616703cd6157489a87789a3
topology-final SHA-256           adbd94f55f89a453cbbcc264a0685003fb8900ca0ba6c3c0b41700c767bcb564
```

Use three explicitly reviewed, currently reachable public numeric Tox TCP records:

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-i2p-construction i2p-router-restart \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p-construction \
  .sandwurm/lab/pairs/PAIR_ID i2p-router-restart
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p-construction \
  .sandwurm/exports/pairs/PAIR_ID i2p-router-restart
```

## Exact nonclaims and next gate

This is one bounded time window on one physical host, two local VMs, two local routers, three public
Tox records, and one router implementation/version. It proves neither anonymity, unlinkability,
timing resistance, availability, independent router administration, a latency SLA, fleet behavior,
nor production suitability.

The next locally actionable I2P gate should bind the already-frozen private route-member proof to an
actual-I2P worker and carry one exact authority-bound Ratox or sync payload. At this proof's
acceptance, server/front replacement and router-owned external-socket attribution remained separate;
ADR 0218 later closes those bounded construction items.
