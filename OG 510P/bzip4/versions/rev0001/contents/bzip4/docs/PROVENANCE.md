# Provenance and baseline verification

## Baseline identity

Revision 0001 is derived from **bzip3 1.5.3**, the upstream release published on 2025-08-13. The official project is `iczelia/bzip3` on GitHub. The imported tree identifies itself as version 1.5.3 in its CMake configuration and codec version string.

Because direct archive transfer was unavailable in the build environment, the exact source tree was obtained through the packaged source in Cargo crate:

- Crate: `libbzip3-sys`
- Crate version: `0.5.1+1.5.3`
- Crate SHA-256: `d2a00fe0cfbd644674a56106ec593014b3f95e94c185fd5d4a75c397cd3b0805`
- Embedded path: `bzip3/`

The imported source snapshot is retained byte-for-byte at `upstream/bzip3-1.5.3/`. The top-level project never compiles that directory.

## Recorded baseline file hashes

```text
42fab2ee9d473b2018abd59b6498b093e8b27bb1af2d0bd64a8eaac3ec6eeebe  src/libbz3.c
3cec3b2f01bb83b18b6fb49fd05c9126b514c853d70b0b5d352c5354fbb1cbfe  src/main.c
4e9f8ba96412f97960ba4950cd8b8a4d1e0d93157d3c821c88506b951fb787a5  include/libsais.h
```

These hashes refer to files under `upstream/bzip3-1.5.3/`, not the active C++ port.

## Behavioral verification

The validation environment separately built the unmodified snapshot with GCC as C99 and built bzip4 with GCC as strict C++20.

A deterministic 12,578,667-byte mixed source/random corpus was compressed with both CLIs at 1 MiB blocks and four workers. The two archives were byte-identical:

```text
f30709338305595e44d95359d49eb2c903458bcf30e7aed355825712beea9668
```

Each implementation decoded the other implementation’s archive and reproduced the input SHA-256:

```text
beb23a1c5ecd311e68b51ffe477d284bccae543b748f317330a1b9aed66badb5
```

The active C++ port subsequently received safety fixes that do not alter normal CLI archive output. The final test report records the post-fix rerun.

## Intentional differences

The active tree is not a textually mechanical rename. It makes defined C++20 substitutions for C-only or unsafe behavior:

- variable-length arrays become vectors;
- resource lifetime uses RAII where introduced;
- signed marker wraparound is expressed through unsigned bit representation;
- negative frame lengths are rejected before I/O;
- the high-level frame API fixes exact-block input handling;
- `bz3_free(nullptr)` is accepted.

The upstream tree remains available for every differential investigation.
