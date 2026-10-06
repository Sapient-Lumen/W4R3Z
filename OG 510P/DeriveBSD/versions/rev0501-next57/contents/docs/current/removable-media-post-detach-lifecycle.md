# Current removable-media post-detach lifecycle

This current view summarizes the runtime state machine accepted in `2026-05-30r521`.

The lane family is `removable-media-local-fallback`; `post_detach` in artifact kinds marks the phase. The old `removable-media-local-post-detach` family string is retired.

## State order

1. r504 contract: `removable.media.local.post_detach.contract`
2. r505 FreeBSD launch evidence
3. r506 recovery evidence
4. r507 query projection
5. r508 export bundle
6. r509 revocation tombstone
7. r510 denial receipt
8. r511 fresh-authority receipt
9. r512 fresh-authority consumption
10. r513 successor-index cutover
11. r514 successor-index checkpoint
12. r515 reader admission
13. r516 reader use
14. r517 reader-use ledger
15. r518 reader-use ledger retention
16. r519 retention expiry
17. r520 retention-expiry enforcement receipt
18. r521 enforcement ledger root
19. r521 post-expiry fresh-authority recovery
20. r521 allowlisted support projection
21. r521 FreeBSD backend enforcement evidence

## Runtime floor

An expired compacted root can no longer produce a new observation, export, rehydration, or raw support/debug surface. It can produce a typed denial path or a fresh-authority path that admits only a successor root.


r529 adds `removable.media.local.post_detach.export.bundle.deletion.receipt` so export cleanup is a terminal, CAS-ledgered transition rather than a flag on access.

Last updated: 2026-05-30r521
