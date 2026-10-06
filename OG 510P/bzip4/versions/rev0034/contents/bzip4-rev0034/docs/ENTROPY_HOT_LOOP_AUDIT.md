# Entropy hot-loop audit — rev0028

## Scope and compatibility boundary

This audit covers only the BZ3v1 bitwise arithmetic encoder and decoder in
`src/libbz3.cpp`. It does not change the probability model, counter widths,
initial values, update rates, context selection, arithmetic interval rules,
transform selection, block framing, or public ABI. Valid encoded bytes must
remain identical to the pristine bzip3 1.5.3 oracle.

An instrumented baseline profile on a large representative regular-datacube ZIP
placed `encode_bytes` at approximately 59% of sampled encode time. The exact
percentage is profiler- and specimen-dependent; it was used to select the work
surface, not as a release performance claim.

## Refactor

The upstream-shaped loop repeatedly spelled multidimensional member accesses for
every coded bit. rev0028 instead:

- binds the order-0, order-1, and APM table bases once per block;
- binds the current and previous order-1 rows once per source byte;
- binds the two adjacent APM cells once per coded bit; and
- updates the already-bound model cells rather than recomputing their addresses.

The compiler therefore receives direct row/cell relationships while the
algorithm and mutation order remain explicit. No table is copied, transposed,
resized, narrowed, or retained across blocks.

## Alias invariant

The current-symbol and previous-symbol order-1 rows intentionally alias when the
two history bytes are equal. The original algorithm reads both probabilities
before updating the current row. A careless pointer refactor could update the
shared cell before reading the previous-symbol probability and silently change
all later bytes.

Both encoder and decoder now state this invariant at the mutation site and
capture `p0`, `p1`, and `p2` before any update. The same read/update order is
maintained in both directions.

## Regression oracle

The strict `entropy_model_row_aliasing` group reuses active and pristine-oracle
encoder/decoder states for two passes over six deterministic input families.
Alternating passes reverse case order. Coverage includes:

- equal-history row aliasing and differing-history rows;
- run-context transitions;
- model reset across reused states;
- all four normal transform models (0, 2, 4, and 6);
- exact active/oracle encoded-size and byte identity; and
- exact decode under both implementations.

The representative external cohort separately requires every rev0028 frame to
match rev0027 byte for byte and reconstruct its input exactly.

The same bounded group exposed a separate imported-libsais signed-overflow
witness in the 32-bit 4k LMS gather path. That finding and its modulo-32-bit
marker-transfer repair are documented in `docs/LIBSAIS_UB_AUDIT.md`. It is not
part of the entropy addressing optimization, but keeping the witness in this
group ensures the newly reached path remains sanitizer-covered.

## Performance witness and limits

A one-round randomized paired local CLI witness covered 18 external regular-
datacube ZIPs, 98,376,644 input bytes, and 104 one-MiB blocks. Baseline and
candidate order was randomized within the run; output used the production atomic
publication path on temporary memory-backed storage.

- compression aggregate: 10.801890 s to 9.398659 s (`-12.991%`);
- decompression aggregate: 10.422643 s to 9.679951 s (`-7.126%`);
- candidate was faster on 18/18 compression and 16/18 decompression specimens;
  the two decompression reversals were tiny archives where startup noise is a
  material fraction of elapsed time.

These numbers are a host- and run-specific witness, not a universal throughput,
latency, energy, or service-level claim. The release promotes the compatible
addressing refactor because byte identity and exact reconstruction are hard
gates; timing remains evidence to be remeasured on each deployment host.

## Rejected or deferred variants

A fixed-count rewrite of the eight-bit context walk and additional `restrict`
annotations did not establish a consistent advantage and were not retained. A
wide LZP comparison prototype changed compatible output behavior and was
rejected. rev0028 contains only the entropy table-addressing refactor described
above.
