# Store/image distribution beyond binary caches (casync, CernVM-FS)

Most “binary cache” systems move whole artifacts. Some ecosystems distribute **filesystems** efficiently:
- content-addressed chunking
- HTTP/CDN-friendly transport
- dedup across versions

References:
- casync (content-addressable data synchronizer). https://github.com/systemd/casync
- casync design notes. https://0pointer.net/blog/casync-a-tool-for-distributing-file-system-images.html
- CernVM-FS overview (CAS + Merkle trees + HTTP-only). https://cvmfs.readthedocs.io/

## DeriveBSD direction

Optional transports for store + images:

1) **Chunked image distribution** (casync-like):
   - publish a chunk index bound to artifact digest
   - clients fetch missing chunks via HTTP

2) **Read-only store snapshots** (CernVM-FS-like):
   - publish store snapshots as Merkle catalogs
   - clients mount a snapshot view (fetch-on-demand)

These can reduce bandwidth and speed up “cold start” for:
- builder nodes
- microVM fleet rollouts

## Keep it optional

- OCI and simple HTTP caches remain the default.
- Alternative transports are adapters that must preserve signature/provenance semantics.

See RFC-0087.

See also: `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`.
