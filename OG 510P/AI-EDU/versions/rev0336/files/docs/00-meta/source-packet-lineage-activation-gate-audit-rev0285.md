# Source-packet lineage activation gate audit rev0285

## Risk named

Rev0284 made `active_change` require a scratch-local activation receipt. That
blocked the direct active-ticket bypass, but the receipt still had a subtler
false-completion hole: it could prove that *some* local source packet file
existed, without proving that the file was the same returned owner packet that
fed the intake bundle, workbench seed, workbench review, and first-packet
decision.

That matters because an unrelated local CSV can be created easily. If that file
could be named as the accepted `SRC2+` packet, the archive would still look like
it had moved from first-packet decision to real-packet activation even though the
actual reviewed source chain had not been preserved.

## Repair

Rev0285 adds a hash-lineage gate inside the existing executable seam rather than
adding a new registry surface.

`record_ft0181_activation_receipt.py` now reopens the decision chain:

1. `first-packet-decision.json`
2. the cited `workbench-review.json`
3. the cited `workbench-seed.json`
4. the seed's preserved `source_csv.sha256`

The activation receipt can be written only when `--source-packet` hashes to that
same `source_csv.sha256`. The receipt records the decision-source chain and sets
`source_packet.matches_decision_chain_source_csv_sha256=true`. The shared guard
recomputes every intermediate hash and rejects edited receipts, edited reviews,
edited seeds, unrelated packet files, archive-controlled packets, smoke markers,
weak source classes, and unsafe outputs.

## Executable behavior

The active-change path now has this order:

1. Proceed-capable workbench review remains `SRC2-CANDIDATE-NOT-ACCEPTED`.
2. First-packet decision remains `NOT_ACCEPTED` and `not_evidence`.
3. `ready_for_real_packet` stops without a live-window command.
4. Activation receipt requires the same source-packet hash as the decision-chain
   returned CSV hash.
5. Only that validated receipt can source an `active_change` ticket.
6. Only that guarded `active_change` ticket can source a live-window card.

## Boundary

This still does not create evidence, custody, acceptance, public-summary support,
or closure. It only prevents an unrelated local file from activating a decision
chain. The cube still needs a real accountable owner route, a real returned
owner-reviewed packet, accepted import/custody surfaces, a live-window readout,
and closure signoff before any stronger claim is allowed.

## Validation coverage

- `tools/check_ft0181_activation_receipt.py` now verifies that unrelated source
  packets with different hashes are blocked.
- `tools/check_ft0181_post_decision_change_ticket.py` inherits the lineage guard
  because `active_change` revalidates the receipt.
- `tools/check_ft0181_live_window_card.py` inherits the guarded active-ticket
  chain before any staged/live card.
- `tools/check_ft0181_field_next_action.py` exercises the ready stop, activation
  route, active-change route, and live-window route with the same source-packet
  hash preserved from seed to receipt.
