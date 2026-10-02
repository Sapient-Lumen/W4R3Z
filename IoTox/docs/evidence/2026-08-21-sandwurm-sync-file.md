# Sandwurm synchronization-file evidence — 2026-08-21

## Claim

Two concurrent source-linked IoTox NixOS guests under Sandwurm converged and explicitly activated
one identical 4 MiB immutable `range-v1` file revision over each supported native carrier: direct UDP
and forced TCP. The forced-TCP guests disabled UDP, local discovery, DHT announcements, and hole
punching and used only the controlled TCP relay.

In each cell the device and client used distinct stable device and Tox identities. Both local ledgers
were explicitly migrated to v3. The publisher granted the remote client only `sync.subscribe`; the
subscriber granted the remote device only `sync.publish`. Both namespace records independently pinned
the same writer and subscriber principals. Friendship alone therefore did not satisfy either network
entrance.

The device built a canonical toxsync range index, committed artifact and manifest objects, and
published the stable-device-signed generation-1 HEAD last. The client requested the HEAD and two
request-selected Tox FileIds, received both through the ordinary source-linked c-toxcore file path,
verified and committed both objects, semantically verified the index/artifact pair, accepted the HEAD
last, and then separately activated its exact 32-byte record token. Both content-free receipts bind
the same identities:

```text
artifact bytes          4194304
artifact SHA-256         1de6e2103a31b5c18b763e77890345d93dfb615af400a4b90c0e0f1c4820fd4e
manifest bytes           786496
manifest SHA-256         3bb8ad40b5677466b9f83b77af9c17f08c7d57313ede8fb4733e2f1323cc1866
signed HEAD record       60ed8db76d5b2ac931449281e29762cdee0fb300f329072b5d97d853603983ac
generation               1
```

This accepts the genuine one-source, whole-object, explicit-activation baseline for M5B. It does not
prove interruption/resume, daemon or guest restart recovery, range reconstruction from a basis,
deterministic directory publication, cancellation, multi-source behavior, full-disk recovery,
rollback/fork fault injection, OTA execution, two physical hosts, or production readiness.

## Accepted observations

Both cells used source commit `cb7eac0db23d60b4624e0872abd5f996664fdaef`, IoTox
`0.39.0 rev0039`, c-toxcore `0.2.23` with the `iotox-file-rr1` scheduler, libsodium `1.0.22`, Argon2
`20190702`, and the same source-linked product binary:

```text
6e1d1c8636f6db8f0af3f359c1b85a53d14d5662113db3d5311e1c70bc1fda07
```

The independently reverified compact exports are:

```text
direct UDP  .sandwurm/exports/pairs/pair.uppm28y8  98304 allocated bytes
forced TCP  .sandwurm/exports/pairs/pair.7ufrcjtg  98304 allocated bytes
```

Digest bindings:

```text
direct-UDP source manifest  25f023cc6d5fd315fe85dc8e283e872d72184f66496b906afb4dac94225bbe09
direct-UDP client receipt   4073adeb7eb430647358b1b180c2419d1a533704a281dd2904076d5d9b02be16
direct-UDP device receipt   ee884ac13f19208b036e69ddb07dd6d218f94be35212f9c26ffef03749dedaa3
direct-UDP client chain     eea83070722bbef148db77d399286860bd98fe400c3a15f28379ce0b6f72bac3
direct-UDP device chain     32e7f1a7985e6a78d6a57696e694b1d58352fae678bec7cef6512a840fa04980

forced-TCP source manifest  32f1454bdf59f9c0f28de683938d403f5ef35324a9cfd8d85024004a0c5f0da5
forced-TCP client receipt   4f5ac8bd064c792c8bc676c8a614ee2259d22a97315c77272ba88d0ad4e2406e
forced-TCP device receipt   aefc5476a927b102246ae6226626eb639be658db39e581d64efc0fe11c78eab7
forced-TCP client chain     8606ae1fd89607b6730bada166f7e13da660c02ddd5cc923528c1283906cd1a9
forced-TCP device chain     5fd689bc6624586fa67725837f880ab0da918bf29e17548e5b07177cf285101c
```

Reverification:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.uppm28y8 sync-file
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.7ufrcjtg sync-file
```

## Secret boundary

The original ignored proof roots contain writable guest disks, copied reusable test identities,
authority and synchronization state, the fixed test-only RecallRoot fixture, and the temporary
bootstrap key. The compact exporter copied only the seven verifier-consumed JSON files, bound every
file plus the private source manifest digest, declared the omitted secret classes, and reverified each
result. The compact receipts contain no phrase, private key, raw peer key, file content, local path,
or guest disk.
