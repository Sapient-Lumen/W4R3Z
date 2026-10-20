# Sandwurm forced-TCP relay restart evidence — 2026-08-20

## Claim

Two concurrent IoTox NixOS guests under Sandwurm recovered a confirmed application session after
their sole controlled TCP relay disappeared and returned with the same identity. The test did not
infer success from process liveness or a bootstrap call: both guests first had to observe the session
and transport peer offline, and both then had to confirm over TCP at a strictly higher online epoch
and exchange fresh text in both directions.

This is the relay-interruption slice of the two-node fault gate. It is not link impairment, guest
restart, daemon replacement, Ratox latency, synchronization, public relay, or production evidence.

## Accepted observation

The verified compact export is:

```text
.sandwurm/exports/pairs/pair._36nsf1u
```

Both guests used IoTox `0.39.0 rev0039` and the pinned source-linked binary SHA-256:

```text
b5e58a4bb0e0d723f4e353f1faf8a0a49034b632225682efb7d35cab97c5408b
```

The fixture restarted exactly once, retained its original public key, and both guest receipts record:

```text
route                         forced-tcp
scenario                      relay-restart
initial online epoch          1
recovered online epoch        2
relay interruption observed   true
relay recovery observed       true
final observed connection     tcp
```

Digest bindings:

```text
client IoTox receipt   717693a6136e5469c3b2ba774433f2ced745831090cf7eab2d997740aafeb1ba
device IoTox receipt   38b9ff3116931d1326f8b0c61e424bead72d2ed5e3e8dcd6c501af5dbe37d2c1
client Sandwurm chain  974cabef362dd2df69d344c5a069df497e9a5287e24967517a34ed80c5dea403
device Sandwurm chain  b725ee532fe0a071d79a9082f96c6692d80fb4051fec4aae426702d9b3576234
```

Reverification command:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair._36nsf1u relay-restart
```

The verifier binds both content-free IoTox receipts to their Sandwurm live-chain receipts and rejects
a scenario/route mismatch, a restart count other than one, a changed relay key, either missing fault
observation, or a recovered epoch that does not strictly exceed the initial epoch.

## Secret boundary

The original proof root retained writable private guest disks, detailed runtime state, reusable test
identity copies, and the relay fixture secret key. The exporter omitted those classes, bound the
original manifest digest, copied only the verifier's seven-file allowlist, and reverified the 96 KiB
compact result before the private original was deleted. The compact export declares
`contains_secrets=false` and is the shareable evidence subset.
