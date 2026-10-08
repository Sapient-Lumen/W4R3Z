# Rev0948 research notes

Research was used to qualify the transaction and scan-efficiency claims, not to
copy another product's architecture.

## SQLite

Official WAL documentation says the historical large-WAL-transaction limitation
was removed in SQLite 3.11.0. Rev0948 therefore does not claim that a large
journal transaction is unsupported. Official transaction and isolation pages
state that `BEGIN IMMEDIATE` starts a write transaction immediately and excludes
another writer. The 4,096-path frontier is application backpressure: it bounds
pending C++ path strings, prepared row work, and the application-controlled
writer interval while leaving correctness independent of the selected default.

- https://www.sqlite.org/wal.html
- https://sqlite.org/lang_transaction.html
- https://sqlite.org/isolation.html

## Syncthing

Current Syncthing documentation says filesystem notifications avoid unnecessary
I/O and detect changes faster, while its FAQ notes that periodic scans of large
folders can cause resource spikes. This supports AnonSync's existing division:
watchers accelerate, but rooted scans retain repair authority. It does not prove
AnonSync performance or feature parity.

- https://docs.syncthing.net/users/tuning.html
- https://docs.syncthing.net/users/faq.html

## Inference

A path-count frontier is useful because bytes and path cardinality are
independent resource dimensions. It is not sufficient for huge-tree efficiency:
AnonSync still stores and sorts all immediate directory components and replays
the skipped prefix. The next index must preserve a complete rooted scanner as
rebuild and scrub authority rather than treating cached metadata as deletion
proof.
