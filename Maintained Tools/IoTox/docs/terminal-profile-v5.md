# IoTox local terminal profile v5

> Historical compatibility format. The encoder now emits `iotox-terminal-profile-v7`; canonical v5
> records remain accepted with no account identity, privilege escalation, or payload byte pins. See
> `terminal-profile-v7.md` for the current payload-integrity boundary.

Status: introduced in rev0034 and canonical in rev0035; adds exact-device cgroup-v2 I/O ceilings and teardown-time I/O
accounting to the profile-scoped resource envelope
Wire effect: none; terminal profiles are owner-controlled local policy and are never selected or
modified by remote Ratox bytes
Superseded by: terminal profile v7; v5 remains the source of the unchanged I/O contract

## Purpose

A terminal profile freezes every local process-selection input for one authorized Ratox OPEN:
executable, arguments, working directory, environment, terminal type, window policy, payload
identity, rlimits, profile-scoped cgroup policy, shutdown timing, and kernel-confinement tier. A
remote peer may request only a preconfigured binding from stable principal to profile. It cannot
supply a path, argv element, environment value, uid/gid, resource ceiling, block device, or
confinement setting.

Profile v5 extends the local cgroup policy with one exact Linux block-device identity and four
independent ceilings:

- read bytes per second (`rbps`);
- write bytes per second (`wbps`);
- read operations per second (`riops`);
- write operations per second (`wiops`).

The device is the canonical numeric `MAJOR:MINOR` tuple consumed by cgroup v2 `io.max`, not a path,
symlink, filesystem label, mount name, or remotely supplied identifier. It is deployment-local and
must be requalified whenever storage topology or numeric device assignment changes.

## Store and canonical byte contract

The owner-private no-follow profile tree, ownership/mode/link/type checks, bounded file sizes, and
atomic registry replacement contract are unchanged from v1. See `terminal-profile-v1.md` for the
filesystem layout and binding record.

A v5 profile is an LF-terminated text record with exact field order. Singleton fields may appear
exactly once. Repeated argument and environment fields retain their documented bounds and canonical
sorting rules. Unsigned integers are canonical decimal: no sign, whitespace, or redundant leading
zero. Hexadecimal fields are lowercase and even length. Decoding succeeds only when re-encoding with
the input version reproduces the original bytes exactly.

## Profile record grammar

```text
iotox-terminal-profile-v5
id=<profile-id>
enabled=<0|1>
argument-hex=<hex bytes>                 repeated 1..32 times
working-directory-hex=<hex bytes>
terminal-type=<token>
inherit-environment=<name>               repeated 0..64 times, sorted
environment-hex=<name>:<hex value>       repeated 0..64 times, sorted by name
identity=inherit
    OR
identity=exact:<uid>:<gid>:1
confinement=compatibility|baseline|strict
cgroup-pids-max=none|<u64>
cgroup-memory-high-bytes=none|<u64>
cgroup-memory-max-bytes=none|<u64>
cgroup-swap-max-bytes=none|<u64>
cgroup-cpu-quota-us=none|<u64>
cgroup-cpu-period-us=none|<u64>
cgroup-io-device=none|<canonical-u32>:<canonical-u32>
cgroup-io-rbps=none|<u64>
cgroup-io-wbps=none|<u64>
cgroup-io-riops=none|<u64>
cgroup-io-wiops=none|<u64>
minimum-dimensions=<columns>:<rows>
initial-dimensions=<columns>:<rows>
maximum-dimensions=<columns>:<rows>
allow-resize=<0|1>
limit-cpu-seconds=<u64>
limit-address-space-bytes=<u64>
limit-file-size-bytes=<u64>
limit-open-files=<u64>
limit-processes=<u64>
hangup-grace-ms=<u64>
terminate-grace-ms=<u64>
kill-reap-grace-ms=<u64>
```

Example:

```text
iotox-terminal-profile-v5
id=maintenance-shell
enabled=1
argument-hex=2f62696e2f6563686f
argument-hex=666978656420617267756d656e74
working-directory-hex=2f7661722f6c69622f696f746f782f776f726b
terminal-type=xterm-256color
inherit-environment=LANG
inherit-environment=TZ
environment-hex=ALPHA:6669727374
identity=exact:65534:65534:1
confinement=strict
cgroup-pids-max=8
cgroup-memory-high-bytes=67108864
cgroup-memory-max-bytes=134217728
cgroup-swap-max-bytes=0
cgroup-cpu-quota-us=25000
cgroup-cpu-period-us=100000
cgroup-io-device=8:16
cgroup-io-rbps=8388608
cgroup-io-wbps=4194304
cgroup-io-riops=2048
cgroup-io-wiops=1024
minimum-dimensions=20:5
initial-dimensions=100:30
maximum-dimensions=240:80
allow-resize=1
limit-cpu-seconds=10
limit-address-space-bytes=134217728
limit-file-size-bytes=1048576
limit-open-files=32
limit-processes=0
hangup-grace-ms=20
terminate-grace-ms=40
kill-reap-grace-ms=60
```

All v1 bounds and grammars for profile IDs, argument count and bytes, normalized absolute working
directories, terminal type, environment, identity, dimensions, rlimits, and grace periods remain in
force. The v2 confinement and v3/v4 cgroup rules also remain in force.

`limit-processes` maps to Linux `RLIMIT_NPROC`, which counts tasks for the real UID rather than
descendants of one terminal. It is therefore unsafe as a session limit for `identity-mode=inherit`:
the production PTY factory rejects that combination unless `limit-processes=0`. Use an exact
dedicated payload identity when a per-UID ceiling is intentional, or use `cgroup-maximum-processes`
with an explicit delegated cgroup root for a true per-session `pids.max` boundary. Zero disables the
legacy per-UID limit; the example does so deliberately.

## I/O policy invariants

The five I/O fields form one policy unit.

1. `cgroup-io-device` is present if and only if at least one of the four ceilings is present.
2. `0:0` is invalid. Major and minor values must each fit `uint32_t` and use canonical decimal.
3. Every configured ceiling is in `1..INT64_MAX`. Zero is not an alias for unlimited; absence is
   represented by `none` in the profile and by `max` at the kernel interface.
4. One profile names at most one device. rev0034 deliberately does not encode a device list or path.
5. A profile I/O policy requires the same explicit cgroup-v2 delegation and hardened payload identity
   prerequisites as the existing process, memory, swap, and CPU policy.

The single-device boundary is intentional. It keeps host/profile composition exact and prevents a
profile from turning one administrator-reviewed device envelope into a union across unrelated media.
A future multi-device format would require a new canonical profile version and explicit set
composition rules.

## Compatibility migration

The decoder accepts five exact headers:

```text
iotox-terminal-profile-v1
iotox-terminal-profile-v2
iotox-terminal-profile-v3
iotox-terminal-profile-v4
iotox-terminal-profile-v5
```

Version-specific meanings are preserved:

- v1 has neither confinement nor cgroup fields, maps to `compatibility`, and has an empty profile
  cgroup policy;
- v2 adds confinement but has no profile cgroup policy;
- v3 adds process, hard-memory, swap, and CPU fields, with no `memory.high` or I/O policy;
- v4 adds `memory.high`, with no I/O policy;
- v5 adds the exact device and four rate fields.

Each input is canonicalized against its own historical encoder. Malformed hybrids, reordered fields,
unknown fields, alternate spellings of `none`, and noncanonical device numbers are rejected. The
public encoder emits v7, so re-encoding a valid v1-v5 record is an explicit local migration. A
historical record acquires later-version defaults and no executable byte pins until it is regenerated
from a qualified local executable.

## Host and profile composition

The host CLI envelope remains administrator-owned. A profile may preserve, add, or tighten policy but
may never weaken or redirect it.

For scalar process, memory, and swap maxima, the lower configured value wins. `memory.high` is clamped
beneath the effective hard memory maximum. CPU bandwidth compares exact `quota/period` ratios without
floating point or overflowing cross-products.

I/O composition is defined as follows:

- if neither layer has I/O policy, the effective policy has none;
- if exactly one layer has I/O policy, that complete device/rate policy is inherited;
- if both layers have I/O policy, their device tuples must be identical;
- for the matching device, each of `rbps`, `wbps`, `riops`, and `wiops` independently selects the
  lower configured value, with an absent value inherited from the other layer;
- a device mismatch is `invalid_argument` and keeps host activation offline.

No path resolution, device alias matching, parent/child block-topology inference, or cross-device
union occurs during composition.

## Host CLI parity

The administrator may supply the same host envelope with:

```text
--ratox-cgroup-io-device MAJOR:MINOR
--ratox-cgroup-io-rbps N
--ratox-cgroup-io-wbps N
--ratox-cgroup-io-riops N
--ratox-cgroup-io-wiops N
```

The device and at least one ceiling must be supplied together. The CLI rejects malformed or
noncanonical device tuples, `0:0`, zero ceilings, values above `INT64_MAX`, and any effective cgroup
policy without an explicit `--ratox-cgroup-root`.

Remote Ratox messages have no field that maps to these options or to profile cgroup fields.

## Delegated `io` controller enforcement

The optional cgroup root remains a normalized, no-follow, daemon-owned cgroup-v2 delegation beneath a
single manager. For every distinct `(payload identity, effective policy)` startup probe and every real
session, IoTox:

1. requires `io` in both `cgroup.controllers` and `cgroup.subtree_control` whenever effective I/O
   policy exists;
2. creates and pins one fresh childless non-threaded domain leaf;
3. verifies that the leaf and controller files remain supervisor-owned and payload-unwritable;
4. writes one complete `io.max` line for the exact device, explicitly using `max` for each absent
   ceiling;
5. reads the bounded nested-key record back and compares semantics rather than byte order;
6. requires exactly one retained device line with all four standard keys and values equal to the
   effective policy;
7. opens a protected read-only `io.stat` descriptor and requires all known counters to begin at zero;
8. attaches the blocked helper only after every requested controller has retained its exact policy.

A representative write is:

```text
8:16 rbps=8388608 wbps=max riops=2048 wiops=max
```

Kernel reads may reorder device lines and nested keys. The parser therefore accepts documented
ordering freedom, `max`, and well-formed future numeric or `max` fields. It rejects duplicate device
lines, duplicate keys, missing standard fields, noncanonical spacing or decimal, an unterminated or
oversized record, and zero finite values for the four standard ceilings. IoTox's own fresh leaf is
expected to contain only the requested device policy; an unexpected second device line fails closed
as possible co-writer or stale-policy evidence.

The blocked-helper ordering is unchanged: no payload code runs in a partially configured cgroup.
Startup probes use the production path and must remove their empty leaves before orphan recovery,
PTY-factory activation, or network exposure.

## Teardown-time `io.stat` evidence

For a session with I/O policy, IoTox pins `io.stat` before attachment. The record is read only after
`cgroup.events` proves recursive `populated=0` and before the exact leaf inode is removed.

`io.stat` is parsed as a bounded LF-terminated nested-key record. Device-line and nested-key order are
irrelevant. Every nonempty device line must contain canonical `rbytes`, `wbytes`, `rios`, and `wios`.
`dbytes` and `dios` are accepted only as a complete pair and otherwise both contribute zero for compatibility. Other
future fields are accepted only as unique canonical unsigned integers. Duplicate device identities,
duplicate keys, missing required read/write counters, malformed spacing, overflow, or truncation fail
the observation.

Counters are summed across every device line in the exact session leaf with saturating `uint64_t`
arithmetic:

```text
io_read_bytes
io_write_bytes
io_read_operations
io_write_operations
io_discard_bytes
io_discard_operations
```

The aggregate intentionally has no device label. It answers how much block I/O the completed session
was charged across its entire leaf, while avoiding storage-topology, profile, process, command, path,
peer, and terminal-content retention.

A read or parse failure produces one incomplete outcome and no partial values. It does not prevent
otherwise valid removal of a proved-empty exact leaf. If teardown itself is unproved, no completed
outcome is claimed and existing conservative reservation stranding remains in force. A completed
outcome is returned and recorded at most once.

## Private runtime projection

Owner-private `run/status` adds cumulative saturating fields:

```text
ratox-cgroup-io-read-bytes=<u64>
ratox-cgroup-io-write-bytes=<u64>
ratox-cgroup-io-read-operations=<u64>
ratox-cgroup-io-write-operations=<u64>
ratox-cgroup-io-discard-bytes=<u64>
ratox-cgroup-io-discard-operations=<u64>
```

These totals are updated only from complete one-shot outcomes. `ratox-cgroup-completed-session-
outcomes` and `ratox-cgroup-incomplete-session-outcomes` retain the evidence-quality boundary. No
per-session record, device tuple, path, identity, profile ID, command, peer identifier, terminal byte,
or error string is published.

## Semantics and nonclaims

`io.max` is an absolute BPS/IOPS limit interface. The kernel may permit temporary bursts and delays
I/O only after a configured threshold is reached. The policy is therefore not a deterministic latency
or completion-time guarantee.

Buffered-write attribution also depends on the kernel/filesystem cgroup-writeback contract. Writeback
is attributed through inode ownership, which can move when different cgroups write the same inode;
filesystems without cgroup writeback support may attribute writeback outside the session. Deployments
must qualify the selected filesystem, workload, and device rather than treating the numeric tuple as
self-proving.

rev0034 does not provide:

- automatic discovery or stable naming of block topology;
- multiple-device profile policy;
- aggregate or advance reservation of physical I/O bandwidth;
- latency, queue-depth, weight, cost-model, or proportional-share policy;
- causal attribution of I/O to commands, files, peers, or profiles;
- continuously sampled rates or PSI-adaptive admission;
- protection from a privileged or same-authority competing cgroup writer;
- target-fleet qualification or a production-readiness claim.

The administrator must provide one exclusive delegated subtree, review the numeric device identity,
and rerun the live device oracle on every target topology.

## Qualification surface

The owned registry freezes:

- v1-v4 canonical migration to v5 and v5 byte-exact round trip;
- I/O policy validation, matching-device composition, independent minima, and mismatch refusal;
- CLI parsing and malformed/incomplete policy rejection;
- unordered/future-compatible `io.max` parsing and malformed nested-key refusal;
- empty, multi-device, complete-or-absent discard-pair, future-field, overflow, and saturating `io.stat` parsing;
- one-shot complete/incomplete aggregate outcomes and six runtime projection fields.

A separate capability-aware process route mounts a fresh cgroup-v2 view. When the execution
environment provides an exclusive writable delegation with `io` preactivated, it discovers the real
backing device from a synchronous-write probe, verifies semantic `io.max` retention on that device,
performs synchronous I/O inside the configured session, and requires nonzero write bytes and
operations in the teardown outcome. Missing namespace capability, controller delegation, or
cgroup-attributed filesystem I/O returns named skip code 77 rather than fabricated positive evidence.
