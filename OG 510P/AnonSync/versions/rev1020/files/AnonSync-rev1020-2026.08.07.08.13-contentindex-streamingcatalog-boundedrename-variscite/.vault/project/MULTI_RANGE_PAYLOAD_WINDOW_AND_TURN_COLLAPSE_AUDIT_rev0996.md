# Multi-range payload window and transfer-turn collapse audit — rev0996

## Product reason

AnonSync's first supported workload is a Linux/headless media tree measured in
terabytes. Rev0994 made shifted-byte reuse possible and rev0995 removed one
source-side per-range index rebuild, but the wire path still returned exactly
one bounded payload range per authenticated request/response turn.

At the exact 4 TiB payload frontier and the ordinary 4 MiB range ceiling, that
shape requires 1,048,576 serialized turns. Even when the source manifest, source
index, receiver manifest, and predecessor index are hot, round-trip scheduling
remains multiplied by one million.

## Retained protocol change

Reconciliation protocol generation 7 permits one large payload operation to
carry several canonical range records in one response. The response remains
bounded by the existing independent frontiers:

- at most 128 payload records;
- at most 4 MiB in one record;
- at most 64 MiB of payload bytes in one page;
- at most one ranged payload identity and one ranged final operation; and
- at most one complete 8,192-record content-defined manifest.

For the default limits, one full response can carry sixteen 4 MiB ranges. The
exact 4 TiB arithmetic therefore becomes:

- old one-range turns: 1,048,576;
- ranges per default 64 MiB window: 16;
- bounded-window turns: 65,536; and
- serialized request/response turns avoided: 983,040.

This is exact limit arithmetic, not a measured 4 TiB transfer result.

## Canonical grouped authority

Payload records remain sorted by `(content_sha256, offset_bytes)`. Every ranged
group must have:

- one exact total size;
- strictly increasing, gap-free, non-overlapping offsets;
- one exact content-defined manifest digest;
- the complete manifest only on the first cache-cold record;
- constant-size references on later records;
- exact containing-chunk offset and size for every record; and
- a continuation equal to the final record's exact end.

The generic response validator carries only scalar group state. It does not
retain a copied pointer vector for every range. Complete-manifest validation is
performed once, and every later record is checked against that retained bounded
manifest authority.

Generation 7 advances both structural frame domains and semantic body-digest
domains. A generation-6 peer cannot silently interpret grouped-range semantics
as the previous one-range contract.

## Source work and memory boundary

The source opens one exact payload descriptor and obtains or reuses one cohesive
content-defined manifest/index cache. One cumulative-index lookup identifies the
first containing chunk for the requested offset. The bounded response loop then
advances linearly through that retained index while enforcing all three limits
for each copy:

- remaining bytes in the containing content-defined chunk;
- remaining bytes in the 64 MiB page budget; and
- the 4 MiB single-record ceiling.

The complete manifest is copied only into the first cache-cold record. Later
records carry its digest and exact chunk extent. A stale receiver manifest
reference still fails before index lookup and payload copy.

The source may now actually retain up to the configured page byte frontier in
one response. That is a deliberate bounded trade: it collapses turns but does
not claim minimum peak RSS. Encoding and TLS framing may hold additional copies
of the page. The next memory-oriented delta slice should measure and then remove
avoidable whole-window copies, or introduce streaming frame publication, before
raising the byte frontier.

Session accounting separates grouped windows, individual range records, and
payload bytes. Those counters cross the authenticated TLS serve result and the
shipping source JSON surface. A lower request count can therefore be audited
against the exact record and byte work that produced it rather than inferred
from continuation state.

## Receiver ordering and restart

The receiver indexes the already validated response as contiguous spans into the
original payload vector. It does not allocate one pointer vector per digest.
Ranges are consumed in exact order.

After each record, the existing durable contiguous-prefix owner remains the only
partial-byte authority. Local predecessor reuse may advance that prefix beyond
later source records in the same window. A later record whose complete extent is
already covered is skipped after its frame, range digest, and manifest authority
have been validated. Any partial overlap or forward gap relative to the exact
prefix remains terminal.

Operation metadata is still admitted only after the whole payload SHA-256 is
proved and the immutable digest-named payload is durable. A crash after any
record leaves only the existing restartable prefix. A fresh process may replay
an older window; the first replayed record re-observes the durable prefix and
later fully covered records are skipped without rewriting committed bytes.

## Regressions

The protocol regression constructs a two-record cache-cold window and a final
reference-only continuation. It rejects:

- range gaps;
- range overlaps and duplicate offsets;
- mismatched total sizes;
- mismatched manifest digests;
- a repeated complete manifest; and
- a continuation not equal to the final range end.

The service restart regression uses an eight-byte window over a ten-byte file. It
proves two records become one durable eight-byte prefix without operation
admission, destroys every in-memory cursor, replays the same two-record window,
re-observes the prefix once, skips the second covered record, and completes from
offset eight. The shifted-insertion regression sums every record in every page
and retains one source index lookup per window.

The TLS cross-session restart test carries two four-byte records in one
authenticated eight-byte response. It proves the same grouped window across
encode, TLS framing, decode, durable staging, process-level cursor loss, replay,
and final completion. The shipping process oracle carries sixteen four-mebibyte
records in one 64 MiB response and requires one source request and one source
response for that first window.

## Adjacent audit and refactor

The first grouped validator retained a vector of payload pointers inside each
validation group, and the receiver built another vector of pointers per digest.
Both were bounded, but both duplicated range cardinality in exactly the new hot
path. The final implementation keeps scalar validation state and contiguous
`begin/count` spans into the immutable response vector.

The source also checks exhausted record and byte budgets before opening a large
payload and projecting its manifest. A page that cannot admit even one record
therefore stops before paying descriptor, hashing, or index work.

A deterministic regression constructs adjacent canonical whole-file and ranged
operations. The whole four-byte payload consumes the complete byte budget; the
large successor then produces no additional targeted open, manifest scan,
manifest hash, chunk-index lookup, grouped window, range, or byte publication.

## Product boundary and next edge

Rev0996 removes the million-turn default framing multiplier by a factor of
sixteen. It is not a measured 4 TiB transfer, not a target-scale RSS result, and
not proof that 65,536 round trips are acceptable on high-latency Tor or I2P
routes.

It does not add cross-file chunk discovery, multilevel delta, compression,
rename/move identity, complete directory semantics, placeholders, quota/ENOSPC
safety, Android lifecycle/storage adapters, or public-route privacy
qualification.

The next delta-transfer edge is measurement and memory shape: instrument one
bounded response from source copy through encoding, TLS, decode, and staging;
remove avoidable page-sized copies or stream records under one authenticated
frame; and use sparse/synthetic multi-terabyte shapes to quantify turns, peak
RSS, disk amplification, restart, and controlled ENOSPC. Cross-file chunk reuse
and rename/move identity should follow the measured bottleneck rather than
another unmeasured generalization.

## Validation

Exact rev0996 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 275/275 registered tests were accounted for across bounded terminal shards, and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 18/18 source-chunk-index, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, 27/27 multi-range-window, and 472/472 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 31.26 seconds at 1,694,252 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0995 parent SHA-256 matched 1129c9f66ba195ceda3f18b274ae58a997820ce332b44c39f9cfdf0fa033efc2 and passed 41/41 wrapper-aware package checks. The active implementation projection contains 603 files / 27,896,855 bytes with SHA-256 a42f7210b2c2109e990fef097fc26e87497cffe3770b4a1fe4b1de20f6432052. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0996-2026.08.04.20.52-multirangewindow-turncollapse-memoryfrontier-petalite.zip
petalite
