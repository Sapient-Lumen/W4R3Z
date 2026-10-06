# bzip4 rev0034

bzip4 is a speed-first, resource-bounded C++20 implementation of the bzip3
1.5.3 codec, built for eventual admission into Datacube. It remains
**BZ3v1-compatible at the block level**. It is not yet a new BZ4 format and it
does not claim a new intrinsic compression ratio.

rev0034 turns the measured block-size recommendations into named operational
profiles, corrects the bzip3 comparison with a matched compiler matrix, ships
Clang-built static convenience tools, and records explicit predictions for the
next rotating cohorts.

## Current effectiveness

At the same block partition, bzip4 and the carried pristine bzip3 1.5.3 oracle
produce identical block records. bzip4's high-level frame is four bytes larger
than the upstream CLI stream because it stores an explicit block count.
Therefore equal-policy ratio is effectively **100% of bzip3**.

On one 546,406,400-byte rotating witness at 1 MiB and eight lanes, matched
three-round builds measured:

| Compiler | bzip4 encode vs bzip3 | bzip4 decode vs bzip3 |
|---|---:|---:|
| GCC 14.2 `-O3` | 14.85% lower elapsed time | 11.65% lower |
| Clang 17 `-O3` | 5.10% lower elapsed time | 8.40% lower |

Those are single-host directional results, not universal guarantees. Compiler
choice was itself a major effect: Clang reduced bzip4 elapsed time by 10.18% for
encode and 14.77% for decode relative to matched GCC `-O3` on this witness.

The recommended 1 MiB speed policy intentionally sacrifices some ratio versus
16 MiB in exchange for parallel latency. On the same input, 1 MiB output was
33.11% larger as a compressed file, but still eliminated 97.93% as many source
bytes as the 16 MiB result. See `docs/EFFECTIVENESS_SCORECARD.md` for why an
“80% of bzip3” target is ambiguous unless the ratio metric is named.

## Recommended profile commands

List the immutable registry:

```sh
bin/linux-x86_64/bzip4_codec profiles
```

Plan without creating workers or codec states:

```sh
bin/linux-x86_64/bzip4_codec profile-plan \
  cloudtainer-speed-v1 INPUT_BYTES
```

Compress and decompress with the general speed profile:

```sh
bin/linux-x86_64/bzip4_codec compress-profile \
  cloudtainer-speed-v1 INPUT OUTPUT.bz3

bin/linux-x86_64/bzip4_codec decompress-profile \
  cloudtainer-speed-v1 OUTPUT.bz3 RESTORED MAX_OUTPUT_BYTES
```

Profiles carried by this release:

| Profile | Requested block | Requested lanes | Default codec budget |
|---|---:|---:|---:|
| `datacube-capsule-speed-v1` | 256 KiB | 8 | 128 MiB |
| `cloudtainer-speed-v1` | 1 MiB | 8 | 128 MiB |
| `cloudtainer-balanced-v1` | 2 MiB | 8 | 128 MiB |

The planner fits lane count to work and workspace. It never changes the
profile's block size. If one lane cannot fit, the operation fails before output
publication. The historical `compress INPUT OUTPUT` command still defaults to
16 MiB and one lane; it remains available for experiments but is not the
recommended Datacube path.

## Why these block sizes

Increasing block size generally improves ratio, but it reduces outer
parallelism and can trigger poor cache or algorithmic behavior.

For one combined 521.09 MiB witness:

| Block / admitted lanes | Encoded bytes | Encode | Decode | Charged codec workspace |
|---|---:|---:|---:|---:|
| 1 MiB / 8 | 42,705,674 | 4.48 s | 4.04 s | 60.9 MB |
| 4 MiB / 8 | 35,626,074 | 4.47 s | 5.16 s | 214.9 MB |
| 16 MiB / 8 | 32,082,915 | 5.41 s | 5.91 s | 831.0 MB |
| 64 MiB / 6 | 30,279,230 | 6.89 s | 6.86 s | 2.471 GB |
| 256 MiB / 1 | 30,203,958 | 17.00 s | >300 s, terminated | 1.644 GB |

On the separate-cube aggregate, 2 MiB produced 9.44% fewer encoded bytes than
1 MiB while adding 4.7% encode time and 2.3% decode time; its eight-lane charge
is 112.3 MB.

The actual 1,868,846-byte Datacube rev0117 source capsule measured about four
times faster at 256 KiB / up to eight lanes than as one maximum-size block,
with a 17.1% output-size cost. Hence the separate capsule profile.

The 256 MiB decoder behavior is an explicit rejection signal. Giant blocks are
ratio experiments, not automatic speed settings.

## Memory and cloudtainer fit

Codec arena memory is driven primarily by block workspace × active lanes, not
total corpus length. Maximum eight-lane charges for the three profiles are:

- 22,421,408 bytes at 256 KiB;
- 60,925,136 bytes at 1 MiB; and
- 112,263,440 bytes at 2 MiB.

These fit under the profiles' 128 MiB default codec budget and leave substantial
headroom beneath a nominal 3 GB cloudtainer ceiling. The charge is an admission
bound, not a process-RSS forecast; Datacube must separately account for stacks,
allocator metadata, I/O buffers, page cache, staging, and its own concurrent
work.

## Safety and provenance

bzip4's main advantage over the stock CLI is not just throughput. The library
and tools provide:

- complete frame-envelope validation before decode;
- cumulative output and exact workspace bounds;
- exact LZP, modified-RLE, arithmetic-stream, and BWT terminal checks;
- fail-fast handling of truncated arithmetic streams;
- decoder workspace contracted to validated actual blocks;
- descriptor-pinned input and source-mutation detection;
- private staging, file fsync, atomic rename, and directory fsync;
- bounded retained worker pools with deterministic ordered publication;
- ZIP/ZIP64 Datacube preflight without extraction;
- an independently compiled pristine bzip3 1.5.3 oracle; and
- manifest, source-closure, fresh-extraction, sanitizer, and poison gates.

The profile ID is external metadata. BZ3v1 records effective block size but does
not record `cloudtainer-speed-v1`. Multiple profiles can converge on small
inputs, so Datacube must authenticate the profile identifier alongside stored
and plaintext hashes and limits.

## Datacube status

The supplied Datacube rev0117 remains `compression_codec = none-v1`; rev0034
does not modify or claim admission into Datacube. The codec side now has an
operational profile contract, but the carrier still needs:

- a deliberate native-source budget increase (the inspected revision reported
  only 675 bytes remaining);
- carried source and notices;
- authenticated profile/build identity;
- stored and plaintext hashes plus output/workspace limits;
- unsupported-reader semantics;
- carrier-level mutation canaries; and
- a source-only exact whole-file rebuild proof.

## Compiler and next speed work

The shipped Linux x86-64 convenience tools are static Clang 17 `-O3` builds,
with IPO disabled. GCC 14.2 remains a required independent validation compiler.
The current bzip3 and libsais documentation both emphasize compiler sensitivity;
current libsais also identifies memory bandwidth and prefetching as important.

The active codec still carries an older 2021–2022 libsais lineage plus local
safety repairs. The next high-value experiment is a controlled current-libsais
branch, not an unreviewed header replacement. PGO and retained in-process
Datacube operation follow it. Dictionary work remains frozen because the prior
proxy improved size while slowing both directions.

See:

- `docs/COMPILER_AND_LIBSAIS_AUDIT.md`
- `docs/PROFILE_POLICY.md`
- `docs/PREDICTION_REGISTER.md`
- `docs/ROADMAP.md`

## Build and test

Portable release build:

```sh
cmake -S . -B /tmp/bzip4-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /tmp/bzip4-build -j2
ctest --test-dir /tmp/bzip4-build --output-on-failure
```

Recommended convenience-binary compiler:

```sh
CC=clang CXX=clang++ cmake -S . -B /tmp/bzip4-clang -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build /tmp/bzip4-clang -j2
ctest --test-dir /tmp/bzip4-clang --output-on-failure
```

Static Linux build:

```sh
CC=clang CXX=clang++ cmake -S . -B /tmp/bzip4-static -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DCMAKE_EXE_LINKER_FLAGS=-static
cmake --build /tmp/bzip4-static -j2
ctest --test-dir /tmp/bzip4-static --output-on-failure
```

Optional GCC IPO remains available with `-DBZIP4_ENABLE_IPO=ON`, but rev0034
does not recommend it as the default. `scripts/validate.sh` runs the portable
release gate; the sanitizer, ThreadSanitizer, poisoned-workspace, IPO, and static
build receipts are carried under `evidence/validation/`.

## Other commands

```sh
bzip4_codec plan INPUT_SIZE BLOCK_SIZE LANES [MAX_WORKSPACE_BYTES]
bzip4_codec compress-fit INPUT OUTPUT BLOCK_SIZE LANES MAX_WORKSPACE_BYTES [SERIALIZE_READS]
bzip4_codec decompress-fit INPUT OUTPUT MAX_OUTPUT MAX_WORKSPACE_BYTES LANES [SERIALIZE_READS]
bzip4_codec inspect INPUT MAX_OUTPUT_BYTES [MAX_WORKSPACE_BYTES]
bzip4_cube_preflight [--probe-payload-duplicates] CUBE.zip [MORE.zip ...]
bzip4_release_audit RELEASE_ROOT
```

## Claims and nonclaims

rev0034 claims an operational profile interface, matched single-host speed
evidence, exact compatible bytes, bounded memory planning, and the existing
safety/provenance envelope. It does not claim a new format, an intrinsic ratio
improvement, universal speed percentages, a dictionary feature, or Datacube
admission.
