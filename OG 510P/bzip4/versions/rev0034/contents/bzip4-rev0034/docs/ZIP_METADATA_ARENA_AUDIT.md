# ZIP central metadata arena audit — rev0030

## Motivation

The streamed parser had already removed whole-central-directory
materialization, but each accepted entry still owned a separate `std::string`
and six independent ZIP64 booleans. That representation multiplied allocator
state and left descriptor density unmeasured.

## Refactor

rev0030 appends every central name to one bounded `std::vector<char>`. Each
entry stores a name offset and 16-bit length plus the numeric fields required by
the later local-header pass. ZIP64 state is one byte. The descriptor is
trivially copyable and guarded with `static_assert(sizeof(CentralEntry) <= 64)`.

No long-lived `string_view` crosses an arena resize. Views are reconstructed from
entry indexes only after the relevant append, and issue creation copies the
name immediately. Duplicate sorting stores indexes rather than views or name
copies.

Scratch scopes are explicit: central-extra capacity is released before
name-order allocation; name-order capacity is released before local span/name/
extra buffers. A fixed-header feasibility check rejects impossible EOCD counts
before entry-vector reserve.

## Telemetry and measurement

Schema v6 added:

- `central_entry_descriptor_bytes`;
- `central_entry_storage_bytes`;
- `central_name_storage_bytes`; and
- `central_parser_peak_retained_bytes`.

The peak is the saturated sum of capacities for the entry vector, name arena,
and currently live tracked scratch vectors. It excludes allocator overhead,
issue strings, method-map nodes, and the EOCD tail.

On the validated 64-bit ABI the former entry layout is 96 bytes and rev0030 is
56 bytes. For the 20,677-entry cohort:

- former-layout equivalent descriptor storage: 1,984,992 bytes;
- rev0030 descriptor storage: 1,157,912 bytes;
- contraction: 827,080 bytes (41.67%);
- actual name bytes: 1,751,547;
- name-arena capacity: 1,838,931; and
- maximum one-archive tracked peak: 581,989 bytes.

These are deterministic object-size and vector-capacity observations. They do
not imply a process-RSS or elapsed-time improvement; paired RSS/timing samples
were noisy and are not promoted.

rev0031 retains the 56-byte entry descriptor and all of these counters. Report
schema v7 appends payload-nomination telemetry without changing the central
arena representation.

## Correctness gates

The ordinary, duplicate-name, empty-name, non-ASCII JSON, aggregate-name-limit,
central-extra, ZIP64, local reconciliation, overlap, and source-change tests all
run through the arena model. ASan/UBSan, ThreadSanitizer, Clang, workspace
poisoning, clean staging, and extracted-package rebuilds are publication gates.
