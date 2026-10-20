# Sandwurm forced-TCP link interruption evidence — 2026-08-20

## Claim

Two concurrent IoTox NixOS guests under Sandwurm recovered after a complete controlled packet
blackout on both task-owned TAP paths. Both guests, both IoTox daemons, and the same controlled TCP
relay remained live. Each peer had to observe both its transport peer and confirmed application
session offline before the runner restored packet flow. Acceptance then required confirmed TCP at a
strictly higher online epoch and fresh text in both directions.

This proves the forced-TCP link-interruption slice. It is not partial-loss, guest restart, Ratox
keypress latency, synchronization, public-relay, physical-link, or production evidence.

## Mechanism selection

The first experiment lowered both TAP devices and later raised them. Both guests correctly observed
offline, but Cloud Hypervisor did not recover guest reachability after the host TAP carrier returned;
neither guest could reach the host and neither TCP-relay connection reappeared. That bounded run
failed without an IoTox receipt and was rejected.

The accepted experiment kept both TAP carriers `UP,LOWER_UP` and atomically replaced each root qdisc
with `netem loss 100%`. After bilateral offline observation, deleting the netem qdiscs restored the
host default `fq_codel` qdiscs and packet flow. This isolates network loss from VMM carrier hotplug
behavior and leaves a clean basis for later seeded delay/loss/reorder profiles.

## Accepted observation

The verified compact export is:

```text
.sandwurm/exports/pairs/pair.a1o_q4gl
```

Both guests used IoTox `0.39.0 rev0039` and the pinned source-linked binary SHA-256:

```text
b5e58a4bb0e0d723f4e353f1faf8a0a49034b632225682efb7d35cab97c5408b
```

```text
route                           forced-tcp
scenario                        link-interruption
link interruption count         1
relay/daemon restart counts      0 / 0
client initial/recovered epoch   1 / 2
device initial/recovered epoch   1 / 2
bilateral interruption observed  true
bilateral recovery observed      true
final observed connection        tcp
post-recovery text both ways     true
```

Digest bindings:

```text
client IoTox receipt   483cc65dbccebe7c239d8bf8aefd74296d277703b3d27df04036bb105fd0646a
device IoTox receipt   2a4d2b478dd97253d34a08f5249930ff7903fe7dea57c7c784e5c93b72b0ffda
client Sandwurm chain  bebb0926c4fe051f62b3853153f9fc684dac37272c4264cab25525176d09d6b6
device Sandwurm chain  4421d9ef98bead12c3872f6f6c1eae4677904dd233160b964637c5daea80a6c7
source manifest        b36f8d2c22c8f3715c969d247f2e6ef11e7e28fbb8f938b6501e91bbd6c42c60
```

Reverification command:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.a1o_q4gl link-interruption
```

The verifier rejects route/scenario disagreement, a link interruption count other than one, any
relay or daemon restart, one-sided interruption or recovery, or either recovered epoch failing to
strictly exceed its initial value.

## Secret boundary

The original proof root retained writable private guest disks, detailed runtime state, reusable test
identity copies, and the bootstrap fixture secret key. The exporter omitted those classes, bound the
original manifest digest, copied only the verifier's seven-file allowlist, and reverified the 96 KiB
compact result before private-source cleanup. The compact export declares `contains_secrets=false`
and is the shareable evidence subset.
