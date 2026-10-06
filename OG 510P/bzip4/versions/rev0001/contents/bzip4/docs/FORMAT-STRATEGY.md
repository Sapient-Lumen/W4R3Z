# Format strategy

## rev0001: compatibility mode

The current CLI reads and writes BZ3v1:

```text
"BZ3v1" | block_size_le32 | repeated { compressed_size_le32, original_size_le32, block_bytes }
```

This baseline is valuable because upstream tools can validate ordinary CLI archives and because every future ratio result can be compared against an unchanged inner codec.

### Important upstream framing distinction

The compatible in-memory `bz3_compress`/`bz3_decompress` API uses a related but distinct upstream frame layout:

```text
"BZ3v1" | block_size_le32 | block_count_le32 | repeated { compressed_size_le32, original_size_le32, block_bytes }
```

The CLI layout omits `block_count_le32`. Sharing the same five-byte magic does not make these byte streams interchangeable. Rev0001 preserves both upstream interfaces and documents the distinction rather than silently changing either format.

## Why not rename the magic immediately

A project name is not a format version. Changing `BZ3v1` to a cosmetic `BZ4` magic without new semantics would break interoperability while adding no capability. A new format should pay for itself by representing features such as transforms, dedup references, stream manifests, stronger checksums, indexes, or resource bounds.

## Future container requirements

A candidate bzip4 container should support:

- explicit version and feature flags;
- independently bounded stream and output sizes;
- transform identifiers and parameters;
- inner codec identifiers, allowing BZ3 blocks as one method;
- per-stream checksums and an optional whole-archive digest;
- optional indexes without requiring them for sequential decoding;
- unknown-feature rejection rather than unsafe guessing;
- deterministic canonical metadata encoding;
- recovery boundaries and corruption localization;
- forward-compatible skippable metadata;
- a small decoder path for constrained systems.

## Layer model

```text
original bytes
  -> reversible domain transform (optional)
  -> similarity ordering / stream split (optional)
  -> long-range dedup references (optional)
  -> block codec selection (BZ3 baseline or future alternatives)
  -> checksums, index, and container framing
```

Each layer must be independently testable. The decoder should be able to reject impossible resource requests before processing inner compressed data.

## Compatibility modes

A future CLI can expose clear choices:

- `--format=bz3`: strict BZ3v1 output readable by bzip3;
- `--format=bz4`: new container with selected transforms;
- `--auto`: choose only among bzip4 methods, while reporting the decision;
- `--no-transform`: bzip4 container around the baseline codec for diagnostic isolation.

No such `.bz4` mode exists in rev0001.
