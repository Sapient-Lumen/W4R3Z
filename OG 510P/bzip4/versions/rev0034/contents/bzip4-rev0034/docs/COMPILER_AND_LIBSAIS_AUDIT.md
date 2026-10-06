# Compiler and libsais speed audit — rev0034

## Why this audit exists

rev0033's direct final-binary witness compared the shipped GCC-IPO bzip4 tool
with an upstream bzip3 tool built using GCC `-O3` without LTO. It was a valid
comparison of those two binaries, but it did not isolate implementation effects.
Because bzip3 spends much of its time in the BWT implementation, compiler and
libsais code generation can dominate the result.

rev0034 therefore adds a matched compiler matrix and changes the convenience
binary policy from GCC IPO to Clang 17 `-O3` without IPO.

## Matched result

The witness is a deterministic 546,406,400-byte stream derived from the 16
rotating cubes supplied in this session. Tests used 1 MiB blocks, eight lanes,
CPU affinity 0–7, and three interleaved repetitions per cell.

| Build pair | bzip3 encode | bzip4 encode | bzip4 lead | bzip3 decode | bzip4 decode | bzip4 lead |
|---|---:|---:|---:|---:|---:|---:|
| GCC 14.2 `-O3` | 9.000 s | 7.663 s | 14.85% | 8.300 s | 7.333 s | 11.65% |
| Clang 17 `-O3` | 7.253 s | 6.883 s | 5.10% | 6.823 s | 6.250 s | 8.40% |
| GCC LTO / bzip4 IPO | 8.603 s | 7.710 s | 10.38% | 7.863 s | 7.367 s | 6.32% |

All bzip3 outputs were identical to one another. All bzip4 outputs were
identical to one another. The two native streams differed only by bzip4's
four-byte explicit block-count field, and every decode matched the input hash.

The stronger conclusion is not a universal percentage. It is:

- bzip4 is competitive with and currently ahead of bzip3 under matched builds
  on this cloudtainer;
- Clang improved both implementations substantially;
- GCC IPO did not beat ordinary GCC `-O3` for bzip4 in this matrix; and
- compiler selection must be treated as a first-class benchmark dimension.

bzip4 performs descriptor-pinned reads and durable atomic publication, including
file and directory synchronization. The upstream CLI wrote redirected standard
output without an explicit durability sync. This slightly disadvantages bzip4
in wall-clock comparison, but the result remains one-host evidence.

## Why online research changed the plan

The current bzip3 documentation explicitly says performance is heavily
compiler-dependent and cites Clang results. The current libsais documentation
recommends Clang, describes the algorithm as memory-bandwidth-bound, and says
many dual-channel x86-64 systems saturate near eight threads. Those statements
match this session's observed Clang advantage and the previous eight-versus-
sixteen-lane plateau.

The active bzip4 amalgamation is a 2021–2022-era libsais lineage inherited from
bzip3 and then safety-patched locally. Current upstream libsais v2.10.4 reports
prefetch-distance tuning, while v2.10.2 reports BWT improvements on degenerate
inputs. That makes a controlled update branch a better near-term speed bet than
adding a new compression transform.

Primary references checked on 2026-06-20:

- https://github.com/iczelia/bzip3
- https://github.com/IlyaGrebnov/libsais
- https://github.com/IlyaGrebnov/libsais/releases/tag/v2.10.4

## Update protocol for libsais

A libsais update is not a header replacement. The active copy contains bzip3
stability patches plus bzip4 repairs for signed marker shifts, suffix-marker
arithmetic, and compaction decrements. Any candidate must:

1. preserve the pristine bzip3 1.5.3 oracle unchanged;
2. import and record a precise new upstream libsais revision;
3. re-audit every local patch against the new implementation rather than
   blindly replaying line edits;
4. pass GCC, Clang, ASan/UBSan, ThreadSanitizer, and poisoned-workspace tests;
5. prove exact encoded block identity for the compatible format;
6. cover degenerate, repetitive, random, minimum, maximum, and truncated cases;
7. remeasure 1/2/4/8-lane encode and decode, memory charge, and RSS; and
8. reject the update if either direction slows materially on rotating data.

## Build policy

- Clang 17 `-O3`, IPO off: convenience Linux x86-64 binaries in rev0034.
- GCC 14.2 `-O3`: required independent production validation.
- GCC IPO: retained as an optional experiment, not the release default.
- PGO: next measured compiler experiment; no gain is assumed in advance.
- Source: canonical in all cases. A static binary is a convenience artifact,
  not by itself a Datacube admission.

The complete raw matrix is carried in `evidence/compiler-fair-matrix.json`.
