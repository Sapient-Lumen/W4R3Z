# Sandwurm synchronization publisher-guest-restart evidence — 2026-08-22

## Claim

Two concurrent source-linked IoTox NixOS guests under Sandwurm safely retired an interrupted 8 MiB
immutable `range-v1` pull when the publisher guest rebooted, recovered the publisher's exact durable
publication from its persisted writable disk, and converged through an explicit fresh pull over each
supported native carrier: direct UDP and forced TCP. The forced-TCP guests disabled UDP, local
discovery, DHT announcements, and hole punching and used only the controlled TCP relay.

Each cell rate-shaped the stable subscriber TAP and required positive authoritative c-toxcore
receive position before asking the publisher guest to reboot. The subscriber observed the publisher
offline, exposed the old job as terminal `failed`, and retained no live incoming transfer, private
staging, accepted HEAD, or activation. The initial Cloud Hypervisor chain then recorded its bounded
reboot exit. A successor Sandwurm chain consumed the exact original prelaunch receipt and writable
runtime-root disk; host identity injection was not repeated.

The successor retained the same Tox and stable-device identities, namespace policy, authority
ledger, source, immutable objects, and stable-device-signed publication HEAD. It validated the source
and both stored objects against the persisted publication record rather than publishing a new
generation. The stable subscriber advanced from online epoch 1 to epoch 2 and held that exact
confirmed, authorized, route-correct epoch for 50 consecutive 100 ms samples. Only then did it issue
a new pull, verify both complete objects, accept the signed HEAD last, and explicitly activate the
exact token.

Both carriers recovered the same immutable identities:

```text
artifact bytes                    8388608
artifact SHA-256                   628137e2ec82540d278434e5214ec1f96765183ad6b8666d4a61fe1a91e2cea5
manifest bytes                     786496
manifest SHA-256                   4808af6e0e0fc52d19060299854af2a0937bc8b56532471df5b4b854f1ae9fd1
signed HEAD record                 e47ab54d788d82b86e5b6ea4ab5c47732c9b3f0a6a15bb8138a252671dd4b62c
generation                         1
direct-UDP interrupted bytes       2742
forced-TCP interrupted bytes       20565
client online epochs               1 / 2 in both cells
minimum stable recovery samples    50 on both roles in both cells
publisher boot ID                  changed in both cells
stable subscriber boot ID          unchanged in both cells
```

This accepts persisted publisher-guest restart recovery for M5B. It proves controlled
operating-system reboot, exact durable publication survival, authenticated-epoch retirement, and an
explicit whole-object retry. It does not prove abrupt power loss, partial-byte reuse, range
reconstruction, automatic retry, durable pause recovery, corrupt-object repair, full-disk/read-only
recovery, deterministic directories, multiple sources, two physical hosts, unattended OTA execution,
or production readiness.

## Accepted observations

Both cells used clean source commit `f26126e17fe22df1f6cd709ea69005ea2552261d`, IoTox
`0.39.0 rev0039`, c-toxcore `0.2.23` with the `iotox-file-rr1` scheduler, libsodium `1.0.22`, Argon2
`20190702`, and the same source-linked product binary:

```text
7b101ea79fd21678ed6c90b1a38e83da319944d96d3b673a637744fcbd632919
```

The independently reverified compact exports are:

```text
direct UDP  .sandwurm/exports/pairs/pair.x3h41g9b  139264 allocated bytes
forced TCP  .sandwurm/exports/pairs/pair.9wfzoss6  139264 allocated bytes
```

Digest bindings:

```text
direct-UDP source manifest          352149e02082ca62e987c3368eef41efd68c44c0b2f659cc8a98d012bfd71b17
direct-UDP compact export           265d7d2d7db14f3484e74ee24009aef5c169cd34df47caac0a172d1193300d4a
direct-UDP client receipt           4c4179383a0dbcc05d85321b87b0b8157fd6df4077959768b45d7c5fba5b1c0e
direct-UDP successor receipt        29ea002c8cd93ea4a0c6b8e584f5891cb2c442822d1e383bd46563acdbc6539f
direct-UDP client chain             be601731ee6cb0096db6c339c49391a76770830a372a5d60b9e6ac890048277c
direct-UDP successor chain          5db1ccc18b1fbcabe5c0d432ef0de263edd7efa94c55aa598006849988d85905
direct-UDP initial device chain     9f7a9dc2f10105f55d49d6816d36e1c3ff82c38601ba73417732f4c952d5e1e5
direct-UDP initial device launch    6b308847303286a44c8b97849cbfac91e60ac311c07b6fdc615197e5b7e550ab

forced-TCP source manifest          172f00f7762dc4fd9c979e4388a584b33af49334c6bf0f077cc3ebb1ab9cf3b4
forced-TCP compact export           942e4b167704c9177c2506e36e09786fbb535230bdd20c7f0d94e01b652a0848
forced-TCP client receipt           9dc4db7c2dfcdddc68f61c4d40e828c1ebde37b4e9287a8947f65ed3c722e5bf
forced-TCP successor receipt        4197c9112ba04c873740608f65a479e4b05d50abc9a655535adf452912c6a227
forced-TCP client chain             e67e1cb8bc2da78676712f925fa4f1966b21c1ed04b7ec368b232695310dd73b
forced-TCP successor chain          61d824370561d7c6d31e910f9aa2e62e10916a1cd8ddf28d4bf89a127f9aa54c
forced-TCP initial device chain     5c264297bf570dd6ce4d536bcfe4e08bb70f6eeab673c7c818d9d4f5ba42c778
forced-TCP initial device launch    4875976c2caafe89d8cd0c446003c7af1191a1b6b77e26a03c3a5074b52540e4
```

Reverification:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.x3h41g9b sync-file-guest-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.9wfzoss6 sync-file-guest-restart
```

## Scientific failures and repair

The first direct-UDP construction reached partial staging, subscriber cleanup, and the expected
Cloud Hypervisor reboot failure, but the host allowed only 60 seconds for a VMM which deliberately
uses a one-minute virtiofs reconnect window before its bounded exit. The host wait now permits 120
seconds without weakening the required status-1 launch and `live:console-not-observed` chain records.

The first forced-TCP construction then proved partial staging and cleanup but Sandwurm's inherited
480-second guest-receipt watchdog cleanly shut down the stable subscriber during the second relay
convergence. This scenario now receives a bounded 960-second outer watchdog, a 600-second recovery
phase, and immediate failure if either chain exits before both recovery markers. Ordinary scenarios
retain their 480-second bound.

## Secret boundary

The original ignored proof roots contain writable guest disks, copied reusable test identities,
authority and synchronization state, the fixed test-only RecallRoot fixture, and the temporary
bootstrap key. The compact exporter copied only the verifier-consumed JSON allowlist, including both
publisher VMM epochs, bound every file plus the private source manifest digest, declared the omitted
secret classes, and reverified each result. The compact receipts retain only boolean reboot,
cleanup, retry, identity, and convergence classifications; bounded counters and epochs; boot-ID,
revision, binary, and chain digests; and aggregate transport position—not content, private paths,
phrases, keys, or guest disks.
