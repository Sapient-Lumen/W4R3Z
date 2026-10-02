# Sandwurm fail-closed actual-I2P sync-loss evidence

Date: 2026-08-28

Status: accepted bounded signed-class no-downgrade and recovery evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`827a661ea63f0ba4e35df09cd5b18bd228ef73b1` and identical IoTox binary SHA-256
`d0021c91efad9c0cf5a6e5e6be247ae7811dc7722a9eb434e411bd603ee6c05d`. The subscriber pinned one
pull to `fail-closed tox/i2p-construction`. After 69,921 bytes arrived through the exact
route-set-v2-signed I2P member, the host stopped only the client i2pd process while a native member
remained ready. IoTox fenced the original job, counted one carrier loss and one blocked job, and
made zero reassignment.

A distinct router process reused the same private datadir. Adapter generation two and the exact
signed member recovered without restarting the IoTox worker. The original transfer remained fenced
until explicit cancellation; a new job ID then fetched and activated the same immutable 131,369-byte
tree through the same carrier. This closes the bounded ADR 0226 gate. It does not enable production
`tox/i2p`, authorize implicit transfer revival, prove anonymity, or establish an I2P throughput or
availability bound.

## Exact fault and synchronization lifecycle

The content-free joined evidence establishes:

```text
source revision                    827a661ea63f0ba4e35df09cd5b18bd228ef73b1
product revision                   rev0045
signed tree content bytes          131,157
signed tree payload bytes          131,072
positive pre-fault position        69,921 bytes
old client router PID              745251
new client router PID              799518
router/SAM fault hold              62.453 seconds
loss observation                   33.251 seconds after stop
route recovery                     30.441 seconds after router replacement
carrier losses                     1
blocked fail-closed jobs           1
route recoveries                   1
worker restarts                    0
reassignments                      0
old job explicitly cancelled       true
replacement job distinct           true
replacement carrier identical      true
```

The original and replacement process-local job IDs are retained in the secret-free host record and
guest receipt. They are evidence identities, not stable protocol identifiers. The carrier itself is
represented only by domain-separated SHA-256 commitment
`0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c`.

The outage oracle is deliberately stronger than failure to make progress. The bridge listener stayed
reachable while the client SAM listener was absent, generation-one loss was audited, and the native
member stayed ready. A silent downgrade therefore would have been possible mechanically and is
rejected by the observed zero reassignment. Generation two admitted all three committed service
fronts; the original worker identity remained stable and reported one recovery with no restart.

## Packet containment and topology

The guests intentionally carry a mixed native/I2P route set, so their captures contain both native
Tox traffic and TCP to the strict local adapter. Every adapter-bound TCP packet remains confined to
`10.0.0.1:39053`; neither capture contains an unexpected network-context packet.

| Role | IPv4 egress | Native UDP | Adapter packets | Unexpected | Capture SHA-256 |
|---|---:|---:|---:|---:|---|
| client | 6,507 | 5,075 | 1,332 | 0 | `c638c5cc3cc37b149a89852664d6f021d9a23dd3a7f79b2985fb7d3f7c297a49` |
| device | 6,345 | 4,710 | 1,540 | 0 | `fefb2dd9e54753782bfaeb84fe1020423359e44bcaf1127a0b013d13bf125c65` |

The exact i2pd executable, 315-file source tree, 21-file certificate tree, and signed-reseed setting
match the earlier accepted I2P construction gates. The final topology records one client-router
replacement, zero service-front replacement, three preserved Destination commitments, exact
router-owned SAM listeners/public sockets, six known SAM-unavailable denials during the fault, and
no unknown adapter outcome.

## Rejected attempts and fixture correction

The first genuine run proved the full no-downgrade interval but did not recover authenticated-ready
inside the host's 900-second bound. A content-free recovery heartbeat was added instead of relaxing
the predicate. The instrumented repetition proved exact worker recovery with zero restart and zero
reassignment, then showed that its fresh 16 MiB object could not finish inside that same bound at the
observed few-kilobyte-per-second rate. That was the already-known large-object I2P carrier-epoch and
throughput boundary, not a route-recovery failure.

The accepted fixture therefore reuses ADR 0219's qualified 131,369-byte tree. The host still waits
for at least 65,536 positive bytes before stopping the exact router, so the remaining object bytes
plus the outage preserve a deterministic mid-transfer fault window. No authority, class pin,
fail-closed, cancellation, recovery, or same-carrier predicate changed. The rejected source-private
proof roots were removed by the guarded cleaner after their diagnostic conclusions were retained.

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.jbr89_gc`. It allocates 6,656,000 bytes
across 19 files including its inventory, reports `contains_secrets=false`, and omits bootstrap secret
state, guest disks, injected identities, and runtime state. The source-private proof allocated
2,453,106,688 bytes. Both independently return `passed` from the strict verifier.

```text
source-private manifest SHA-256  f3bcc690fbfda6a0c1208e01002a76e41fec533e792f785cb4c05f56e0ae24d8
compact pair manifest SHA-256    efcc9b37464da714f2c1a4381d582637ddaf990ac1fa8b72e5e6be64d9cec0c1
compact-export SHA-256           e64f905e93e3b7a951373b89d74ae3fdf045626eac1441c811e7defad71c6788
fault record SHA-256             2b37edc79278ea090b6047815c98b43ed1678e0bca2fe74255c0b41e5a19e814
topology-final SHA-256           bda3759f92791fbd1097991ad028a760d612ca6af6713cc9aaf37c02799e70e0
client receipt SHA-256           4347c7f98b32f429644b178d7d0b0979b41666836e7ca0d589251b0ce56e4293
device receipt SHA-256           499f97250b6f06bf139a55c9c270a0e970e391494bb1d2047a0346c15e7eb1d6
```

Use three explicitly reviewed, currently reachable public numeric Tox TCP records:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-i2p-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/lab/pairs/PAIR_ID sync-tree-route-private-actual-i2p-loss
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID sync-tree-route-private-actual-i2p-loss
```

## Exact nonclaims and next gate

This is one bounded time window on one physical host, two local VMs, two local I2P routers, three
public Tox records, and one router implementation/version. It proves exact signed-class fail-closed
behavior and explicit fresh recovery under that construction. It proves neither anonymity,
unlinkability, timing resistance, independent router administration, a performance SLA, nor fleet
behavior.

The next protocol edge for large privacy-pinned objects remains digest-bound auxiliary chunk/range
transfer. The next evidence edges remain repeated/very-late loss and later record/time populations;
none is a reason to silently promote `tox/i2p-construction` to production `tox/i2p`.
