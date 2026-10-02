# Sandwurm Ratox idle construction evidence — 2026-08-20

## Claim

Two concurrent IoTox NixOS guests under Sandwurm completed matched 40-sample serialized real Ratox
terminal keypress-to-render cells over observed direct UDP and forced TCP. Each trial crossed the private controller socket,
the genuine Tox route, the authorized remote Ratox host, a raw/no-echo PTY byte-echo process, the
return route, and a local pseudoterminal render copy. Acceptance required exact one-byte sequence
spans and one joined remote `input-staged`, `input-committed`, and `output-appended` event triple per
trial.

This accepts the first two complete-service R7 construction cells. It does not qualify the frozen
1,000-sample release gate, any bulk-load condition, a dedicated route, guest restart,
route faults, two physical hosts, or production support.

## Accepted observation

The verified compact exports are:

```text
direct UDP  .sandwurm/exports/pairs/pair.b8y5m37j
forced TCP  .sandwurm/exports/pairs/pair.9dw2uul1
```

The direct cell used source commit `5fcdae7`; the forced-TCP cell used documentation-only successor
`6d6feeb`. All four guests used the same pinned source-linked binary:

```text
aa9092a8735ec8d8a9fe7cc510ea4f336843321fd13f038281aa5b175ad33e04
```

Controller-clock measurements use nearest-rank percentiles and microsecond monotonic timestamps:

```text
metric                    minimum    p50       p95       p99/max    mean
UDP keypress -> output     26.041 ms  44.837 ms 63.134 ms 66.815 ms 45.750 ms
UDP keypress -> render     26.513 ms  45.442 ms 63.941 ms 67.435 ms 46.308 ms
UDP owner queue             0.009 ms   0.028 ms  0.059 ms  0.115 ms  0.033 ms
TCP keypress -> output     44.730 ms  64.831 ms 103.674 ms 107.987 ms 72.082 ms
TCP keypress -> render     45.224 ms  65.454 ms 104.139 ms 109.183 ms 72.688 ms
TCP owner queue             0.010 ms   0.023 ms  0.058 ms   0.081 ms  0.029 ms
```

All 80 accepted inputs produced exactly one output and render. No sample exceeded 250 ms. Remote
stage-to-PTY-output p95 was effectively unchanged: 27.377 ms under UDP and 27.452 ms under TCP.
Forced TCP instead added about 20.012 ms at p50 and 40.198 ms at p95 to the complete render path.
Because the remote queue/PTY component did not grow with it, the added tail lies outside remote
owner-class queueing and PTY execution, consistent with transport/iteration and return delivery.

The UDP cell passes the provisional p99 <= 100 ms, zero 250 ms miss, exact-delivery, and owner queue
p99 < 2 ms targets, but its p95 of 63.941 ms is above the provisional direct-route target of 50 ms.
The TCP cell passes the miss, delivery, and queue targets but exceeds both 50 ms p95 and 100 ms p99.
Because the release decision requires 1,000 samples per cell, these are diagnostic signals rather than
qualification verdicts. Bulk cells must preserve the full-path measurement before a dedicated-route
decision.

Digest bindings:

```text
client receipt              284b14c859c59852db212eacbd1626ac659f1527245d45e6f91f7ebe038f5807
device receipt              ad57a025aba9497f34af1330142e409f0f07f84507628c54988ed375a90cce9e
client Sandwurm chain       12f897b8d2eb1f2e13bbfb3b97bca49051c782767bd15bdeb1389e5db36581f2
device Sandwurm chain       822702441250ccc137f0e5a570a322abc187dbcb33fcd56afddd573395bf1dce
controller capture          28a07d4821aea0fed89accbe868ee59a648a1a402e642964e97558b7a0eab083
remote host events          369e738ba7df56e33455e5c861f4efb7bfc188b51be6a24a365d8980a8d39df8
remote host final status    0fa51defec27faf63e817fc19eeda5738aa80d17e935e9e7157f2f07244f51f6
source manifest             e1c1486a417756f9d70c9d97eaf89c7752d2f6a03bf199f8159967345acb4df5

forced-TCP client receipt   449120645686a31fadf06eaf2c2990527513877b34255bf8cc040a43ad0e8bd5
forced-TCP device receipt   e9a70e7525b277df3eb6664c23dc4351893ca47a8f6c094b6213567ef7ef200c
forced-TCP client chain     dc56eb076af75e05233fbe4f3facb69069c465740b14c166a013aec40b89df78
forced-TCP device chain     8c3c2062dc7035f24c90dcd87232472a14ebaf357810e1b091e3389bb79dec87
forced-TCP capture          7a1dabb76087ca97549d7c3655c20b6bcb969c8e4921124ff954ed65f484135f
forced-TCP host events      ac71807b7b6721d11c749f44439faedd852235a65b72611d117f0007ea82b369
forced-TCP host status      de1439fa5d90ec8f65b32ef32fc19d5dced47670a495169720969d022a79e144
forced-TCP source manifest  3a30b62a6b7e49ad560661ad319bc164f6d5a9d31071b33f29e8fc7376255113
```

Reverification command:

```sh
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.b8y5m37j ratox-idle
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.9dw2uul1 ratox-idle
```

## Secret boundary

The original proof root contains private writable guest disks, copied reusable identities, runtime
state, the fixed test-only RecallRoot fixture, and the bootstrap secret. The compact exporter retained
only eleven verifier-consumed JSON/text/TSV files per route, bound both source manifests and every
retained digest, and reverified each 168 KiB result. Neither contains a guest disk, injected identity, bootstrap secret,
terminal content, raw peer key, or RecallRoot phrase.
