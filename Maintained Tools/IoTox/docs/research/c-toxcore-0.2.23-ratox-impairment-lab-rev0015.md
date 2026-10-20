# c-toxcore 0.2.23 Ratox impairment laboratory — rev0015

Date: 2026-08-15. Status: founding-host controlled-path evidence, not a terminal protocol or
two-host qualification.

## Question

Which c-toxcore carrier behavior matters before IoTox freezes a reconnectable Ratox terminal
protocol? In particular:

- does custom-lossless head-of-line behavior become visible under delay, loss, and bulk;
- does custom-lossy preserve a useful low-latency region;
- where does local transport admission, rather than path loss, become the bottleneck; and
- does forced TCP retain any meaningful lossy-datagram behavior?

## Method

`tools/run-ratox-impairment-lab.sh` creates two disposable network namespaces joined by one private
bridge. Four source-linked c-toxcore agents run in each namespace from the immutable reusable test
identity baseline. Only each namespace's `eth0` egress receives a netem qdisc. The tool never adds a
qdisc to a host or physical interface. One exact private-subnet NAT rule permits public bootstrap
and relay access, and cleanup removes the rule, namespaces, veths, and bridge.

Every run requires all eight route directions to report the requested provider connection: direct
UDP for `udp`, and TCP relay for `tcp`. The carrier order is deterministically permuted. Route zero
collects 24 single probes per carrier/state and one 64-packet burst per custom carrier/state, with
2 ms between burst submissions and a 2.5 second deadline. The bulk state overlaps one exact finite
file transfer. Burst records distinguish:

- `local-rejected`: toxcore did not admit the send;
- `path-missed`: toxcore admitted it but no correlated echo arrived by the deadline;
- arrival-rank inversions among successful replies; and
- additional duplicate replies.

The profiles were applied independently in both directions:

| Profile | Namespace egress netem |
|---|---|
| baseline | limit 1000, deterministic seed |
| delay40 | 40 ms delay, 10 ms normal jitter, limit 1000 |
| adversity | delay40 + 2% random loss + 0.5% duplicate + 5% reorder/50% correlation, limit 256 |
| constrained | delay40 + 1% random loss + 4 Mbit/s rate, limit 64 |

The TCP path necessarily includes a public relay outside the namespaces. Sequential TCP profiles
therefore compare controlled endpoint impairment on top of a changing external path; they do not
claim a fixed relay or an exact causal delta between profiles.

## Bulk burst result

Times are milliseconds. `ok/local/path` partitions all 64 attempted records. `inv` counts pairwise
arrival-rank inversions among replies and is not a percentage.

| Native path | Profile | Carrier | ok/local/path | median | p95 | inv |
|---|---|---|---:|---:|---:|---:|
| UDP | baseline | lossless | 64/0/0 | 6.8 | 11.4 | 0 |
| UDP | baseline | lossy | 64/0/0 | 27.4 | 49.4 | 0 |
| UDP | delay40 | lossless | 39/13/12 | 204.0 | 292.4 | 0 |
| UDP | delay40 | lossy | 35/0/29 | 96.4 | 123.4 | 67 |
| UDP | adversity | lossless | 62/2/0 | 236.9 | 387.1 | 0 |
| UDP | adversity | lossy | 38/0/26 | 85.6 | 113.8 | 78 |
| UDP | constrained | lossless | 57/7/0 | 151.2 | 306.6 | 0 |
| UDP | constrained | lossy | 63/0/1 | 129.2 | 143.9 | 0 |
| TCP | baseline | lossless | 64/0/0 | 320.4 | 390.9 | 0 |
| TCP | baseline | lossy | 64/0/0 | 319.0 | 468.4 | 0 |
| TCP | delay40 | lossless | 64/0/0 | 378.5 | 547.6 | 0 |
| TCP | delay40 | lossy | 64/0/0 | 449.9 | 647.4 | 0 |
| TCP | adversity | lossless | 3/61/0 | 1,206.0 | 1,239.2 | 0 |
| TCP | adversity | lossy | 34/30/0 | 617.7 | 764.8 | 0 |
| TCP | constrained | lossless | 64/0/0 | 265.1 | 371.4 | 0 |
| TCP | constrained | lossy | 64/0/0 | 300.5 | 332.3 | 0 |

No run observed an additional application-level duplicate reply. That does not prove the network
did not duplicate packets: netem counters and configuration prove the profile was active, while
toxcore/TCP can suppress duplicates before the application callback.

## What the result says

The 2 ms burst is beyond a safe interactive operating point once delay and bulk coexist. On UDP,
lossless preserves order and eventually protects admitted records, but it builds hundreds of
milliseconds of tail and can reject local admission. Lossy avoids the reliable prefix stall and
returns survivors faster, but drops and reorders enough that it is suitable only for explicitly
replaceable state with sequence/base information and resynchronization.

The constrained UDP profile is the clearest policy example. Lossless rejected seven sends but lost
none after admission; lossy admitted all 64 and returned 63 at a 129 ms median. The correct response
is not to choose one carrier globally. IoTox needs admission-aware pacing, a sparse reliable control
and input-commitment lane, and an optional lossy lane only for state superseded by a newer complete
state.

Forced TCP erases the wire-level distinction. Both custom APIs arrive in order with zero inversion,
and adversity under bulk turns primarily into local admission collapse: lossless rejected 61/64 and
lossy rejected 30/64. A lossy screen-state encoding cannot defeat TCP head-of-line blocking on a TCP
relay. Latency isolation there requires reducing/coalescing load or evaluating a separately
authenticated Tox route; changing the custom packet API is not route independence.

Normal Tox text remains unsuitable for terminal framing. Its idle receipts retained large,
carrier-specific tails even in baseline runs, while the custom packet probes were much tighter.
Text remains chat/compatibility traffic.

## Transfer and instrumentation integrity

All eight finite-file phases completed exactly with zero dropped IoTox transport events. Measured
bulk throughput ranged from 1,439,116 bytes/s for baseline direct UDP to 108,666 bytes/s for
adversity TCP. The owner interactive queue remained locally prioritized; the failures above occur
at or below toxcore/path admission, not because one IoTox FIFO sat behind the file workload.

The first namespace implementation exposed and repaired two laboratory defects before the retained
run: same-namespace toxcore construction is now serialized through per-lane socket readiness to
avoid UDP port-selection races, and process counters resolve the real post-`setns` daemon rather
than its privileged waiting parent. A second defect caused one rejected burst send to discard every
partial observation; the retained schema returns one record per ordinal and separates admission
from post-admission misses. Earlier exploratory reports are not qualification evidence.

## Exact retained evidence

The complete redacted reports and qdisc counters are under
`docs/evidence/2026-08-15-ratox-impairment/`. The matrix manifest verifies the SHA-256 of all eight
reports and ends in `matrix pass`.

```text
provider=c-toxcore-0.2.23 source-linked
standalone-binary-sha256=e670681a62717da3ed84970c0e8df37f245aa96a4a34fb49740bf8385c537f1d
matrix-manifest-sha256=d8f90131860084b1792beb388e74544878acc94417d2c570990b9914c67c9a40
matrix-run-id=20260815T210104Z-5fc4e
host-kernel=Linux 6.12.34 x86_64
host-physical-qdisc-touched=no
```

The binary hash is also recorded inside the matrix manifest. Report identities are hashes of Tox
public keys only; reusable private identities remain in the ignored private cache.

## Next gate

Freeze terminal framing only after a paced local PTY prototype proves at-most-once input,
generation fencing, bounded replay, explicit gaps, resize, exit, and authority denial. Then repeat
keypress-to-render tests beside the 1/8/16/32/64 stream sweep. Direct UDP may use a replaceable
lossy state lane after snapshot/delta semantics exist. TCP relay must assume one ordered congested
substrate and should trigger dedicated-route evaluation if the latency budget fails.
