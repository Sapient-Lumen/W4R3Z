# AnonSync rev0942

Mission: replace Resilio Sync with a practical C++ folder-sync product whose
shipping peer service supports direct, Tor, and I2P routes.

## Product change

- New reconciliation transfers use one durable raw receiver prefix instead of
  one private file per range followed by a second whole-file assembly.
- The canonical prefix basename binds whole SHA-256, total size, and committed
  contiguous length.
- Range bytes are written at the exact next offset, fsynced, and committed by an
  atomic no-replace rename plus directory fsync.
- A longer crash tail is truncated to the basename cutpoint on fresh-process
  continuation.
- At completion, the same inode is whole-file verified and renamed directly to
  the digest payload name before remote operation metadata is admitted.
- An interrupted rev0941 range-file transfer remains resumable through the
  retained compatibility owner without minting a competing prefix.

## Audit corrections

- The draft retained a pre-rename `stat`, but rename legitimately changes ctime;
  a correct transfer could reject its own committed inode. Rev0942 refreshes and
  binds the observation after every commit rename.
- Physical transient bytes and admission reservation are separate. A short
  prefix reports exact bytes on disk while reserving its complete declared file,
  preventing partial transfers from overcommitting completion capacity.
- The hot path avoids rehashing unrelated payloads, while complete scans remain
  at new-owner admission and final publication as correctness oracles.

## Explicit limits

This remains sequential range resume, not block reuse or delta synchronization.
The current file ceiling is 64 MiB; one-byte edits retransmit the complete file;
some payload APIs still materialize whole files; continuation still traverses
private basenames; and payload/partial reachability and garbage collection remain
absent.

Archive: `AnonSync-rev0942-2026.07.29.07.27-prefixcommit-crashtail-capacityreserve-rosecutpoint.zip`
