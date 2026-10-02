# Sandwurm bounded-range daemon-restart resume evidence

Date: 2026-08-29

Status: accepted direct-UDP and forced-TCP qualification

## Claim

After an unclean subscriber-daemon death during a 1 MiB missing-range receive, a fresh IoTox
process retained exactly one plan-bound strict prefix and no dead transport handle. After both peers
independently re-established transcript-bound authority, a distinct explicit pull reverified the
signed HEAD, manifest, and basis, derived the identical range plan, handed the inode to fresh
attempt/message/FileId identities, fetched only the suffix, verified the complete reconstructed
4 MiB artifact, accepted the HEAD last, and explicitly activated it.

## Fixture and acceptance

Both cells use the immutable private reused-key baseline. Generation 1 is a 4,194,304-byte basis.
Generation 2 changes one aligned 1,048,576-byte region, reuses 3,145,728 verified bytes, and uses the
same 786,496-byte range manifest. The selected range is shaped to 256 kbit/s until the crash barrier.

The client must observe at least 262,144 but fewer than 1,048,576 per-file bytes, then receive
`SIGKILL`. Acceptance requires status 137, exactly one canonical attempt partial, zero disposable
transport temporaries, a present stable-device-signed attempt journal, and unchanged predecessor
accepted-HEAD and activation records. Startup must preserve the same Tox address/savedata and the
exact partial length. The host waits for both client reconnect readiness and publisher-side
reauthorization before permitting the fresh pull. The two jobs, attempts, messages, and FileIds must
all differ; `interrupted = retained = restart-resumed`, and `restart-resumed + suffix = 1,048,576`.

`carrier-receive-position` is auxiliary-worker telemetry and is therefore zero on these primary
native routes. The crash predicate correctly uses the exact active per-file position and retains the
aggregate value only as a content-free diagnostic.

## Accepted cells

| Route | Compact proof | Interrupted = retained = resumed | Suffix | Pair span |
|---|---|---:|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.xg41pthc` | 281,055 | 767,521 | 223,208,250,517 ns |
| forced TCP | `.sandwurm/exports/pairs/pair.00992erw` | 276,942 | 771,634 | 548,301,180,454 ns |

Both were built from the source-linked working tree atop
`7f1f42c1cf6e672c9ac610a9dbf767745b21c217` (the receipt records the required `-dirty` suffix),
report `IoTox 0.45.0 rev0045`, use libsodium 1.0.22, and carry binary SHA-256
`a7eb9e0bc478125a2ced8f9f8c4bd89759364c12689948d594113ebc5fc3ab53`.

Their common final identities are:

- artifact SHA-256: `a9c0a0a26d2c01cf541e0d959cf3e8bed2f4aefcafaa713b5d1c104903a7a715`;
- manifest SHA-256: `575e41d269c20e5669d7d873999a9e7fdaf455eac3420f41e2b1b94273d7db93`;
- signed HEAD record: `d33125d9c857dfc7ddb855e093e2768312c6f1a1aeba5ee1ffc8d8c7988fd253`.

Direct client/device receipt SHA-256 values are
`45117d7452e17695e333f7dfae7edef438d1c15f3989ff5bb5dab8f57c453b57` and
`1c67c2390f22f5b1961869bb5bf45069b89b6ae448ad86d60796ead4775bf74f`.
Forced-TCP values are
`4aa93a17e409ef989c60d8d32ed816b3a185d1f8b31572a9e8e6298d253e5e17` and
`845e6ad172b0e8fd4fb2b486ce6d8011b83748304ac595f05de76311a993a2bf`.

Each secret-free compact root allocates 188,416 bytes and independently passes strict replay.
Direct compact pair-manifest/compact-export SHA-256 values are
`595a18111c6d5ab6833b1c9a6b80792c42dd082cd2e11415c705646ce8cc94f3` and
`01b466b2ffc7208237d40bd868c51e2e8f6f3eb2f47b98c4b76d6c58aec5c256`.
Forced-TCP values are
`864dde7e295b5b2f6fe68d23c42857b9cd44e11d9f8637f502a8154cd1947b74` and
`01570026538802d13152602237b83e84706bf6972d70b635b5191ef469730b10`.

## Scientific corrections retained

The first genuine run found a product defect before range admission: the original plan commitment
submitted the complete canonical plan to a hash API with a 64 KiB payload ceiling. ADR 0239 now uses
a fixed 32 KiB domain-separated hash chain and includes a greater-than-64-KiB regression. The next
run showed that primary-route aggregate receive telemetry is intentionally zero; the gate now uses
the concrete file position. A later run exposed a real two-sided timing boundary: local client
authority recovered before the publisher had observed the same session, so an immediate HEAD request
failed closed. The accepted gate adds an explicit bilateral reconnect barrier before repull; it does
not weaken authority or retry an admitted effect.

Compact export initially exposed a missing strict-inventory allowance for the new content-free
markers. The verifier now names exactly the ready, crash, reconnect, reacquired, publisher-armed,
publisher-offline, and publisher-recovered records. None of the rejected diagnostics is acceptance
evidence.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-file-range-restart-resume
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-file-range-restart-resume

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.xg41pthc sync-file-range-restart-resume
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.00992erw sync-file-range-restart-resume
```

The accepted compact IDs must be cited by a tracked Markdown file before a zero-retention cleanup;
the cleaner intentionally treats undocumented compact exports as superseded. Raw roots may be
removed only after raw verification, compact export, compact verification, and that citation.

## Exact nonclaims

This evidence does not prove a crash at the complete-bundle/final-chunk linearization, clean
shutdown checkpointing, full guest/kernel/power loss, disk-full behavior during retention or inode
handoff, I2P/Tor continuation, repeated late loss, four-plus carrier loss, concurrent multi-source
striping, two physical hosts, or a performance improvement. It does not resurrect old jobs,
messages, FileIds, file numbers, routes, workers, epochs, or transport handles.
