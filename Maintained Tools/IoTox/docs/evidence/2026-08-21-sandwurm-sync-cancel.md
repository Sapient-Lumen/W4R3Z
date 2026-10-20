# Sandwurm synchronization cancellation evidence — 2026-08-21

## Claim

Two concurrent source-linked IoTox NixOS guests under Sandwurm explicitly cancelled one identical
8 MiB immutable `range-v1` pull over each supported native carrier: direct UDP and forced TCP. The
forced-TCP guests disabled UDP, local discovery, DHT announcements, and hole punching and used only
the controlled TCP relay.

Each cell rate-shaped the subscriber TAP, began the ordinary two-object pull, retained the
process-local job ID returned by `sync-pull`, and required positive authoritative c-toxcore receive
position plus two admitted FileId receives before invoking `sync-cancel JOB_ID`. Acceptance required
the same job to become terminal `cancelled`, all incoming transfers to leave live state, private
staging to become empty, and both accepted HEAD and activation state to remain absent after a settling
interval. Publisher and subscriber receipts bind those observations to one exact published revision.

Both carriers used the same immutable identities:

```text
artifact bytes             8388608
artifact SHA-256            628137e2ec82540d278434e5214ec1f96765183ad6b8666d4a61fe1a91e2cea5
manifest bytes              786496
manifest SHA-256            4808af6e0e0fc52d19060299854af2a0937bc8b56532471df5b4b854f1ae9fd1
signed HEAD record          e47ab54d788d82b86e5b6ea4ab5c47732c9b3f0a6a15bb8138a252671dd4b62c
generation                  1
direct-UDP job ID           11323572150965481825
direct-UDP cancelled bytes  72663
forced-TCP job ID           8017992176140393257
forced-TCP cancelled bytes  9597
admitted receives           2 in each cell
```

This accepts explicit process-local pull withdrawal after genuine provider progress for M5B. It
proves that IoTox terminally fences the local job and leaves no accepted or activated revision. It
does not prove that the remote publisher received a CANCEL packet, transport bytes stopped
immediately, a cancelled job survives daemon restart, partial bytes can resume, a shared committed
object is deleted, or a completed pull can be rolled back. It also does not prove live link-loss
recovery, guest restart, range reconstruction, deterministic directories, multiple sources,
full-disk/read-only recovery, two physical hosts, unattended OTA execution, or production readiness.

## Accepted observations

Both cells used clean source commit `aff7921ab1c41dd13d78e74f12f073ecd801b382`, IoTox
`0.39.0 rev0039`, c-toxcore `0.2.23` with the `iotox-file-rr1` scheduler, libsodium `1.0.22`, Argon2
`20190702`, and the same source-linked product binary:

```text
c025d8d34470ba674c3ed9b6fd9e74661fc369b1dc36da29d300103b78c6b774
```

The independently reverified compact exports are:

```text
direct UDP  .sandwurm/exports/pairs/pair.kfpfl6pz  98304 allocated bytes
forced TCP  .sandwurm/exports/pairs/pair.6x5cujaj  98304 allocated bytes
```

Digest bindings:

```text
direct-UDP source manifest  cfaa9e653a37cb52b87ca79d4f95457f7e26851e505b6bd588a453ddab9f2524
direct-UDP compact export   34d323f4035e5f73770607c9c994fe5194722932901e7860c4073b1fa69cff22
direct-UDP client receipt   7a9856e7c2abbd864932af4b57c9d6384b533e197a9f3aa72f28ce226e110148
direct-UDP device receipt   cc152c3050cfb14c4b8a16409e41c24f6864c2ce9d9c67c5671296512fc4b663
direct-UDP client chain     710b0513b93f0b395302e9318d5417bb01daf1626f6a8df7ca58a605a44ec4ef
direct-UDP device chain     373c45e202b11ab0901fdd8f914840262c180e4d9ae2075b4d1cbd27cf3a2c56

forced-TCP source manifest  88a05570fde04161a33a631a957dc5595f90fbf0a87a399aa686ac200736ee63
forced-TCP compact export   db10553d2986616ec1a685bb7e7960aa0d4edfcad97e626c510c7e8ee504a590
forced-TCP client receipt   3743e07adfad7e8921669b93946508f0561533a78eb9d9e10bde640a9c7da00a
forced-TCP device receipt   1610283948856be30a64682203952ae1dc685153c14535f42e133521cccfa51c
forced-TCP client chain     0fb177a82b02b5f6942d134dde3f225d99cfcf940631a4bf1198d8af01d5c864
forced-TCP device chain     7ab703d543d1e95454719ba8e30521d8327d3b7007d90e7209823ca0df737132
```

Reverification:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.kfpfl6pz sync-file-cancel
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.6x5cujaj sync-file-cancel
```

## Secret boundary

The original ignored proof roots contain writable guest disks, copied reusable test identities,
authority and synchronization state, the fixed test-only RecallRoot fixture, and the temporary
bootstrap key. The compact exporter copied only the verifier-consumed JSON allowlist, bound every
file plus the private source manifest digest, declared the omitted secret classes, and reverified
each result. The compact receipts retain only boolean cancellation classifications, bounded counters,
digests, a process-local random job ID, and aggregate transport position—not content, private paths,
phrases, keys, or guest disks.
