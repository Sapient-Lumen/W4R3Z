# ZIP central-directory streaming and retention audit — rev0031

The central parser is range-backed and record-at-a-time. A permitted central
directory is a CPU and structural budget, not a request to allocate the entire
region.

## Streamed record path

For each declared record the parser:

1. reads the fixed 46-byte header;
2. proves that name, extra, and comment lengths fit the remaining directory;
3. appends the name directly to one bounded arena;
4. reads only the current extra area into one reusable buffer;
5. validates the complete TLV stream and resolves conditional ZIP64 fields;
6. skips the comment without retaining it; and
7. advances exactly to the next central record.

Before any entry vector reserve, the parser proves that the declared entry count
can fit at least that many fixed headers in the declared central byte count.
This converts an implicit later parse failure into an early structural and
allocation bound.

## Compact retained entry model

The former entry carried an owning `std::string` and six separate ZIP64 boolean
members. rev0030 stores all names in one `std::vector<char>` and retains an
offset, a 16-bit length, numeric central metadata, and one ZIP64 state byte. The
entry is trivially copyable and statically guarded at no more than 64 bytes.

On the validated 64-bit ABI:

- former descriptor: 96 bytes;
- rev0030 descriptor: 56 bytes;
- contraction: 40 bytes per entry, or 41.67%.

Across the 20,677-entry cohort, descriptor capacity is 1,157,912 bytes versus a
former-layout equivalent of 1,984,992 bytes. The 827,080-byte difference is a
layout/capacity measurement; it is not an RSS claim.

A bounded 1 MiB eager name reserve is derived from the directory's variable-byte
upper bound. It avoids geometric growth for common cubes without allowing an
extra/comment-heavy hostile directory to force a speculative allocation near
the full central-byte limit.

## Scratch lifetime and telemetry

Central-extra scratch ends with the central stream. Duplicate detection then
sorts a vector of entry indexes; that vector ends before local-record auditing.
The local pass reuses one name buffer and one extra buffer and stores only a
24-byte `{start,end,payload_delta,entry_index}` span. rev0031 replaces the
former native-width entry index with two 32-bit fields: the configured entry
bound already fits the index, while the local-header prefix is at most the
fixed header plus two 16-bit lengths. This exposes validated payload starts to
the optional nomination probe without adding another per-entry vector.

Schema v7 reports descriptor width, final entry capacity, final name capacity,
and the peak sum of explicitly tracked core vectors. Issue strings, allocator
metadata, the method map, and the EOCD search tail are excluded by definition.

The cohort has 1,751,547 actual name bytes and 1,838,931 retained name-capacity
bytes. Aggregate peak-core telemetry is 3,497,235 bytes; the maximum per archive
is 581,989 bytes. Timing and RSS were noisy and are not promoted.

## Preserved behavior

The refactor preserves byte-safe JSON escaping, capped diagnostics, duplicate
name semantics, local/central reconciliation, ZIP64 resolution, descriptor
checks, path and member-type policy, and the maximum-end overlap sweep.
