# rev0309 source-hash anchor firebreak refactor

## Problem

Rev0308 made lane provenance stricter, but lane provenance is not the whole
chain. Several records carry a copied source snapshot plus a hash. If the guard
revalidates the referenced source file but does not compare the copied hash to
that file's current bytes, stale snapshot metadata can survive longer than it
should.

That matters most near activation: first-packet decisions source post-decision
change tickets, and post-decision change tickets source activation/live-window
entry and live-window cards.

## Change

The field guard now enforces the hash anchor at those handoffs:

```text
source_first_packet_decision.decision_sha256 == sha256(first-packet-decision.json)
source_post_decision_change_ticket.ticket_sha256 == sha256(post-decision-change-ticket.json)
```

The comparison is in the shared integrity guard rather than in only one command
path, so direct guard checks, generated records, router-selected artifacts, and
release validators all inherit the same boundary.

## Regression coverage

- `tools/check_ft0181_post_decision_change_ticket.py` mutates a valid ticket's
  copied decision hash and requires the guard to block it.
- `tools/check_ft0181_live_window_card.py` mutates a valid live-window card's
  copied ticket hash and requires the guard to block it.

## Boundary

This is not evidence acceptance. It only prevents stale or copied local metadata
from making the field rail look safer than it is. `FT-0181` remains live and
blocked on real owner-reviewed material or a documented route block.
