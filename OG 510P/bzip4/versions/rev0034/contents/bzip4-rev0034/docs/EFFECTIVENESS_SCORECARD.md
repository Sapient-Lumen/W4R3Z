# bzip4 effectiveness scorecard — rev0034

## Executive judgment

bzip4 is already effective as a **safer, resource-bounded, parallel BZ3v1
implementation for Datacube**. It is not yet a new compression format and it
has not improved the codec's intrinsic ratio. Its current value is:

1. useful encode/decode throughput under bounded parallelism;
2. exact bzip3 block compatibility for a fixed block split;
3. much stronger frame admission, output bounds, workspace planning, pinned
   input, and atomic publication; and
4. an operational profile contract that Datacube can bind in carrier metadata.

The current evidence supports “faster than bzip3 on this cloudtainer” more than
rev0033's wording did, but the defensible claim is **single-host and
configuration-specific**, not universal.

## Baseline law

“Versus bzip3” has two materially different meanings.

### Equal block policy

At the same effective block size and partition, bzip4 and pristine bzip3 1.5.3
produce byte-identical block records. bzip4's count-bearing high-level frame is
four bytes larger than the upstream EOF-terminated CLI stream because it stores
an explicit block count. Compression ratio is therefore effectively **100% of
bzip3**, not 80%, when policy is equal.

### Recommended bzip4 speed profile versus bzip3's 16 MiB CLI default

On the 546,406,400-byte combined rotating witness:

| Policy | Encoded bytes | Input remaining | Space removed | Compression factor |
|---|---:|---:|---:|---:|
| 1 MiB / 8-lane bzip4 speed profile | 42,705,674 | 7.816% | 92.184% | 12.795× |
| 16 MiB / 8-lane comparison | 32,082,915 | 5.872% | 94.128% | 17.031× |

The 1 MiB result is **33.11% larger as a compressed file**, yet it retains
**97.93% of the bytes saved** by the 16 MiB result. Expressed as compression
factor, it retains only **75.13%**. Any requirement such as “80% as effective”
must name the metric; those three descriptions are all mathematically correct.

For Datacube, “fraction of original bytes eliminated” is usually the most
useful operational measure because transfer and storage cost are linear in
bytes. Final encoded bytes must still be recorded directly.

## Current metric table

| Concern | Current state | bzip3 baseline | Confidence |
|---|---|---|---|
| Lossless correctness | Exact reconstruction across oracle, rotating cubes, malformed-frame tests, and profile round trips | Same intended property | High |
| Ratio at equal block split | Same block bytes; bzip4 frame is +4 bytes | Baseline | High |
| Compression speed, matched GCC O3 | 14.85% lower wall time on the current 521.09 MiB witness | Upstream 1.5.3 | Medium; 3 runs, one host |
| Decompression speed, matched GCC O3 | 11.65% lower wall time | Upstream 1.5.3 | Medium; 3 runs, one host |
| Compression speed, matched Clang O3 | 5.10% lower wall time | Upstream 1.5.3 | Medium; 3 runs, one host |
| Decompression speed, matched Clang O3 | 8.40% lower wall time | Upstream 1.5.3 | Medium; 3 runs, one host |
| Best tested compiler | Clang O3 was 10.18% faster than GCC O3 for bzip4 compression and 14.77% faster for decompression | Upstream is also strongly compiler-sensitive | Medium |
| 1 MiB / 8-lane charged workspace | 60,925,136 bytes | Upstream has no equivalent whole-frame admission receipt | High |
| 1 MiB / 8-lane observed process RSS | roughly 75–85 MiB in current witnesses | roughly 68–79 MiB in matched CLI runs | Medium |
| 3 GB cloudtainer fit | Recommended profiles fit with very large headroom | 16 MiB × many lanes can spend hundreds of MiB | High |
| Parallel scaling | Strong through 4 lanes; useful to about 8 lanes on this host; 16 lanes previously added memory without time gain | Upstream creates per-call threads | Medium |
| Small Datacube capsule latency | 256 KiB / up to 8 lanes: about 32.1 ms encode and 27.6 ms decode in the prior 30-repetition in-memory witness | Same codec at a maximum single block was about 4× slower | Medium |
| Malformed input behavior | Complete envelope preflight, cumulative output ceiling, exact terminals, fail-fast truncation, contracted decoder workspace | Less centralized and less explicit | High |
| File safety | Descriptor-pinned source, mutation check, private staging file, file fsync, atomic rename, directory fsync | Ordinary CLI publication | High |
| Provenance | Carried pristine oracle, source closure, manifest, fresh-extraction rebuild, static tools | Upstream source only | High |
| Datacube admission | Codec side is close; carrier/source-budget and metadata weld remain | No Datacube contract | Medium |

## Compiler-fair correction

rev0033 reported an 11.4% compression lead for its shipped binary, but that
comparison used GCC O3 without LTO for upstream and GCC IPO for bzip4. It was a
valid final-binary witness, not an implementation-isolated comparison.

rev0034 adds an interleaved matched matrix. The result is better and more
nuanced:

| Build pair | bzip3 encode | bzip4 encode | bzip3 decode | bzip4 decode |
|---|---:|---:|---:|---:|
| GCC 14.2 O3 | 9.000 s | 7.663 s | 8.300 s | 7.333 s |
| Clang 17 O3 | 7.253 s | 6.883 s | 6.823 s | 6.250 s |
| GCC LTO / IPO | 8.603 s | 7.710 s | 7.863 s | 7.367 s |

Each cell is the arithmetic mean of three taskset-pinned end-to-end runs over
521.09 MiB at 1 MiB blocks and eight lanes. bzip4 also performed durable atomic
publication; upstream wrote redirected stdout without an explicit fsync. User
CPU time showed the same direction. The matrix still remains one-host evidence.

The key conclusion is not merely “bzip4 is faster.” It is that **compiler and
code-generation choice is at least as important as the C-to-C++ implementation
difference**. Clang is now the default convenience-binary compiler for this
release; GCC remains a required validation compiler.

## Block-size effectiveness

The user's observation is correct: increasing block size usually improves
ratio. It does not monotonically improve it, and it can destroy the very
parallelism needed for cloudtainer latency.

For the combined witness:

| Block / lanes admitted | Encoded bytes | Encode | Decode | Charged codec workspace |
|---|---:|---:|---:|---:|
| 1 MiB / 8 | 42,705,674 | 4.48 s | 4.04 s | 60.9 MB |
| 4 MiB / 8 | 35,626,074 | 4.47 s | 5.16 s | 214.9 MB |
| 16 MiB / 8 | 32,082,915 | 5.41 s | 5.91 s | 831.0 MB |
| 32 MiB / 8 | 30,484,802 | 5.44 s | 5.12 s | 1.652 GB |
| 64 MiB / 6 | 30,279,230 | 6.89 s | 6.86 s | 2.471 GB |
| 128 MiB / 3 | 29,971,968 | 10.36 s | 10.12 s | 2.468 GB |
| 256 MiB / 1 | 30,203,958 | 17.00 s | >300 s, terminated | 1.644 GB |

The safe interpretation is:

- 1 MiB is the current general speed point;
- 2 MiB is the current measured speed/size compromise;
- 4 MiB may be competitive for one large continuous stream but is worse for a
  set of smaller cubes and slower to decode in the combined witness;
- 16–128 MiB are explicit ratio experiments, not automatic settings; and
- 256 MiB exposed a severe decode-time pathology and is operationally rejected
  until profiled and explained.

## Memory effectiveness

The rotating corpus size does not determine codec arena memory. The important
quantity is approximately block workspace × simultaneously active lanes.
Recommended profiles charge:

| Profile | Fixed requested block | Lane cap | Maximum profile arena charge |
|---|---:|---:|---:|
| `datacube-capsule-speed-v1` | 256 KiB | 8 | 22,421,408 bytes |
| `cloudtainer-speed-v1` | 1 MiB | 8 | 60,925,136 bytes |
| `cloudtainer-balanced-v1` | 2 MiB | 8 | 112,263,440 bytes |

All three use a 128 MiB default codec-workspace budget and fit beneath it. This
is deliberately far below a nominal 3 GB container ceiling. Datacube still must
reserve memory for its own process, thread stacks, allocator metadata, input and
output, page cache, and concurrent heavy operations.

The planner's charge is a conservative admission bound, not predicted resident
set size. At giant blocks, observed RSS can be much lower than the charged
virtual arena; Datacube should enforce the charge and record process HWM as a
separate receipt.

## Safety effectiveness

Safety work is not decorative overhead here. Datacube's codec boundary needs to
reject impossible or adversarial frames before allocating large arenas or
publishing bytes. bzip4 currently provides:

- fixed-size envelope reads and complete predecode validation;
- checked block counts, record spans, cumulative output, and workspace;
- exact LZP, modified-RLE, arithmetic-stream, and BWT terminal checks;
- truncation fail-fast behavior;
- decoder workspace contracted to validated actual blocks;
- descriptor-pinned input with mutation detection;
- atomic and durability-checked output publication;
- bounded retained worker pools and explicit lane admission; and
- an independently compiled pristine bzip3 oracle.

Those features make bzip4 substantially more suitable than the stock CLI for a
provenance-sensitive embedder even in a hypothetical exact speed tie.

## Remaining gaps

1. Datacube has not admitted the codec. It still needs source-budget space,
   authenticated profile ID, stored/plain hashes, limits, old-reader behavior,
   carrier mutation tests, and a source-only whole-file rebuild proof.
2. The shipped profile identifier is external metadata. BZ3v1 itself does not
   encode it. Multiple profiles can converge to the same effective block size
   for small inputs, so frame inspection can prove compatibility with a profile
   block law, not unique profile identity.
3. Current speed evidence is one host and three repetitions per compiler cell.
   A rotating next-session cohort and a second machine remain necessary.
4. The embedded libsais lineage is old and heavily patched. Updating it may be
   valuable, but byte identity, workspace, UB repairs, and pathological inputs
   must all be re-proved.
5. The 256 MiB decoder pathology needs cycle-level attribution before any large
   automatic block policy can be trusted.

## Bottom line

For Datacube's present priority order, bzip4 is in a strong state:

- **speed:** promising and currently ahead of bzip3 in matched host witnesses;
- **ratio:** identical at equal policy, intentionally traded for speed by the
  recommended smaller-block profiles;
- **memory:** comfortably below the cloudtainer ceiling at recommended profiles;
- **safety/provenance:** substantially stronger than stock bzip3; and
- **integration:** technically close, but not yet admitted into Datacube.

The next major win is more likely to come from Clang, current libsais/prefetch
work, PGO, and retained in-process service operation than from dictionaries or a
new compression format.
