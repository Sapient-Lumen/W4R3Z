# rev0309 mission kernel

`rev0309` keeps the cube pointed at the same scarce event: a real
owner-reviewed `FT-0181` packet moving through the field lane without synthetic
or stale local records becoming evidence, activation authority, public support,
or closure. The archive still has no accepted owner packet, no accepted `SRC2+`
evidence, no real active-change window, no public-claim upgrade, and no closure.

## Heart of the work

The mission is now less about discovering the right doctrine and more about
protecting the narrow chain that would carry one real owner packet through the
archive. Rev0304 through rev0308 created the field lane, fixed clock drift, and
blocked checker/release scratch from masquerading as returned CSVs, activation
source packets, or local source-chain artifacts.

The next near-completion risk was subtler: a downstream record could preserve a
source hash in its snapshot while the integrity guard re-read the source file but
did not always compare the snapshot hash back to the current bytes at the exact
post-decision and live-window handoffs. That leaves room for stale metadata to
look more trustworthy than the file currently being sourced.

## rev0309 correction

`rev0309` anchors those hashes at the handoff points where the field rail gets
closest to activation:

- `source_first_packet_decision.decision_sha256` must match the referenced
  `first-packet-decision.json` before a post-decision change ticket can pass
  integrity.
- `source_post_decision_change_ticket.ticket_sha256` must match the referenced
  `post-decision-change-ticket.json` before activation/live-window entry briefs
  or live-window cards can pass integrity.

The patch adds regressions for stale decision-hash and ticket-hash snapshots. It
does not add a schema family, registry, queue item, or broader policy layer.

## Non-evidence boundary

The correction makes existing source-chain records harder to stale-copy or
launder. It does not contact an owner, import a real CSV, accept `SRC2+`, record
an active-change window, upgrade a public claim, mutate a service record, or
close `FT-0181`.
