# toxsync v1 formats

All integers are unsigned little-endian. Decoders reject nonzero reserved fields, inconsistent sizes, excessive resource requests, and trailing bytes.

## Target index (`.txi`)

Header, 64 bytes:

```text
0   8   magic: "TOXSYNC1"
8   2   format version = 1
10  2   header bytes = 64
12  4   block size
16  8   target size
24  8   block count
32 32   target SHA-256
```

Each block record is 24 bytes:

```text
0   4   rolling weak checksum
4   4   block length
8  16   fast 128-bit candidate fingerprint
```

The final block may be shorter than `block_size`. The whole-artifact SHA-256 is authoritative; the fast fingerprint is not an authenticity primitive.

## Treepack (`.treepack`)

The 16-byte header is `TXTREE1\0`, version 1, and a zero reserved word. Entries are strictly sorted by portable relative path. Each 20-byte entry header carries type, executable flag, path length, content length, and reserved fields, followed by UTF-8-agnostic path bytes and file bytes. An all-zero end entry terminates the stream.

v1 supports directories and regular files. It rejects symbolic links, device nodes, sockets, FIFOs, absolute paths, `.`/`..`, backslashes in received paths, noncanonical ordering, duplicate paths, resource-limit violations, and trailing bytes. It preserves only whether any executable bit was set; timestamps, ownership, ACLs, xattrs, sparse extents, and full permission modes are deliberately absent.

## Range request

The first transport codec is a fixed 64-byte request containing magic/version, request ID, artifact digest, target offset, requested length, and reserved bytes. The response framing is intentionally left to the IoTox transport layer so packetization, cancellation, and Tox file-transfer use can evolve independently.
