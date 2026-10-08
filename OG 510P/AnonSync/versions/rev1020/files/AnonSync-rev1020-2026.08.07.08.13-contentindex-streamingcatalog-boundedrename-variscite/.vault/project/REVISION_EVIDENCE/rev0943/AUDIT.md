# Rev0943 focused audit

## Mission guard

This change advances the Resilio-replacement product spine. It removes
whole-file memory ownership from ordinary C++ file admission and apply while
retaining the same direct, Tor, and I2P peer service. Descriptor and durability
rules are implementation discipline, not a competing mission.

## Severe release-process defect corrected: split source truth

The unfinished revision existed in two divergent worktrees. One contained the
later descriptor-specific implementation; the other contained independent tests
and structural audits plus an older generic callback design. GCC had validated
one tree and ASan another. Those results were real but could not be aggregated
into a release that did not exist. Rev0943 ports the independent tests onto the
narrower implementation and reruns all gates on one canonical tree.

## Authority reduction: no public arbitrary writer

A public `std::function<void(int)>` seam would let arbitrary code execute while
the atomic publisher retained a private temporary descriptor and rooted
namespace authority. The released API accepts only an opened regular-file
descriptor, its exact metadata, and its expected SHA-256. The writer adaptation
is private to the translation unit. Source metadata and digest are re-proved,
the shared offset is untouched, and exact destination extent is required before
namespace publication.

## Product correction: streamed local and remote files

The folder observer hashes in bounded chunks and retains the descriptor rather
than the bytes. Payload insertion copies and hashes directly into durable
storage. Remote apply opens the selected immutable payload and streams it into
the existing rooted atomic state machine. The process proof crosses the former
64 MiB complete-file/page coupling with a 64 MiB-plus-4 KiB payload continued
across fresh authenticated sessions.

## Remaining performance defect

New local content is still read twice, and the payload store still performs
complete namespace traversal and hashing in mutation/snapshot paths. Repeating
that work per file can become the dominant cost for large small-file sets. This
must be replaced by a directly addressable/indexed hot path checked against the
complete-store oracle, not by weakening source mutation or digest checks.

## Remaining product risk

The 4 GiB ceiling is not qualified. Multi-gigabyte ENOSPC/quota/restart, sparse
files, changed-block reuse, reachability/GC, live public Tor/I2P, rename and
empty directories, cross-platform fidelity, and usable conflict/restore flows
remain open.
