# Peak-resource kernel accounting — applied review for rev0036

Date: 2026-08-19
Scope: Linux cgroup-v2 lifetime peak interfaces, CPU accounting tuple availability, bounded parsing,
and IoTox teardown-time projection.

## Primary sources reviewed online

1. Linux kernel documentation, **Control Group v2**

   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. Linux kernel source documentation, **Control Group v2**

   https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/cgroup-v2.rst

The sources define kernel interfaces and semantics. They do not audit IoTox, certify the construction
host, or establish production readiness.

## Applied findings

### Peak interfaces are lifetime high-water marks

The cgroup-v2 documentation defines `pids.peak` as the maximum number of processes present in a cgroup
and its descendants, `memory.peak` as the maximum recorded memory usage, and `memory.swap.peak` as the
maximum recorded swap usage. These are high-water marks for a cgroup lifetime, not cumulative event
counts or rolling samples.

Applied construction:

- IoTox attempts to open all three files through protected read-only descriptors before attachment.
- Each interface is independently optional because kernel age, controller availability, and swap
  configuration differ.
- A fresh empty leaf must report canonical zero through every available peak descriptor.
- The descriptor is read again only after recursive quiescence and before exact leaf removal.
- The final optional value therefore represents one exact session leaf lifetime when available.

### Peak values use one-value record grammar

The documented files expose one integer value rather than flat key/value or nested-key records.
`memory.peak` and `memory.swap.peak` can be reset by writing, but ordinary reads return the recorded
high-water mark.

Applied construction:

- rev0036 adds a dedicated parser bounded to 64 bytes.
- It accepts exactly canonical unsigned decimal plus LF.
- It rejects signs, spaces, extra lines, leading zeroes, overflow, truncation, and oversized input.
- IoTox never writes the peak files and does not reset their evidence.

### CPU work accounting does not require configured bandwidth policy

The cgroup-v2 documentation states that `cpu.stat` exists whether or not the CPU controller is enabled.
It always reports `usage_usec`, `user_usec`, and `system_usec`. With the controller enabled it also
reports bandwidth statistics: `nr_periods`, `nr_throttled`, and `throttled_usec`; kernels supporting
CPU burst accounting additionally report `nr_bursts` and `burst_usec`.

Applied construction:

- IoTox now attempts to open `cpu.stat` for every session.
- A configured IoTox CPU quota still requires the interface; an unlimited session records it when
  available without turning absence into a confinement failure.
- The parser requires the complete work tuple.
- Bandwidth and burst data are nested optional all-or-none tuples; partial or detached tuples fail
  closed.
- The one-shot outcome has explicit work, bandwidth, and burst capability flags so observed zero and
  unavailable remain different states.

### Kernel-reported fields stay source values

The kernel exports usage, user, and system fields separately. The documentation does not require an
IoTox consumer to reconstruct one field from the others or use them as a quota decision.

Applied construction:

- rev0036 retains all three values exactly as parsed.
- Aggregation uses independent saturation-safe totals.
- No residual is invented if user plus system differs from usage because of accounting details or
  observation granularity.
- Bandwidth period/throttle and burst counters are aggregated only when their complete tuples were
  observed.

### Capability needs explicit aggregate cardinality

A zero peak, zero throttle count, or zero burst count is meaningful only when the corresponding
interface or tuple was observed. Aggregate totals alone cannot distinguish an unsupported host from
sessions that genuinely measured zero.

Applied construction:

- Each peak publishes observed-session count, saturated sum, and maximum.
- CPU publishes observed work-tuple, bandwidth-tuple, and burst-tuple session counts.
- Counts follow tuple nesting; burst evidence is accepted only within bandwidth evidence, and
  bandwidth evidence only within a parsed CPU work record.
- Owner-private status carries no session, profile, process, command, peer, path, device, or terminal
  labels.

## Implementation boundary

rev0036 implements:

- independently optional protected `pids.peak`, `memory.peak`, and `memory.swap.peak` descriptors;
- strict bounded canonical single-value parsing and zero fresh-leaf validation;
- post-quiescence, pre-removal one-shot peak capture;
- quota-independent optional `cpu.stat` observation;
- mandatory CPU work plus optional complete bandwidth and burst tuples;
- explicit per-session and aggregate capability counts;
- saturation-safe peak sums/maxima and CPU work/bandwidth/burst totals;
- owner-private runtime status projection;
- unit, fuzz, saturation, projection, and live no-quota CPU/available-peak oracle coverage.

rev0036 does not implement:

- live resource sampling, histories, rates, percentiles, alerts, or adaptive policy;
- peak reset, process attribution, working-set analysis, CPU-capacity inference, or simultaneous-demand
  estimation;
- aggregate memory/I/O admission derived from outcomes;
- privileged-writer exclusion, namespace/container isolation, fleet qualification, or production
  activation.

## Construction-host evidence

The direct registry exercises canonical and malformed peak records, CPU tuple compatibility and
rejection, optional-capability semantics, one-shot aggregation, saturation, and runtime projection.
The lifecycle private-cgroup route on the construction host proves that an unlimited session retains
nonzero CPU work without an IoTox CPU quota and compares each available final peak file against the
exact post-removal outcome. Controller-specific positive memory, CPU-bandwidth, and I/O routes remain
named skips where the host lacks writable preactivated controller delegation; no synthetic pass is
claimed for those environments.
