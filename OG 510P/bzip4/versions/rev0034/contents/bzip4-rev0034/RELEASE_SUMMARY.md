# bzip4 rev0034 release summary

## Release focus

rev0034 converts speed policy into an operational contract and corrects the
performance narrative. It adds three immutable named profiles, profile-aware
planning and encode/decode commands, a matched bzip3 compiler matrix, Clang-built
static convenience tools, an effectiveness scorecard, and a falsifiable
prediction register.

The codec remains the compatible BZ3v1 implementation. No new BZ4 wire format,
dictionary, or ratio-changing transform is introduced.

## Effectiveness versus bzip3

Equal block partitioning produces identical block records. bzip4's count-bearing
high-level frame is four bytes larger than the upstream EOF-terminated CLI
stream. Equal-policy ratio is therefore effectively bzip3's ratio.

The previous release's 11.4% compression headline compared a GCC-IPO bzip4
binary with upstream built using GCC `-O3` without LTO. rev0034 preserves that
historical witness but supersedes it as an implementation-isolated claim.

A new three-round matched matrix over 546,406,400 bytes at 1 MiB / eight lanes
measured:

| Matched build | Encode lead | Decode lead |
|---|---:|---:|
| bzip4 vs bzip3, GCC 14.2 `-O3` | 14.85% | 11.65% |
| bzip4 vs bzip3, Clang 17 `-O3` | 5.10% | 8.40% |

Clang also reduced bzip4 time by 10.18% encode and 14.77% decode relative to
GCC `-O3` on this host. GCC IPO was slightly slower than ordinary GCC `-O3` for
bzip4 in the matched matrix. The defensible conclusion is that bzip4 is
currently ahead on this cloudtainer and compiler choice is a first-order
variable; no universal percentage is claimed.

## Operational profiles

The new registry contains:

- `datacube-capsule-speed-v1`: 256 KiB, requested 8 lanes;
- `cloudtainer-speed-v1`: 1 MiB, requested 8 lanes; and
- `cloudtainer-balanced-v1`: 2 MiB, requested 8 lanes.

All default to a 128 MiB codec-workspace budget. The planner reduces active
lanes for block count or memory but never changes block size. Profile encode and
decode fail before publication if one lane cannot fit or if a validated frame
is incompatible with the requested block law.

BZ3v1 does not carry the profile name. Datacube must authenticate it in carrier
metadata. Small inputs may be compatible with more than one profile because the
requested block sizes can converge to the same effective legal block size.

The historical numeric CLI remains available. Its two-argument compression
form still defaults to 16 MiB scalar behavior and is explicitly documented as
nonrecommended for production Datacube use.

## Ratio interpretation

On the combined witness, 1 MiB / eight lanes produced 42,705,674 bytes while
16 MiB / eight lanes produced 32,082,915 bytes. The 1 MiB file was 33.11%
larger, yet it retained 97.93% of the bytes eliminated by 16 MiB. It retained
75.13% of the compression factor. rev0034 records all three views so future
“80% effective” requirements cannot silently switch metrics.

The user's larger-block ratio observation is directionally correct. It is not
monotonic, and speed degrades when outer parallelism or decoder behavior
collapses. A 256 MiB decode exceeded 300 seconds and was terminated; it remains
operationally rejected.

## Static binary policy

The four Linux x86-64 convenience tools are now built with Clang 17 `-O3`, IPO
off, and `-static`. GCC remains a mandatory validation compiler. Source is
canonical, and the binaries alone do not constitute Datacube admission.

Online review materially informed this choice: current bzip3 documentation
states that performance is heavily compiler-dependent, while current libsais
documentation recommends Clang, describes memory-bandwidth saturation, and
reports recent prefetch/BWT performance work.

## Datacube status

Datacube rev0117 is unchanged and still declares `none-v1`. Profile naming
closes one codec-side gap, but the carrier still needs source-budget space,
carried code and notices, authenticated profile/build identity, stored/plain
hashes and limits, old-reader semantics, mutation canaries, and a source-only
whole-file rebuild gate.

## Validation target

The suite now contains 23 strict groups, including the new codec-profile group.
Release validation covers GCC, Clang, ASan/UBSan, ThreadSanitizer,
poisoned-workspace, GCC IPO, static Clang builds, exact profile round trips,
incompatible-profile no-publication behavior, manifest/source closure, and a
fresh extracted rebuild.

## Predictions and next work

The release predicts a 3–12% median matched-Clang bzip4 lead on the next
rotating cohort, expects 1 MiB to remain at or near the speed optimum, and gives
a controlled current-libsais update a 55% chance of a ≥3% gain in at least one
direction. These are predeclared forecasts, not claims.

Immediate priority order:

1. controlled current-libsais/prefetch branch with exact-byte and safety gates;
2. Datacube codec admission using the named profile metadata contract;
3. broader rotating-cohort and second-machine compiler-fair measurements;
4. PGO and retained in-process operation; and
5. continued giant-block pathology attribution.

Dictionary work remains frozen unless it improves both directions within the
same memory budget on unseen data.
