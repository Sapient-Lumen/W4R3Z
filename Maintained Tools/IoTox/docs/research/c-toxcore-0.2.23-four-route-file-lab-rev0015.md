# c-toxcore 0.2.23 four-route file laboratory — rev0015

Date: 2026-08-15. Status: founding-host research, not a bonded-transport specification.

## Question

Does a bulk transfer hit a ceiling owned by one Tox connection, and can independent Tox routes
between the same two logical IoTox device identities escape it?

The controlled comparison holds total payload constant:

```text
1 route x 1 file
1 route x 4 simultaneous files
2 routes x 1 file each
4 routes x 1 file each
```

Each route is an independent source-linked c-toxcore instance, savedata identity, friendship,
confirmed IoTox session, owner thread, and socket. The four A processes copy one test-only stable
device identity; the four B processes copy another. Route keys remain distinct. This represents the
data-plane shape of two logical nodes but is not a product architecture: four independent agents do
not yet share one authority/store coordinator.

`tools/run-four-route-lab.sh` provisions exactly eight private route identities and two private
device identities, reuses immutable clean baselines by default, destroys copied work state, divides
one constant byte count over the selected streams, verifies every destination byte, rotates phase
order between trials, and records process, event, and host-network deltas. The retained report
contains hashes only; the ignored cache contains the secrets.

## First result: a correctness failure, not a speed result

The initial 1 MiB run stopped deterministically after 74,034 bytes. The outgoing journal reported
IoTox library failure wrapping c-toxcore error 7, `TOX_ERR_FILE_SEND_CHUNK_SENDQ`. The sender then
removed its local transfer without cancelling the provider transfer, leaving the receiver live.

The provider contract explained the boundary:

- `tox.h` says to call `tox_file_send_chunk` in response to the chunk-request callback and send the
  complete requested length;
- `Messenger.c` defines a 1,371-byte maximum file payload from the 1,400-byte crypto packet;
- `do_reqchunk_filecb` owns a per-friend free-slot count and may loop 128 times per file;
- its own comment says the loop depends on sending chunks from inside the callback;
- `send_file_data` reserves connection queue slots and returns queue-full when the friend crypto
  connection cannot admit another packet.

IoTox had emitted as many as 128 callbacks to its event thread and only then called back through the
owner queue. c-toxcore therefore requested ahead against state that had not been updated; the later
calls filled the connection queue. ADR 0057 replaces that path with a transfer-scoped source called
synchronously inside the provider callback, preserves the opened-file integrity checks, and
retains an asynchronous bookkeeping event that cannot send twice. The exact mock now has a strict
mode that returns `SENDQ` for any call outside the callback; a multi-chunk regression passes in that
mode.

## Second result: IoTox observability hid route behavior

After the callback repair, the first genuine shakedown completed but four routes were slower. The
raw 1 MiB result was:

| Topology | Elapsed ms | MB/s | CPU ticks | Process `wchar` bytes |
|---|---:|---:|---:|---:|
| 1 route / 1 stream | 3,170 | 0.331 | 648 | 6,061,894 |
| 1 route / 4 streams | 7,400 | 0.142 | 1,472 | 8,116,874 |
| 2 routes | 3,195 | 0.328 | 1,071 | 6,025,194 |
| 4 routes | 4,681 | 0.224 | 1,973 | 6,272,161 |

The total eight-process CPU counters use the host's 100 ticks/second. The one-route phase consumed
about 6.48 CPU-seconds during 3.17 wall-seconds and wrote nearly six bytes of process-visible data
for each payload byte. Source inspection showed why: every healthy 1,371-byte request and receive
event rebuilt complete global and per-peer transfer directories, atomically replaced many scalar
files, rewrote status, and appended the global event journal.

That work was observational, not transfer truth. IoTox now still consumes and counts every required
event, but samples healthy nonterminal journal/projection updates at 250 ms. Offers, controls,
failures, terminal events, and dropped-event evidence remain immediate. A structured `files` query
forces exact projection.

The same 1 MiB shakedown after that change was:

| Topology | Elapsed ms | MB/s | CPU ticks | Process `wchar` bytes |
|---|---:|---:|---:|---:|
| 1 route / 1 stream | 2,204 | 0.476 | 40 | 1,355,722 |
| 1 route / 4 streams | 2,339 | 0.448 | 68 | 1,564,590 |
| 2 routes | 1,640 | 0.639 | 51 | 1,378,238 |
| 4 routes | 1,110 | 0.945 | 69 | 1,476,877 |

For the one-route control, this removed 93.8% of measured IoTox process CPU ticks and 77.6% of
process-visible writes while reducing elapsed time 30.5%. Four-route speedup changed from 0.67x to
1.98x. This before/after result locates a real shared local bottleneck and demonstrates why it had
to be removed before drawing transport conclusions.

## Replicated 8 MiB result

The qualification run used the rebuilt source-linked standalone, all UDP peer routes, three trials,
constant 8,388,608 payload bytes per phase, and rotated topology order. All 12 phases completed
byte-identically. No transport event was dropped.

| Topology | Median ms | Median MB/s | Speedup | Parallel efficiency |
|---|---:|---:|---:|---:|
| 1 route / 1 stream | 6,000 | 1.398 | 1.00x | — |
| 1 route / 4 streams | 6,129 | 1.369 | 0.97x | — |
| 2 routes | 4,510 | 1.860 | 1.33x | 66% |
| 4 routes | 3,681 | 2.279 | 1.62x | 40% |

The decisive control is four simultaneous files on one route: it does not improve throughput.
Four files over four independent Tox connections do. The c-toxcore implementation and the measured
shape jointly make a per-friend crypto connection queue/congestion controller the leading candidate
for the bondable ceiling. This is an inference, not a provider-internal profile: all routes also
share the host kernel, loopback path, storage, memory bandwidth, and scheduler, which explains why
four-route scaling is sublinear.

A single 32 MiB exploratory run retained the same direction but showed the expected warm-state and
shared-ceiling effects: 1 route 9.752 s, 2 routes 8.026 s (1.21x), 4 routes 6.690 s (1.46x), and
four streams on one already-warmed route 8.306 s (1.17x). Because this trial was not replicated and
phase order affects warmed congestion state, it is supporting evidence only.

## Exact evidence identity

```text
base-repository-commit=303c1a602f5bbfabccc0a07f76452b99f1579f86
harness-sha256=f2b50f6f6684c27c4e923d5634af4ca04121f3300d1607f3aea6d06090aa5967
standalone-binary-sha256=01b47ba3bdbbc8fdcfef8d1d63b164681731444e96d5c1f8669f6d24b7ff6a4b
replicated-report-sha256=ca760978ddd3a673bd6a057f3a3eb389cdd3f5d4d6e8542aa6e3f771c66a6b86
provider=c-toxcore-0.2.23 source-linked
host-kernel=Linux 6.12.34 x86_64
host-logical-cpus=12
clock-ticks-per-second=100
```

The run necessarily exercised uncommitted product and harness changes; the hashes identify the
exact executed artifacts. `docs/evidence/2026-08-15-four-route-lab.tsv` is an exact retained copy of
the redacted replicated report.

## Bonding roadmap

The experiment justifies a prototype, not transparent production striping. The next gates are:

1. Define a logical route set authenticated by the already proven stable device identity. Sharing a
   device key across independent test processes is not the production coordinator.
2. Define one immutable object manifest with total size, digest, stripe ranges, route assignment,
   and one completion rule. Four independent Tox file completions must not become four ambiguous
   application objects.
3. Prototype fixed range striping first, then compare adaptive work allocation that gives faster
   routes more ranges without permitting overlap, omission, or destination clobber.
4. Inject lane pause, disconnect, cancellation, duplicate completion, reordered completion, and
   process restart. Reassembly must verify the complete object before atomic publication.
5. Repeat randomized/cooldown 1x/2x/4x trials across two hosts, larger objects, direct UDP and
   TCP-relay-only routes. Cross-client interoperability is explicitly outside this repository's
   current scope.
6. Measure resident memory, per-route socket/queue pressure, p50/p95 completion, power, disk versus
   tmpfs, and c-toxcore congestion/send-queue state before selecting a default lane count.
7. Keep bonding below the M7 signed-object/OTA manifest. Arrival over any number of routes grants no
   authority to install, execute, or mutate a device.

Until those gates pass, `tools/run-four-route-lab.sh` remains a laboratory and IoTox continues to
offer ordinary files over one selected Tox connection.
