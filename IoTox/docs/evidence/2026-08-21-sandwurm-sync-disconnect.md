# Sandwurm synchronization disconnect evidence — 2026-08-21

## Claim

Two concurrent source-linked IoTox NixOS guests under Sandwurm safely retired an interrupted
8 MiB immutable `range-v1` pull and converged through an explicit fresh pull over each supported
native carrier: direct UDP and forced TCP. The forced-TCP guests disabled UDP, local discovery, DHT
announcements, and hole punching and used only the controlled TCP relay.

Each cell rate-shaped the subscriber TAP, admitted both request-selected FileId receives, and
required positive authoritative c-toxcore receive position before the host replaced both TAP qdiscs
with `netem loss 100%`. Both guests observed transport plus application-session offline. The
subscriber then exposed the old job as terminal `failed`, had no live incoming transfer or private
staging, and retained neither accepted HEAD nor activation. After link restoration, both guests
advanced from online epoch 1 to epoch 2 and retained one confirmed, authorized, route-correct epoch
for 50 consecutive samples. Only then did the subscriber issue a fresh pull, verify both complete
objects, accept the signed HEAD last, and explicitly activate its exact token.

Both carriers used the same immutable identities:

```text
artifact bytes                    8388608
artifact SHA-256                   628137e2ec82540d278434e5214ec1f96765183ad6b8666d4a61fe1a91e2cea5
manifest bytes                     786496
manifest SHA-256                   4808af6e0e0fc52d19060299854af2a0937bc8b56532471df5b4b854f1ae9fd1
signed HEAD record                 e47ab54d788d82b86e5b6ea4ab5c47732c9b3f0a6a15bb8138a252671dd4b62c
generation                         1
direct-UDP interrupted bytes       37017
forced-TCP interrupted bytes       56211
initial/recovered online epochs    1 / 2 on both roles in both cells
minimum stable recovery samples    50 on both roles in both cells
```

This accepts authenticated-epoch retirement and explicit whole-object retry after genuine link loss
for M5B. It proves that the subscriber cannot carry a live job, FileId, partial staging, accepted
HEAD, or activation across the retired epoch. It does not prove partial-byte resume, reuse of
unverified staging, automatic retry, file-transfer pause/resume, range reconstruction, deterministic
directories, multiple sources, guest restart, full-disk/read-only recovery, two physical hosts,
unattended OTA execution, or production readiness.

## Accepted observations

Both cells used clean source commit `4f051fe6ed37e438858af7de21becaa3d528474d`, IoTox
`0.39.0 rev0039`, c-toxcore `0.2.23` with the `iotox-file-rr1` scheduler, libsodium `1.0.22`, Argon2
`20190702`, and the same source-linked product binary:

```text
6e5121ded8480b0d894b4d43703f6ab103aa2514b6cfcef6d5238b18a04c88a4
```

The independently reverified compact exports are:

```text
direct UDP  .sandwurm/exports/pairs/pair.ip8h7ud4  98304 allocated bytes
forced TCP  .sandwurm/exports/pairs/pair.xi96v2re  98304 allocated bytes
```

Digest bindings:

```text
direct-UDP source manifest  1a5dbfdc26cd8b6af44158bf4107acbca7cc2be2132355613389aba06f2b7315
direct-UDP compact export   3e2c57a60b33706d21015677cb5ad939afed1b91d940aa4026bd4472c62ee2a8
direct-UDP client receipt   366444ead59eec9491256032231c6dc6cfe3795f163dd484d84fb04ebf8cbc33
direct-UDP device receipt   1faa28723a7517354bf755a87e530a0db96ea94727ed58b449fd20eacfd87c07
direct-UDP client chain     1738441cd0926ad819a415e962f8d2279502fb5b05663542c53766ac1503c750
direct-UDP device chain     6187af4c4b89b1b673a96fb678e181e032dce16279f7d116d574aadbf247be4b

forced-TCP source manifest  56badb6df76ea29f157362ed5dd87c37afd08f9d80fd2c40b7f88df49a54b974
forced-TCP compact export   7cb60afca1dde7df7d6217bbd4e29eaa3fe5837e56a247520cae6df75e35f5c6
forced-TCP client receipt   c917f961cfbe362a42149bd987a738a1be567e22283c098bcddcd8b1821ecf13
forced-TCP device receipt   ac9a51318ce5599ebf0f8739c197f6697c36ae06df2ab9f0ebc7cf938db29650
forced-TCP client chain     39518db6f8cb7bc391e4171b561456e84ea6b0c34e71d4992fd1a29db2ea8dc4
forced-TCP device chain     787e42dbd1c359922f1d2d1990c3efe92c97ccdc198696ed356c9c87be2643b4
```

Reverification:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.ip8h7ud4 sync-file-disconnect
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.xi96v2re sync-file-disconnect
```

## Scientific failures and repair

The first direct-UDP experiment restored connectivity and admitted the retry at the first confirmed
callback. A second natural connection flap safely failed that new job, demonstrating that confirmed
state alone was too weak as a laboratory release point. The gate now requires 50 consecutive
100 ms samples of one higher confirmed, authorized, route-correct epoch before retry.

A later experiment converged on the subscriber but timed out waiting for the publisher checkpoint.
The publisher recovery loop had retained its pre-disconnect authority command output rather than
resampling it with the session and route. The product had advanced and served the new transfer; the
evidence predicate was stale. The accepted source refreshes all three observations together and
exports an atomic publisher recovery probe. An explicit evidence-release barrier also keeps the
subscriber online until the publisher secures its stability and completion evidence.

## Secret boundary

The original ignored proof roots contain writable guest disks, copied reusable test identities,
authority and synchronization state, the fixed test-only RecallRoot fixture, and the temporary
bootstrap key. The compact exporter copied only the verifier-consumed JSON allowlist, bound every
file plus the private source manifest digest, declared the omitted secret classes, and reverified
each result. The compact receipts retain only boolean cleanup/retry classifications, bounded
counters, epochs, digests, aggregate transport position, and route identity—not content, private
paths, phrases, keys, or guest disks.
