# ZIP payload nomination and exact-verification audit — rev0031

## Purpose

The datacube roadmap called for a generic shallow classifier that could nominate
regions for future deduplication without making a bespoke semantic parser or
silently authorizing a format change. rev0031 implements the first conservative
lane: repeated ZIP member payloads that can be proven identical without
extracting members.

The result is measurement infrastructure, not a deduplicating container. It
answers two separate questions:

1. Which nonempty, unencrypted entries share the same central CRC-32 and
   uncompressed size and are therefore worth nominating for deeper work?
2. Which nominated entries also have the same compression method, compressed
   size, SHA-256 digest, and exact compressed bytes?

The first result is explicitly unverified. The second is an exact lower bound on
repeated compressed payload bytes already present in the container.

## Admission order

The probe runs only when explicitly enabled and only after the ordinary
preflight has completed all of the following:

- classic/ZIP64 end-record resolution;
- central-directory and extra-field framing;
- local/central reconciliation;
- data-descriptor validation;
- member-type and path policy;
- payload-range bounds;
- central-directory overlap checks; and
- the maximum-end local-record overlap sweep.

A structurally invalid archive is never passed to the nomination stage. All
reads remain positional reads from the descriptor-pinned source, and the final
source-fingerprint check covers the probe as well.

## Two-level classifier

### Content nomination

Entries are first grouped by `(uncompressed_size, crc32)`. This is cheap and
useful as a nomination signal, but it is not identity proof: CRC-32 collisions
exist, and central metadata is not recomputed by this non-extracting tool.

Empty logical members are excluded. They are common enough to create noisy
clusters while usually offering less compressed repetition than any practical
reference record would cost.

### Exact compressed-payload proof

Inside a content nomination, entries are considered exact-payload candidates
only when their compression method and compressed size also agree. Each
candidate payload is then:

1. read incrementally through one bounded buffer;
2. hashed with SHA-256;
3. grouped by digest; and
4. compared byte for byte against its digest-group representative through two
   bounded buffers.

SHA-256 is a screening key, not the final authority. An equal digest that fails
the exact comparison produces a nonfatal `payload_digest_collision` issue and
is not counted as verified identity.

Identical compressed payload bytes can be safely represented as a conservative
container-level repetition lower bound because a future reference layer could
restore the original payload bytes exactly. rev0031 does not implement that
layer and does not deduct reference metadata, index, alignment, or decoder-state
costs.

## Bounded work and memory

The probe is off by default. `ZipLimits` exposes:

- `max_payload_probe_read_bytes`;
- `max_payload_probe_group_entries`;
- `payload_probe_chunk_bytes`; and
- `min_payload_probe_bytes`.

A group is admitted atomically against the conservative worst-case read cost

`(3 * entries - 2) * compressed_size`.

That covers one hash read of every member and one exact two-range comparison of
every member after the representative. A group that cannot fit is skipped in
full; no partially processed group is reported as verified. Larger logical
nominations are considered first so a finite budget preferentially measures the
largest potential wins.

The existing local interval record is refactored from
`{start, end, size_t entry_index}` to
`{start, end, uint32 payload_delta, uint32 entry_index}`. It remains 24 bytes on
the validated ABI while making the already-validated payload start available to
the probe. No extra per-entry payload-offset vector is retained.

Incremental probe scratch consists of at most two chunk buffers and one digest
record vector for the current candidate group. Schema v7 reports the peak
capacity of those incremental vectors separately from central-parser retention.

## Representative evidence

Across the 18 regular-datacube archives:

- 20,677 entries and 93,061,110 compressed bytes passed structural preflight;
- 238 CRC/size nomination groups contained 678 entries;
- every one of those 238 same-representation groups was hashed and exactly
  verified;
- 440 entries beyond one representative per group account for 1,718,627 gross
  repeated compressed bytes;
- the same groups describe 4,935,579 gross repeated logical bytes;
- 6,692,344 payload bytes were read across hashing and exact comparison;
- no group hit the read or entry limit;
- no digest collision was observed; and
- maximum incremental probe scratch capacity was 131,144 bytes.

The gross repeated compressed bytes are 1.846773% of the cohort's compressed
member bytes. This is a useful lower-bound signal, but not enough on its own to
justify a new reference format: metadata and implementation costs still need a
complete final-container oracle.

## Report and tool surface

`bzip4_cube_preflight --probe-payload-duplicates ARCHIVE.zip` enables the probe.
Schema `bzip4.zip-preflight.v7` adds nomination, hashing, verification, skipped-
group, read-budget, collision, and scratch-capacity counters. Ordinary calls
remain metadata-only and report all probe counters as zero.

## Nonclaims

rev0031 does not decompress members, verify their CRCs, detect equal content
that was compressed into different byte representations, build references,
change BZ3v1 bytes, or claim final compression-ratio improvement. It establishes
a bounded and exact first classifier lane that future ratio experiments can use
without confusing a metadata hint, cryptographic digest, or specimen-specific
name with proof.
