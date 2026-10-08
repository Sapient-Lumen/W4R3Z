# AnonSync rev0943

Mission: replace Resilio Sync with a practical C++ folder-sync product whose
shipping peer service supports direct, Tor, and I2P routes.

## Product change

- Shipping local observation no longer stores a complete regular file in a
  `std::string`; it hashes a retained descriptor with bounded positional reads.
- New durable payload insertion streams from that descriptor into the private
  content store while independently recomputing SHA-256.
- Remote materialization opens the exact digest-named payload and streams it
  through the existing rooted atomic publication state machine.
- Ordinary share setup remains 64 MiB by default. An explicit deployment may
  admit up to 4 GiB independently of the 4 MiB range and 64 MiB page limits.
- The real two-process reconciliation proof transfers 64 MiB plus 4 KiB through
  sixteen ranges and one fresh-process continuation, then materializes exact
  bytes without a whole-file C++ allocation.

## Audit and refactor

- Two divergent unfinished worktrees had split the implementation from newer
  tests. GCC and sanitizer claims from those siblings could not describe one
  release. Rev0943 consolidates both into one canonical tree and reruns every
  release gate there.
- A draft generic public writer callback was rejected. The public atomic
  publication seam now accepts only one borrowed regular-file descriptor, exact
  source metadata, and expected SHA-256.
- Source offset preservation, source mutation, wrong digest, exact extent,
  rooted destination, payload-store descriptor selection, and structural
  ownership are covered by the same canonical test/audit set.
- Reconciliation no longer requires one response page to accommodate a complete
  durable payload. The legacy one-frame delivery/effect path remains capped at
  4 MiB rather than inheriting a larger durable file ceiling.

## Explicit limits

Four GiB is an unqualified admission ceiling, not production large-file support.
The largest exercised file is 64 MiB plus 4 KiB. Local admission reads new bytes
once for observation and again for durable insertion. Payload-store mutation and
snapshot paths still traverse and hash durable content, one-byte edits still
retransmit the whole file, sparse layout is not preserved, and reachability/GC,
ENOSPC/quota, multi-gigabyte restart, live public overlays, rename/directories,
and ordinary-user conflict/restore UX remain incomplete.

Archive: `AnonSync-rev0943-2026.07.29.10.27-streamingfiles-canonicaltree-descriptorfence-roseanchor.zip`
