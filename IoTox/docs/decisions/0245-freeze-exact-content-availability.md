# ADR 0245: Freeze exact content-v2 availability

Status: accepted construction prerequisite; live Agent and genuine-provider qualification remain
open, 2026-08-29.

## Context

ADR 0244 could stripe complete mirrors and fence a disappearing source, but it intentionally had no
wire representation for a partial store. Marking partial stores complete would turn absence into a
trial-and-error hint, defeat rarest-first scheduling, and make “complementary sources” an inflated
claim. The preserved toxsync scheduler already accepts exact little-endian availability windows and
the content engine can derive those windows from verified local CAS objects.

## Decision

Allocate canonical message types 30/31 under the still-dark content-v2 feature bit 29. A fixed
120-byte request binds namespace, frozen signed-HEAD record digest, page/chunk kind, first logical
index, and a bounded nonzero object count. Its correlated result echoes that identity and carries
exactly `ceil(count/8)` little-endian membership bytes. Counts are capped at 8,192 objects, keeping
the largest result below one IoTox frame. Unused tail bits, padding, and envelope fields are zero.

The source derives availability only from its local root manifest and content store. It rehashes the
root against HEAD and size/digest-verifies every claimed page or chunk. The same current
`sync.subscribe` proof and subscriber membership required for object reads gates inventory reads.
Responses share the publisher's bounded epoch/carrier/message-ID replay cache; exact replay returns
the retained bitmap and conflicting reuse fails.

The receiver accepts a bitmap only for its coordinator's exact current kind/first/count window and
only after independently reapplying ADR 0242 source authority. Source ID, principal, and HEAD cannot
be rebound. Tail bits fail closed. Sparse availability expires at every window advance; the source
must answer the new window explicitly. A complete-mirror declaration remains a separate optimized
entrance.

## Qualification

The owned registry now has 632 checks. Codec tests cover exact sizes, round trips, correlated frames,
maximum count, nonzero padding, bad tail bits, and envelope aliases. Local resolver tests prove a
removed CAS chunk clears exactly one verified membership bit. Publisher tests prove current
subscriber admission and replay without recomputation. A complete flat-content test splits every
window by even/odd global chunk index across two independently authorized writers, observes both
sources, fetches no chunk from the wrong source, advances multiple windows, and reconstructs the exact
frozen artifact.

## Consequences

- Complementary partial stores now have an exact bounded protocol and deterministic coordinator
  proof; they no longer need to masquerade as complete mirrors.
- Availability is scheduling truth only. It never selects a HEAD, authenticates bytes, commits an
  object, or grants activation.
- Bit 29 remains unadvertised. Durable Agent attempts, FileId/result/offer joining, combined CAS
  quota and authenticated reachability/GC, restart behavior, and genuine c-toxcore/Sandwurm evidence
  remain prerequisites.
