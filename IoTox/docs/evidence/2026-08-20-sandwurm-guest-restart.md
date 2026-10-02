# Sandwurm device guest restart evidence — 2026-08-20

## Claim

A continuously running IoTox client NixOS guest recovered after the device guest crossed a real
kernel-boot boundary on its existing writable disk. The controlled TCP relay stayed live. The stable
client had to observe both transport and application-session offline, then confirm the same device
identity at a strictly higher online epoch and exchange fresh text in both directions. The device
receipt binds distinct pre/post boot-ID hashes and the client receipt binds an unchanged boot-ID hash.

This proves persisted-disk guest restart under the sole-machine Sandwurm topology. It does not claim
snapshot restore, power-cut durability, Ratox PTY survival, physical-host replacement, synchronization,
public-relay behavior, or production readiness.

## Two-epoch restart mechanism

Cloud Hypervisor attempted to reboot the original VM in place, but its virtiofs workspace backend did
not reconnect. After one bounded minute it exited status 1 with the vhost-user socket reconnect error,
matching Sandwurm's documented virtiofs reboot limitation. The first Sandwurm chain and live-launch
receipt bind that failure rather than hiding it.

The runner then launched a second Sandwurm epoch using the exact first prelaunch receipt. Its launch
therefore referenced the same writable runtime-root disk; it did not materialize another disk or
reinject identity files. A new virtiofs backend and VMM booted that persisted disk. The verifier
requires both the bounded first-epoch exit and the successful second chain.

## Accepted observation

The verified compact export is:

```text
.sandwurm/exports/pairs/pair.iph6w2qy
```

Both guests used IoTox `0.39.0 rev0039` and binary SHA-256:

```text
b5e58a4bb0e0d723f4e353f1faf8a0a49034b632225682efb7d35cab97c5408b
```

```text
route                              forced-tcp
scenario                           guest-restart
device guest restart count         1
relay/daemon/link restart counts    0 / 0 / 0
client initial/recovered epoch      1 / 2
device process-local epochs         1 / 1
client boot-ID digest changed       false
device boot-ID digest changed       true
device identity preserved           true
fresh confirmed replacement         true
post-restart text both directions   true
```

Digest bindings:

```text
client receipt             90d4fb1852a9dc81421d9caff4b3d37129bccb04763fbb15091a9d465f2b2a65
device receipt             1fbaa83167df619bccda107ef2cf1907a45430c4400f261b2888e69b0b78916c
client final chain         88c6791c4f239f7acf3d9bc37e07f3900b4ec14e8d921e56b18b9c15cc5087e1
device initial chain       92d1c6caf34be7a26ce7e5cb350911c7b825c75dd596987ac9f45577bfda3b3b
device initial live launch 58f0fccaac52ea2e77465c829ba719048ceb7ea4cc86189334fde0588cf92a3f
device final chain         7cf889573058f183b97c79ac73149aff6bf6a995ef089dc81ad64bd0def522da
source manifest            61a6742cccbf28fa51c7e67913cbe5c65289dc4ae9461765e721b79dd94da096
```

Reverification command:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.iph6w2qy guest-restart
```

The verifier rejects a missing first or second chain, an unrecognized initial VMM exit, a fresh-disk
path substitution, unchanged device boot identity, changed client boot identity, a missing stable-client
offline observation, a stale client epoch, or a missing fresh session/identity assertion.

## Secret boundary

The original proof retained both writable VM roots, saved IoTox state, reusable identity copies, and
the relay key. The compact exporter retained only nine verifier-consumed JSON files, bound every
digest, and reverified the 132 KiB export before private-source cleanup. It contains no disk, injected
identity, bootstrap secret, runtime journal, or boot ID in plaintext.
