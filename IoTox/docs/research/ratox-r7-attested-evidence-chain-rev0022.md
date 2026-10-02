# Ratox R7 attested evidence chain — rev0022

Date: 2026-08-17
Status: constructed and deterministically validated; no two-physical-host qualification claim

## Research question

How can IoTox move from a strict parser of asserted R7 durations to a reproducible, tamper-evident
chain that retains raw same-clock timestamps, exact Ratox host joins, balanced trial order, auxiliary
provenance, and explicit agreement from both capture roles?

## Source review

Primary references rechecked:

```text
https://doc.libsodium.org/public-key_cryptography/public-key_signatures
https://docs.kernel.org/admin-guide/sysctl/kernel.html#random
https://www.rfc-editor.org/info/rfc7679/
https://docs.python.org/3/library/os.html
```

Applied interpretation:

- detached Ed25519 signatures can bind an exact canonical payload without duplicating the payload;
- a Linux boot ID is stable for one running kernel and is useful as a scoped capture coordinate, but
  it is not hardware identity or measured-boot attestation;
- cross-host one-way timing depends on clock behavior, so the R7 gate should derive only same-clock
  intervals unless a separately qualified synchronization method exists;
- evidence readers should operate on bounded descriptors, reject symlinks and non-regular inputs, and
  detect mutation during a read; outputs should be exclusive and fsynced.

The sources define cryptographic, kernel, measurement, and file-API behavior. They do not audit IoTox
or validate any physical experiment.

## Construction

### Reconstructable balanced schedule

`tools/ratox_r7_evidence.py` creates a deterministic two-route by six-load schedule. A domain-separated
derivation binds the SHA-256 counter stream to both the run ID and seed; unbiased rejection sampling
then drives Fisher-Yates. Each twelve-trial block contains every cell once, avoiding long accidental
runs of one route or load while retaining randomized order. The run ID, seed, ordinal, route, and load
derive a unique SHA-256 trial token.

### Raw timestamp derivation

The v2 measurement row retains three controller and three host timestamps. The analyzer derives four
same-clock intervals and rejects reversal across a sample or across the run. It never subtracts, adds,
or orders values across controller and host clocks. Reports expose p50/p95/p99 for each same-clock
stage independently. This replaces v1's asserted end-to-end and stage-duration columns.

### Exact host joins without terminal content

`RatoxServiceEvent` now carries message ID, sequence, next sequence, and byte count. INPUT admission
and whole-frame commit events therefore join to one exact protocol frame. OUTPUT append events identify
one exact produced span. The runtime journal projects only coordinates and lifecycle metadata; tests
continue to assert the absence of terminal input/output, argv, environment, and other content.

### Canonical digests and two-party signatures

The unsigned bundle binds canonical schedule and sample digests plus exact sizes and digests of
retained route and bulk evidence. The two auxiliary artifacts must be different files with different
content. Two distinct ephemeral Ed25519 keys sign role-separated payloads containing the
same complete metadata. The signing command also checks the role's local Linux boot ID and verifies
that the secret key derives the advertised public key. Seal and analysis independently verify both
signatures.

The design calls these capture attestations, not remote attestation. A coordinated or compromised
pair can still sign false measurements. The value is precise tamper evidence and explicit agreement
over one reproducible bundle.

### Fail-closed limits

The v2 tool preserves strict ASCII, canonical integer, metadata, line, row, and total-byte bounds.
Schedule rows, measurement rows, and final samples must be exact. Inputs use no-follow regular-file
reads with before/after identity checks. Secret keys must be 64-byte owner-only regular files.
Auxiliary evidence must be nonempty, distinct, and bounded. Outputs are exclusive 0600 files and both
the file and containing directory are fsynced.

## Findings

1. A signed duration is still an asserted duration. Retaining raw same-clock endpoints lets the
   analyzer re-derive every gate input.
2. A global sample ordinal does not join host lifecycle evidence. Exact session, message, byte-span,
   and event-ordinal coordinates close that local join without copying terminal content.
3. Randomized metadata is insufficient. Reconstructing a balanced schedule makes route/load order
   independently checkable.
4. A digest of the result file alone permits substitution of route and load observations. Their exact
   bytes must be bound and supplied again at analysis time.
5. “Provenance complete,” “physical-host-count=2,” and “route verified” overstate what software can
   establish. Metadata now records two capture roles and distinct kernel boots while explicitly
   requiring external review of physical topology, route topology, and load semantics.
6. A signature key name does not prove the right key or machine performed signing. The signer derives
   the public key from the secret and checks the local running-kernel boot ID before signing.
7. Per-sample event order is not enough. Host events and host timestamps must also progress globally,
   preventing a reordered but individually valid sample sequence.
8. Adding locally derived stage durations and comparing that sum to a controller interval silently
   recreates a cross-clock assumption. v2 validates and reports each clock domain independently.

## Validation boundary

The embedded self-test constructs 12,000 measurements, reconstructs the schedule, generates two
deterministic test keypairs, signs role-specific payloads, seals the evidence, and produces identical
reports twice. Negative cases reject edited sample rows, invalid signatures, globally reordered host
events, changed route evidence, one file reused for both evidence roles, and symlink evidence paths.

Owned C++ checks verify the exact input admission/commit coordinates and content-free runtime journal
projection. The final rev0022 report records the compiler build, standalone process tests, and a
complete deterministic sharded traversal of the 293-check owned registry.

No physical R7 pass is claimed. The tools do not prove packet route, load truth, clock calibration,
binary integrity, physical host count, or uncompromised operators. Those are retained-procedure and
independent-review obligations.
