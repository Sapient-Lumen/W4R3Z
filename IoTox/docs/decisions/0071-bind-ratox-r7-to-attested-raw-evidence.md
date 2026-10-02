# ADR 0071: Bind Ratox R7 to an attested raw-evidence chain

Status: accepted
Date: 2026-08-17

## Context

ADR 0070 made malformed and incomplete R7 matrices fail closed, but its v1 input still trusted
operator-supplied durations and physical-run metadata. A syntactically valid file could claim two
hosts, randomized order, route verification, or local stage durations without retaining the schedule,
the raw same-clock timestamps, the exact Ratox byte/event coordinates, or agreement from both capture
hosts. The analyzer could validate shape but could not detect later row edits or substitution of the
route and bulk-load observations.

The complete-service experiment needs a construction that narrows that gap without pretending that a
software signature is remote attestation or that a digest proves the semantic truth of an arbitrary
capture file.

Primary references rechecked for this decision:

```text
https://doc.libsodium.org/public-key_cryptography/public-key_signatures
https://docs.kernel.org/admin-guide/sysctl/kernel.html#random
https://www.rfc-editor.org/info/rfc7679/
https://docs.python.org/3/library/os.html
```

The libsodium reference defines detached public-key signatures. Linux documents `boot_id` as a UUID
created on first retrieval and unchanged for that running kernel. RFC 7679 reinforces that one-way
measurements depend on clock properties; this design therefore derives only same-clock intervals and
never subtracts a host timestamp from a controller timestamp. Python's descriptor APIs supply the
regular-file, no-follow, close-on-exec, exclusive-create, stat, and fsync primitives used by the
construction tool.

## Decision

### Evidence schema v2 is the only qualifying schema

`iotox-ratox-r7-samples-v1` remains historical. A new qualification run must use
`iotox-ratox-r7-samples-v2`, produced and verified by `tools/ratox_r7_evidence.py` through the stable
entry points `tools/prepare-ratox-r7.py` and `tools/analyze-ratox-r7.py`.

The v2 bundle retains canonical raw timestamps from two independent steady clocks:

- controller input admission, output receipt, and render completion;
- host input receipt, whole-frame PTY commit, and PTY-output append.

The analyzer derives controller end-to-end, host receive-to-commit, host commit-to-output, and
controller output-to-render durations. It rejects local timestamp reversal and never subtracts,
adds, or orders values across the controller and host clock domains. Owner queue wait remains an exact
single-clock duration recorded at the gate and is not used to construct a cross-host stage sum.

### Trial order is reconstructed, not asserted

Every run has a 128-bit run ID, a 256-bit public schedule seed, and an exact sample count per cell. A
domain-separated SHA-256 derivation binds the counter stream to both run ID and seed before
rejection-sampled Fisher-Yates permutations. Each contiguous twelve-run
block contains every combination of the two required routes and six required bulk-stream counts
exactly once. Each trial has a run-bound SHA-256 token. The analyzer reconstructs every ordinal,
route, load cell, and token from the run ID and seed and rejects any deviation.

The schedule is balanced randomization, not a secrecy mechanism. Publishing the seed after scheduling
is expected.

### Host lifecycle records carry exact content-free joins

Ratox service events now retain these event-specific coordinates:

```text
message-id
sequence
next-sequence
event-bytes
```

An admitted INPUT and its later whole-frame PTY commit carry the same protocol message ID and exact
input byte span. An OUTPUT append carries the exact produced output span. The private runtime journal
continues to omit terminal bytes, argv, environment, paths, profile contents, and error payloads.

A qualifying sample requires one exact input byte, a nonempty output span, strictly ordered and never
reused host event ordinals, never reused input message IDs, and nonoverlapping per-session input and
output spans. Controller timestamps, host timestamps, and host event ordinals may not move backward
across the run.

### The complete unsigned bundle is digest-bound

Canonical sizes and SHA-256 values bind:

- the reconstructed schedule bytes;
- every canonical sample row;
- one retained route-observation file;
- one retained bulk-load-observation file.

The qualification command requires the two external observation files again and recomputes their
sizes and digests. The route and bulk artifacts must be different regular files with different byte
content. Empty files, symlinks, non-regular files, oversized files, unstable file identity, or
size/digest substitution fail closed. The analyzer does not claim to understand every possible packet-capture,
network-namespace, process, or load-generator format; human review must still establish that those
bound files support the stated route and load facts.

Metadata says `provenance-artifacts-bound=1`, `capture-role-count=2`, and
`distinct-kernel-boots=1`. It labels physical topology, route topology, and bulk-load semantics as
`external-review-required`. It deliberately does not say that two physical hosts, a particular route,
or a truthful load were cryptographically proved.

### Both capture hosts attest the same canonical run

Each run uses two distinct ephemeral Ed25519 capture keypairs. Controller and host capture roles sign distinct,
domain-separated payloads containing the same complete unsigned metadata, schedule digest, sample
digest, external-evidence digests, source commit, both capture public keys, and both boot IDs.

The signing command:

1. parses and canonically reconstructs the attestation payload;
2. reads the local Linux kernel boot ID and requires it to match the role's bound boot ID;
3. derives the public key from the owner-only 64-byte secret key and requires it to match the bound
   capture key;
4. creates a detached libsodium signature and wipes mutable secret buffers on a best-effort basis.

The sealing command verifies both signatures before publishing final evidence, and the analyzer
verifies them again.

These are capture-agreement signatures. They prove possession of the two ephemeral private keys over
one exact bundle. They are not stable IoTox device identity, TPM-backed attestation, proof that two
physical machines existed, proof that a boot ID was not copied into a dishonest payload, or proof that
the signed measurements were generated by unmodified software.

### File parsing and publication remain bounded and fail closed

Inputs are ASCII, newline-terminated, canonical, size bounded, line bounded, field bounded, and opened
as regular no-follow descriptors where the platform supplies `O_NOFOLLOW`. Reads compare device,
inode, size, mtime, and ctime before and after consumption. Outputs are exclusive owner-only files,
fully written, file-fsynced, and parent-directory-fsynced; a failed write removes the partial output.
Secret key files must be regular,
exactly 64 bytes, and inaccessible to group and other users.

## Consequences

A v2 PASS now means considerably more than a v1 PASS: the matrix order is reproducible; durations are
re-derived from same-clock timestamps; sample rows and auxiliary provenance are tamper evident; exact
Ratox host event/span joins are present; and both ephemeral capture roles agreed to the same canonical
bundle from distinct running-kernel identifiers.

A v2 PASS still does not prove the physical setup, route interpretation, load-generator correctness,
clock quality, binary provenance, or absence of coordinated fabrication. Those remain reviewable
experiment facts. IoTox must not claim physical R7 qualification until the two-host run and its bound
raw artifacts are retained and independently examined.

The v2 self-test constructs a complete 12,000-sample matrix, signs and seals it, verifies deterministic
same-clock decomposition reports, proves that host-local durations are not compared to controller
durations, and rejects row tampering, invalid signatures, out-of-order host events, changed or aliased
auxiliary evidence, and symlink substitution.

## Rejected alternatives

- **Keep v1 and add optional signatures.** Signing asserted durations preserves their ambiguity and
  allows qualifying runs with no schedule or exact event joins.
- **Synchronize clocks and subtract host time from controller time.** That adds an avoidable clock
  synchronization dependency. The required gates can be expressed as same-clock intervals.
- **Use one signing key.** One assembler signature does not retain explicit agreement from both capture
  roles.
- **Reuse stable IoTox identity keys.** Qualification capture keys are narrowly scoped and must not
  enlarge the authority or recovery consequences of stable device identity.
- **Call detached signatures remote attestation.** Ordinary software keys and boot IDs do not establish
  measured boot, hardware identity, or uncompromised execution.
- **Parse every route and load artifact format.** That would create an unbounded provider-specific
  surface. The tool binds exact nonempty files; the experiment report states how reviewers interpret
  them.
