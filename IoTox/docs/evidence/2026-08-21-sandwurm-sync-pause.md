# Sandwurm synchronization live-pause evidence — 2026-08-21

## Claim

Two concurrent source-linked IoTox NixOS guests under Sandwurm paused and resumed one live receive
inside the same 8 MiB immutable `range-v1` pull over each supported native carrier: direct UDP and
forced TCP. The forced-TCP guests disabled UDP, local discovery, DHT announcements, and hole punching
and used only the controlled TCP relay.

Each cell rate-shaped the subscriber TAP, began the ordinary two-object pull, and required positive
authoritative c-toxcore provider position plus admitted incoming-transfer truth. The subscriber chose
one active transfer, retained its exact file number and request-selected 32-byte FileId, and invoked
the public `iotox file-control PEER FILE_NUMBER pause` operation. That same transfer reported
`state=paused`, `local-paused=1`, the same FileId, and one unchanged positive partial provider
position for 20 consecutive 100 ms samples. Accepted-HEAD and activation state remained absent.

The subscriber then invoked `resume` on that exact file number. The response retained the same FileId,
returned active state with local pause cleared, and the existing subscriber job completed normally:
both immutable objects were verified and committed, the signed HEAD was accepted last, and only an
explicit exact-token operation activated it.

Both carriers converged the same immutable identities:

```text
artifact bytes                    8388608
artifact SHA-256                   628137e2ec82540d278434e5214ec1f96765183ad6b8666d4a61fe1a91e2cea5
manifest bytes                     786496
manifest SHA-256                   4808af6e0e0fc52d19060299854af2a0937bc8b56532471df5b4b854f1ae9fd1
signed HEAD record                 e47ab54d788d82b86e5b6ea4ab5c47732c9b3f0a6a15bb8138a252671dd4b62c
generation                         1
direct-UDP paused position         38388 bytes
direct-UDP paused FileId           d906741cc79b3ecb1bee677fca1e16b890a8ba6ef08415054505c90a484616bd
forced-TCP paused position         68550 bytes
forced-TCP paused FileId           fe8b72739d3a7f203d5869c92105668892061aca208c77538332d45e59116359
minimum stable pause samples       20 on both roles in both cells
```

This accepts same-job, same-FileId live local pause/resume for M5B. It proves that partial receive
flow may stop without cancellation, disconnect, epoch replacement, accepted HEAD, or activation and
then continue through the ordinary complete-object path. It does not prove a peer-owned pause can be
cleared locally, durable pause intent, automatic pause policy, pause expiry, process or guest restart
of a paused transport handle, partial-byte reuse after handle loss, multi-source fairness, range
reconstruction, deterministic directories, two physical hosts, unattended OTA execution, or
production readiness.

## Accepted observations

Both cells used clean source commit `d18cfa3d2d5ff717f4b27209b0a8326698ae1ae9`, IoTox
`0.39.0 rev0039`, c-toxcore `0.2.23` with the `iotox-file-rr1` scheduler, libsodium `1.0.22`, Argon2
`20190702`, and the same source-linked product binary:

```text
7b101ea79fd21678ed6c90b1a38e83da319944d96d3b673a637744fcbd632919
```

The independently reverified compact exports are:

```text
direct UDP  .sandwurm/exports/pairs/pair.5qa1ubwd  98304 allocated bytes
forced TCP  .sandwurm/exports/pairs/pair.hd71hqag  98304 allocated bytes
```

Digest bindings:

```text
direct-UDP source manifest  8112ed74721e2af5554597a0690ccf6e870836f49f1e2027cc7f41d61a051a3f
direct-UDP compact export   0a80f12d108f2d61f224791935f66741273d103e03c6b87eed8ff901ccf45eda
direct-UDP client receipt   b74b7c15773b573391c69aaec4a05c41af184e3b1f2cdd38e80d17b1cd698472
direct-UDP device receipt   95769a2230db58d5403db2788014ee80cdcd22dc8797176b631c857a6712c11f
direct-UDP client chain     dd17613f292295d374bd953ad65b561a08690a23fde44b15d9e7aa014178648a
direct-UDP device chain     e1fe0519bc11440f81252384d87e3b617092337012adb8acc241fdea90cdbeff

forced-TCP source manifest  7e8cc084e9f3ff24c46d872dcc42baa01e0e1a4507fd8f4a741f2ae264ecdb5b
forced-TCP compact export   703a5d4631f348656f5d783cbac376044530276785d2c580fab37b07130e8d2f
forced-TCP client receipt   f8f5378beda6e7ad58dd1ff1a45a0c2103d41a2973c89d83efd0977c2bf0079c
forced-TCP device receipt   bca18448b8cd8ffe66b7137ee1c2dbfbb778aebcd0c49706ee064ad1a718112d
forced-TCP client chain     b88dd562a60ae84d74b489df8400224e7fa2f1068a4c504d88a7532866996e7f
forced-TCP device chain     4a484fdd5b8000ed91cba41d3ea53e269be9134fed2a8f893270b94fbee0e401
```

Reverification:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.5qa1ubwd sync-file-pause
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.hd71hqag sync-file-pause
```

## Secret boundary

The original ignored proof roots contain writable guest disks, copied reusable test identities,
authority and synchronization state, the fixed test-only RecallRoot fixture, and the temporary
bootstrap key. The compact exporter copied only the verifier-consumed JSON allowlist, bound every
file plus the private source manifest digest, declared the omitted secret classes, and reverified
each result. The compact receipts retain only boolean pause/resume classifications, bounded counters,
digests, one opaque FileId, and transport position—not content, private paths, phrases, keys, or guest
disks.
