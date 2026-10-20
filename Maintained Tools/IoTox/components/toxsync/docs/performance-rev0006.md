# toxsync 0.3.0 / rev0006 performance record

## Fixture

The retained benchmark creates a 128 MiB deterministic target, copies it as a basis, changes
one byte every 4 MiB, creates a direct-to-disk v1 index, and reconstructs through
`FileRangeSource` using the memory-bounded aligned path.

Configuration:

```text
build:                  GCC 14.2, Release
SHA-256:                OpenSSL EVP
rolling initialization: SSE2
block size:             4 KiB
data buffer:            1 MiB
range descriptor limit: 256
fsync:                   disabled for benchmark
runs:                    7 independent processes
host:                    available virtualized x86-64 environment
```

Fixture files are local and generally page-cached after creation. This record measures the
algorithm/process implementation, not Tox, cold storage, flash, or an IoT target.

## Results

```text
metric                         median
streaming index rate           1,143.65 MiB/s
verified aligned sync rate     1,120.34 MiB/s
index workspace                1,114,096 bytes
sync workspace                 1,060,896 bytes
maximum process RSS            9,824 KiB
encoded index                  786,496 bytes
reused target bytes            134,090,752
fetched target bytes           126,976
coalesced source ranges        31
```

Raw index rates:

```text
1122.62 1143.88 1116.65 1143.65 1144.98 1121.41 1150.20 MiB/s
```

Raw sync rates:

```text
1003.95 1122.47 1128.83 1120.34 942.208 1088.27 1130.18 MiB/s
```

Raw maximum RSS:

```text
9852 9824 9824 9844 9668 9808 9820 KiB
```

## Scale result

Under the 64 MiB metadata budget:

```text
16 TiB target
8 MiB blocks
2,097,152 blocks
50,331,712-byte .txi
less than 9 MiB explicit default sync workspace
```

This is a formula and implementation-limit test. A 16 TiB artifact was not created or read in
this environment.

## Interpretation

The main rev0006 achievement is bounded memory, not a claim that every real sync will exceed
1 GiB/s. Native Tox goodput may be orders of magnitude lower. Larger blocks, cold reads,
compression, treepack extraction, flash writes, CPU throttling, and final durability all
change the result.
