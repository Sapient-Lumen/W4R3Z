# Testing strategy

## Automated CTest coverage

`cpp_api_roundtrip` covers:

- source-like highly repetitive bytes;
- every byte value repeated across a block;
- deterministic incompressible/random data;
- C++ move ownership;
- codec version identity;
- high-level in-memory frame round trips for exact block-size random and repeated inputs, tested through the matching library API rather than the distinct CLI framing.

`cli_roundtrip` covers:

- multi-worker compression, test, and decompression;
- paths containing spaces;
- byte-for-byte restored output;
- rejection of a negative encoded block length.

## Sanitizers

The Debug sanitizer configuration enables AddressSanitizer and UndefinedBehaviorSanitizer on the codec, CLI, tests, and research tools. The release archive records a clean CTest run with leak detection and `halt_on_error` enabled.

## Differential validation

The immutable upstream tree is compiled separately as C99 for differential work; it is never linked into bzip4. Validation includes:

- bzip4 encode -> upstream bzip3 decode;
- upstream bzip3 encode -> bzip4 decode;
- identical output archives for ordinary supported CLI inputs and settings;
- exact restored input hashes.

## Next testing layers

- property-based generation across every boundary size;
- fuzzing of BZ3v1 headers and blocks;
- allocation-failure injection;
- large-block and 32-bit-host limits;
- cross-endian and non-x86 builds;
- thread-creation failure handling;
- corpus regression snapshots with expected sizes and hashes;
- transform-specific round-trip and adversarial tests before any `.bz4` format ships.
