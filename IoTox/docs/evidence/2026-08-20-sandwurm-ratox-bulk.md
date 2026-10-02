# Sandwurm Ratox bulk construction evidence — 2026-08-20–21

## Claim

Two concurrent source-linked IoTox guests completed the full 1/8/16/32/64 direct-UDP construction
ladder while a genuine authorized Ratox terminal crossed the same Tox friendship. Every accepted
cell required all named 1 GiB sparse finite-file transfers to be active, 40 exact one-byte
keypress-to-remote-PTY-to-local-render samples, every transfer to advance, and an empty transfer set
after bounded cancellation. No payload bytes enter compact evidence.

This proves the upstream-provider direct-UDP construction boundary, the patched-provider direct-UDP
boundary through the ordinary 32-stream limit, and the patched-provider forced-TCP boundary through
16 streams on this founding host. It does not replace the frozen
1,000-sample release matrix, prove physical-host separation, or decide that an authenticated
dedicated Tox route is unnecessary. The upstream 64-stream result remains historical: its
patched-provider rerun completed all terminal samples but did not advance every bulk lane inside the
global construction bound.

## Accepted observations

```text
streams  compact proof                                      source
1        .sandwurm/exports/pairs/pair.jpzj3v9e              771696e
8        .sandwurm/exports/pairs/pair.gewajlh8              fb31a01
16       .sandwurm/exports/pairs/pair.tmf_6btx              1df78cb
32       .sandwurm/exports/pairs/pair.pgs5oiap              1df78cb
64       .sandwurm/exports/pairs/pair.3urw59bd              d19790e
```

The one-stream cell used binary SHA-256
`aa9092a8735ec8d8a9fe7cc510ea4f336843321fd13f038281aa5b175ad33e04`. The 8–64 cells include the
admission-boundary telemetry repair and used
`96ec8fc81888aeaa646042bec0e476e124795dacd2a183f9cafcd7c7dbeae9d6`.

Nearest-rank controller-clock measurements:

```text
streams  render p50  render p95  render p99/max  owner queue p99/max  >=250 ms
1         16.063 ms   35.443 ms    48.378 ms       0.394 ms             0
8         16.212 ms   33.763 ms    37.682 ms       0.134 ms             0
16        14.143 ms   28.121 ms    47.940 ms       0.061 ms             0
32        14.229 ms   22.318 ms    28.556 ms       0.061 ms             0
64        12.719 ms   23.954 ms    33.903 ms       0.059 ms             0
```

Bulk lifecycle observations:

```text
streams  time after probe to all lanes advanced  position min/max           position total  cancel
1        already advanced at probe end           not retained               11,624,709      clean
8         3.828 s                                 v2 bounds nonauthoritative  6,938,631       clean
16       18.830 s                                 2,742 / 6,875,565         17,440,491      1 round / 0.298 s
32        5.598 s                                 4,113 / 5,958,366         23,075,301      1 round / 0.596 s
64        5.899 s                                 1,371 / 6,339,504         29,576,583      2 rounds / 32.119 s
```

The v2 eight-stream generator compared position extrema lexically. Its active count, progressed
count, wait, and total remain exact; its min/max fields are deliberately not claimed. Schema v3
forces numeric coercion and verifies that total bytes lie within the reported numeric range.

The data does not show interactive owner-queue congestion. Bulk traffic kept c-toxcore hot and all
loaded cells were materially faster than idle direct UDP. The visible constraints are instead:

- ordinary IoTox deliberately defaults to 32 active sends and receives; the 64 cell explicitly used
  `--max-active-sends 64 --max-active-receives 64` without changing that default;
- first-byte service across lanes is variable rather than monotonically proportional to count;
- 64-way cancellation convergence is currently expensive even though admission, transfer progress,
  and terminal latency remain healthy.

## Current-provider direct-UDP rerun

The named `0.2.23+iotox-file-rr1` provider passes the unchanged direct-UDP gate through the ordinary
32-transfer product limit:

```text
streams  compact proof                                      render p50/p95/max       queue max  progress  cancel
1        .sandwurm/exports/pairs/pair.9bnaldle              14.171/19.197/20.228 ms  0.038 ms   0.010 s   0.124 s
8        .sandwurm/exports/pairs/pair.qik3vr38              22.178/38.424/51.655 ms  0.082 ms   0.017 s   0.158 s
16       .sandwurm/exports/pairs/pair._xln0m5u              43.204/65.436/66.703 ms  0.148 ms   0.009 s   0.209 s
32       .sandwurm/exports/pairs/pair.1b2rc7mf              18.657/44.294/48.871 ms  0.278 ms   0.012 s   0.393 s
```

Every accepted cell rendered 40/40 exactly with no 250 ms miss, advanced every lane, and canceled
to an empty provider transfer set in one round. All use binary SHA-256
`6a7a4248d40e9ced2ab5472edc602258de2b6bd97d4be2422ea8077d8278c0a1`, and both receipt and runtime
origin name `iotox-file-rr1`.

The current-provider 64-stream opt-in admitted all 64 transfers and captured all 40 exact terminal
samples, but the all-lanes-progress assertion did not complete before the global deadline. Its
private failed root was inspected and deleted; it is not accepted evidence. An immediate repeat also
reached 64 active transfers but did not complete terminal capture. Because the two failed gates
differ, this does not establish one deterministic 64-stream failure mechanism; it does independently
reject current 64-stream qualification. The harness now emits a separate terminal-captured
rendezvous record and a content-free progress checkpoint whenever the progressed-lane count changes,
so future failures distinguish terminal capture, lane progress, and cancellation without mounting a
private guest disk. The ordinary limit remains 32.

## Forced-TCP observations and provider repair

The accepted forced-TCP compact observations are:

```text
streams  compact proof                                      provider
1        .sandwurm/exports/pairs/pair.mpyslgfi              upstream 0.2.23
8        .sandwurm/exports/pairs/pair.5zxagsvs              upstream 0.2.23
16       .sandwurm/exports/pairs/pair.e_i79q7a              0.2.23+iotox-file-rr1
```

```text
streams  render p50  render p95  render p99/max  owner queue p99/max  progress wait  cancel
1         23.253 ms   33.009 ms    43.501 ms       0.194 ms            0.024 s        0.156 s
8         17.519 ms   26.580 ms    30.512 ms       0.036 ms            0.010 s        0.168 s
16        26.254 ms   41.108 ms    42.596 ms       0.041 ms            0.018 s        0.258 s
```

All three cells rendered 40/40 exactly with no 250 ms miss. The final 16-stream cell used binary
SHA-256 `6a7a4248d40e9ced2ab5472edc602258de2b6bd97d4be2422ea8077d8278c0a1`; its receipt and retained
host status independently bind `c-toxcore 0.2.23+iotox-file-rr1` and
`linked:c-toxcore+iotox-file-rr1`.

The stock provider admitted 16 transfers but advanced only 4 before the outer 240-second completion
bound. Source inspection found that `do_all_filetransfers()` restarted at slot zero whenever the
per-friend crypto send window reopened. The tracked patch adds one zero-initialized per-friend cursor
and resumes after the last chunk-request admission. Its SHA-256 is
`fb4080c26a9e04753681376b721d5ab0570202e4e78a32e17a9f6d18e7e0d2ed`. The unchanged 16-stream gate
then advanced 16/16 lanes.

At 32 streams, the patched sender received all 32 RESUME controls and synchronously admitted chunks
for all 32 files, while the client observed data for only 17 before the same outer completion bound.
Ratox still rendered 40/40 exactly. This diagnostic came from a private failed construction root,
which was deleted rather than misrepresented as accepted compact evidence. It localizes the next
bottleneck after sender repair to reliable data delivery through one TCP crypto/relay path. The
roadmap response is route striping for bulk, not weakening the terminal queue or ordinary
32-transfer resource default. A 64-stream single-route TCP cell is not useful until the 32-stream
delivery boundary is addressed.

## Four-route forced-TCP striping

Four isolated IoTox agents per guest share one stable device principal but use four distinct reusable
Tox savedata identities. All routes are forced TCP through the same pinned bridge relay. Route zero
carries Ratox plus its bulk share; routes one through three carry bulk only. Both guest receipts bind
four distinct peer-key hashes and observed `connection=tcp` rows. An evidence barrier now requires
both guests to snapshot those live routes before either side tears an auxiliary agent down.

The 32-stream cell passed twice, defeating the one-route 17/32 delivery boundary. The current compact
proof is `.sandwurm/exports/pairs/pair.hb491hc_`, source `136d0bc`, binary SHA-256
`6a7a4248d40e9ced2ab5472edc602258de2b6bd97d4be2422ea8077d8278c0a1`:

```text
routes / streams        4 / 32 (8 per route)
active before / after   32 / 32
progressed              32
progress wait           132 ms
position min / max      411,300 / 625,176 bytes
position total          15,577,302 bytes
cancel                  1 round / 1.260 s
Ratox                   40/40 exact; zero >=250 ms
render p50 / p95 / max  47.437 / 72.788 / 137.606 ms
owner queue p50/p95/max  0.018 / 0.301 / 1.070 ms
```

The higher cells are diagnostic failures, not accepted proofs:

- 40 streams (10 per route) completed one full client workload—40/40 exact renders, 118.596 ms
  maximum, 40/40 progressed in 111 ms, and cancel-to-empty in 833 ms—but a teardown race invalidated
  its two-sided route receipt. After the evidence-barrier repair, an identical run again captured the
  terminal and progressed 40/40, but cancellation did not converge inside 60 seconds. Forty is not
  repeatably qualified.
- 48 streams (12 per route) completed 36 exact terminal samples before the durable owner-command
  evidence update missed its five-second bound. Its recorded interactive queue maximum was only
  2.630 ms, localizing the stall outside the priority queue.
- 56 streams (14 per route) returned the first echoed byte but its durable owner-command evidence did
  not become observable inside five seconds.
- 64 streams (16 per route) completed 18 terminal samples; the nineteenth PTY output exceeded five
  seconds and appeared only after controller detach.

All failed private roots were inspected read-only and deleted. A separate current 32-stream attempt
stopped with both guests at three of four confirmed routes before an identical retry passed. Thus
eight streams per route is the repeatable workload point once routes converge. The establishment
recovery gate below closes bounded retry and partial-route refusal; safe reassignment after a live
lane fails remains open. Nothing here proves transparent bonding, aggregate throughput, or
physical-host behavior.

## Four-route establishment recovery

The `ratox-stripe-recovery-32` scenario deliberately stopped only the device's fourth auxiliary
agent after its peer request had been applied, then restarted that exact route from its existing Tox
savedata. Every auxiliary route also had at most two staggered automatic restart opportunities.
Work was withheld until all four distinct routes confirmed over forced TCP; retry exhaustion had no
three-route fallback.

The accepted compact proof is `.sandwurm/exports/pairs/pair.fmf8pynz` (180 KiB). Its binary SHA-256
is `6a7a4248d40e9ced2ab5472edc602258de2b6bd97d4be2422ea8077d8278c0a1`:

```text
routes / streams        4 / 32 (8 per route)
route-process restarts  3 total: 1 injected, 2 automatic
active before / after   32 / 32
progressed              32 in 167 ms
position min / max      312,588 / 600,498 bytes
position total          13,518,060 bytes
cancel                  1 round / 1.754 s
Ratox                   40/40 exact; zero >=250 ms
render p50 / p95 / max  54.822 / 85.788 / 103.412 ms
owner queue p50/p95/max  0.020 / 0.434 / 1.507 ms
end-to-end gate          361.240 s
```

The client recorded one automatic restart. The device recorded its injected restart plus one
automatic restart. This proves identity-preserving establishment recovery under the construction
schedule, not preservation or reassignment of transfers already active when a route process dies.

## Live-loss discovery and protected-route consequence

The live-loss discovery stopped route three only after 32 transfers were active, then required the
client to observe the route offline and its eight transfers absent before Ratox began. The observed
transfer lifecycle was consistent: eight affected transfers were purged, 24 remained active, no
transfer moved routes, and restarting unchanged savedata produced the same confirmed TCP route with
no stale files. One correctly sequenced run completed 40/40 Ratox samples during that offline
interval and recovered the route, but its serialized teardown left six transfers after 45 bounded
control attempts. After teardown was made concurrent across route agents, the next run failed a
Ratox receive's five-second deadline before route recovery was allowed.

These failed roots were inspected read-only and deleted, so there is deliberately no compact proof
to reverify. The result rejects the assumption that queue priority plus an eight-transfer share makes
a route protected. The next acceptance cell is `ratox-stripe-protected-live-loss-24`: route zero has
no bulk work and routes one through three have eight streams each. This reduces aggregate bulk
admission to 24 in exchange for a real interactive failure domain; reclaiming route-zero bulk
capacity is an explicit future scheduling question, not the default.

The first dedicated-route diagnostic delivered all 40 exact samples but had a 506.113 ms maximum,
above the provisional 250 ms miss boundary, and an all-files-at-once cancel batch overloaded each
agent's local control socket. The acceptance configuration therefore also isolates CPU service
(primary agent and probe on vCPU 0, auxiliary agents on vCPU 1) and uses one sequential cancel worker
per route with the three route workers parallel. Schema v5 binds both CPU assignments and rejects any
protected-route sample at or above 250 ms.

That topology still left three transfers after 58 attempts (7 successful replies, 51 errors),
localizing the failure below the CLI/socket fan-out. The frozen cleanup rule now makes per-file
cancel best-effort once, then recycles only route workers that remain non-empty. Same-identity TCP
reconfirmation and empty state are mandatory before readiness; this is explicit worker fencing and
does not reassign a transfer.

The accepted CPU-isolated rerun is `.sandwurm/exports/pairs/pair.0xk33kco` (180 KiB). Its compact
manifest SHA-256 is `e26380574d5d8844a9b1ae18ba749eabe97a8caee48d71869a0f15e450ac787d`:

```text
routes / bulk streams   4 / 24 (route 0 protected; 8 on routes 1-3)
faulted / unaffected    8 / 16
active before / after   24 / 16
progressed              16 in 488 ms
position min / max      63,475,929 / 65,447,427 bytes
position total          1,031,082,486 bytes
reassigned              0
Ratox                   40/40 exact; zero >=250 ms
render p50 / p95 / max  111.045 / 164.825 / 232.356 ms
owner queue maximum     1.844 ms
cleanup controls        16 attempts; 10 accepted; 6 errors
cleanup fallback        1 client bulk-worker restart
route restarts          2 total including fault-route recovery
```

This closes live-loss discovery for the construction policy, not immutable-object reassignment.
The maximum is only 17.644 ms below the provisional miss boundary, so the 1,000-sample and
long-running scheduler gates remain open.

## Reverification

```sh
for cell in \
  1:pair.jpzj3v9e 8:pair.gewajlh8 16:pair.tmf_6btx \
  32:pair.pgs5oiap 64:pair.3urw59bd; do
  streams=${cell%%:*}
  proof=${cell#*:}
  ./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
    ".sandwurm/exports/pairs/$proof" "ratox-bulk-$streams"
done

for cell in 1:pair.mpyslgfi 8:pair.5zxagsvs 16:pair.e_i79q7a; do
  streams=${cell%%:*}
  proof=${cell#*:}
  ./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
    ".sandwurm/exports/pairs/$proof" "ratox-bulk-$streams"
done

./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.hb491hc_ ratox-stripe-32

./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.fmf8pynz ratox-stripe-recovery-32

./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.0xk33kco ratox-stripe-protected-live-loss-24

for cell in \
  1:pair.9bnaldle 8:pair.qik3vr38 16:pair._xln0m5u 32:pair.1b2rc7mf; do
  streams=${cell%%:*}
  proof=${cell#*:}
  ./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
    ".sandwurm/exports/pairs/$proof" "ratox-bulk-$streams"
done
```

Each compact export is 172–180 KiB allocated and contains only the verifier allowlist. Private guest
disks, reusable identities, bootstrap keys, RecallRoot material, runtime journals, and bulk payloads
were removed after export.
