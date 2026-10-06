# Speed-first block-size policy — rev0034

## Decision

bzip4 is now optimized and evaluated primarily for elapsed compression and
elapsed decompression time under an explicit memory budget. Compression ratio
is a tie-breaker and a no-regression concern, not the primary objective.
Dictionary work is frozen unless it makes both directions faster within the
same memory envelope.

The project remains a BZ3v1-compatible implementation. Block size changes the
serialized frame partition and therefore belongs in a stable codec parameter
profile. Lane count changes only scheduling and may be fitted locally to the
available workspace without changing encoded bytes.

A ratio statement must name its metric. On the combined witness, the 1 MiB
speed result was 33.11% larger than the 16 MiB compressed file, retained 75.13%
of its compression factor, and still retained 97.93% of the source bytes
eliminated. The release reports final bytes directly and uses “fraction of
source bytes eliminated” only as a secondary operational view.

## Does the largest block maximize ratio?

Usually larger blocks helped this corpus, but not monotonically and not for
free. The current session supplied 16 rotating Datacube-like archives. They
were unpacked into deterministic tar streams and tested with exact round trips.
The specimens are useful target evidence but are not carried release inputs.

For the aggregate of 16 separately compressed cube payloads:

| Block | Encoded bytes | Encode sum | Decode sum | Peak encode RSS | Peak decode RSS |
|---:|---:|---:|---:|---:|---:|
| 128 KiB | 58,849,371 | 5.98 s | 5.53 s | 33.8 MiB | 38.1 MiB |
| 256 KiB | 52,627,333 | 4.82 s | 4.64 s | 38.2 MiB | 41.8 MiB |
| 512 KiB | 47,017,124 | 4.93 s | 4.36 s | 51.7 MiB | 53.5 MiB |
| **1 MiB** | **42,537,570** | **4.67 s** | **4.39 s** | 80.7 MiB | 82.2 MiB |
| 2 MiB | 38,520,562 | 4.89 s | 4.49 s | 113.2 MiB | 115.6 MiB |
| 4 MiB | 35,125,635 | 6.12 s | 6.09 s | 172.0 MiB | 174.2 MiB |
| 8 MiB | 32,299,966 | 8.03 s | 7.68 s | 273.4 MiB | 276.0 MiB |
| 16 MiB | 31,466,198 | 10.00 s | 10.04 s | 442.0 MiB | 443.6 MiB |
| 32 MiB | 30,662,810 | 11.99 s | 11.08 s | 518.9 MiB | 521.0 MiB |
| 64 MiB | 30,462,979 | 13.75 s | 13.09 s | 511.3 MiB | 513.1 MiB |

One MiB minimized aggregate encode-plus-decode time in this witness. Two MiB
made the output 9.44% smaller than one MiB while adding about 4.7% encode time
and 2.3% decode time. Four MiB made the output 17.4% smaller than one MiB, but
encode and decode sums each rose by roughly 31–39% because smaller cubes no
longer supplied enough blocks to use all lanes.

A single combined 546,406,400-byte stream showed the same ratio direction but
a different speed surface:

| Block / lanes | Encoded bytes | Encode | Decode | Charged codec workspace |
|---:|---:|---:|---:|---:|
| 1 MiB / 8 | 42,705,674 | 4.48 s | 4.04 s | 60.9 MB |
| 4 MiB / 8 | 35,626,074 | 4.47 s | 5.16 s | 214.9 MB |
| 16 MiB / 8 | 32,082,915 | 5.41 s | 5.91 s | 831.0 MB |
| 32 MiB / 8 | 30,484,802 | 5.44 s | 5.12 s | 1,652.4 MB |
| 64 MiB / 6 | 30,279,230 | 6.89 s | 6.86 s | 2,471.4 MB |
| 128 MiB / 3 | 29,971,968 | 10.36 s | 10.12 s | 2,467.8 MB |
| 256 MiB / 1 | 30,203,958 | 17.00 s | >300 s | 1,644.0 MB |

The 256 MiB frame was larger than the 128 MiB frame, so “larger always means
smaller” is false even on this target family. Its decoder also exceeded five
minutes before the witness was terminated. This is an operational rejection of
that setting, not a claim that the frame was corrupt.

Moving from 32 MiB to 64 MiB saved only 205,572 bytes, or 0.67% of the 32 MiB
output, while encode and decode time rose by about 27% and 34%. The extra block
size also reduced the budget-fitting lane count from eight to six under the
2.8 GB codec-workspace witness budget.

## The actual Datacube capsule points toward small blocks

The supplied Datacube rev0117 carries a 1,868,846-byte plaintext source capsule.
A 30-repetition in-memory retained-pool witness measured:

| Requested block | Blocks / lanes | Encoded bytes | Mean encode | Mean decode |
|---:|---:|---:|---:|---:|
| **256 KiB** | **8 / 8** | 368,948 | **0.0321 s** | **0.0276 s** |
| 512 KiB | 4 / 4 | 344,686 | 0.0393 s | 0.0331 s |
| 1 MiB | 2 / 2 | 335,602 | 0.0697 s | 0.0674 s |
| maximum effective block | 1 / 1 | 315,163 | 0.1276 s | 0.1229 s |

The one-block encoding was 14.6% smaller than the 256 KiB encoding, but roughly
four times slower in both directions. If Datacube decodes the capsule on common
startup paths, this latency result matters more than the approximately 54 KiB
stored-size difference.

## Recommended profiles

These measured recommendations are now represented by an operational profile registry:

- **`datacube-capsule-speed-v1`:** fixed 256 KiB block, requested eight
  lanes, workspace-fitted at runtime. This is the current recommendation for a
  roughly two-megabyte capsule.
- **`cloudtainer-speed-v1`:** fixed 1 MiB block, requested eight lanes. It
  won aggregate elapsed time on the rotating cube cohort while using only about
  60.9 MB of charged codec workspace.
- **`cloudtainer-balanced-v1`:** fixed 2 MiB block, requested eight lanes.
  It retained near-best time and saved 9.44% versus the one MiB output in the
  separate-cube witness.
- **Ratio-biased experiments:** 4–32 MiB only after a complete encode/decode/RSS
  oracle on the actual payload shape. They are not defaults.
- **Rejected default range:** 64 MiB and above. These settings may remain legal
  for explicit experiments but should never be selected automatically by the
  speed-first profile.

The named profile is external authenticated metadata: BZ3v1 stores effective
block size, not the profile name. Small inputs can make profiles converge, so
frame preflight proves compatibility with the block law rather than unique
profile identity. Datacube must bind the identifier itself. A different fixed
profile can be introduced when future capsule sizes justify it. Runtime lane
fitting is safe because lane count is not serialized and cannot change bytes.
The historical two-argument `compress` command remains 16 MiB scalar behavior
and is not the recommended profile path.

## Memory interpretation

Per-lane workspace grows almost linearly with block size: approximately 7.6 MB
at one MiB, 14.0 MB at two MiB, 26.9 MB at four MiB, 103.9 MB at 16 MiB,
206.6 MB at 32 MiB, 411.9 MB at 64 MiB, and 822.6 MB at 128 MiB.

The current Datacube environment observation reported 4 GiB total and about
3.25 GiB available, but its own provisional policy reserves headroom and limits
one heavy operation to at most half of currently available memory. Therefore,
2.8 GB is useful as a stress witness, not a recommended Datacube default.
The speed profiles need far less: eight one-MiB lanes charge 60,925,136 bytes,
and eight two-MiB lanes charge 112,263,440 bytes.

## Dictionary and ratio work

The prior zstd FastCover proxy improved held-out size but slowed compression by
about 22% and decompression by about 12%. Under the current priorities that is a
clear rejection. No dictionary lane should enter the hot path unless an unseen,
rotating cohort demonstrates:

1. faster compression;
2. faster decompression;
3. exact reconstruction and deterministic bytes;
4. bounded prepared-dictionary memory shared across lanes; and
5. no unacceptable final-size regression after charging dictionary bytes.

Until then, compatible BWT, entropy, CRC, scheduling, compiler-layout, and I/O
work outrank all trained-format research.

## Evidence boundary

The machine-readable measurements are in
`evidence/current-session-block-size-frontier.json` and
`evidence/datacube-capsule-speed-frontier.json`. They are single-host witnesses.
They establish the direction for this revision, not universal performance.
