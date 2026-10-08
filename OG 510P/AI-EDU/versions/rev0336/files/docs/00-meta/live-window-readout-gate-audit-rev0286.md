# rev0286 live-window readout gate audit

## Risk addressed

The riskiest remaining post-activation gap was the terminal live-window handoff. A
`live-window-card.json` could reach `paused`, `rolled_back`, `completed_no_closure`,
or `quarantined`, and the router only told the maintainer to open the prose
readout gate. That was better than a direct service-record edit, but it left the
next high-risk action outside the executable rail: a terminal card could be
mistaken for enough basis to edit records, revise public language, move lifecycle
state, dispatch follow-up work, or imply closure.

## Repair

Rev0286 adds a scratch-local terminal readout seam instead of another registry:

- `tools/record_ft0181_live_window_readout.py`
- `tools/check_ft0181_live_window_readout.py`
- `make owner-live-window-readout`
- `owner_live_window_readout_integrity_error(...)` in `tools/ft0181_field_guards.py`
- router collection and routing in `tools/decide_ft0181_field_next_action.py`

A terminal card now routes to a bounded aggregate readout artifact. The readout
can source only the post-readout recheck due-date firebreak. It does not authorize service
record edits, lifecycle movement, custody, public language, acceptance, or
closure.

## Executable order after a live-window card

1. Nonterminal card states (`staged`, `active`) stop inside the card limits.
2. Terminal card states route to `make owner-live-window-readout ...`.
3. The readout revalidates the source card hash and terminal state.
4. The readout records only aggregate count classes, disposition, hashes, and
   route controls.
5. The router then stops at `ft0181-post-readout-action-dispatch.md`.

## Blocks added

The new readout gate blocks:

- nonterminal card states;
- disposition/card-state mismatches;
- source-truth class mismatches;
- aggregate readout counts below the source card;
- one-reviewer readouts;
- continue/rerun readouts with no bounded decision delta;
- rerun/no-change readouts with no field trim;
- raw learner data, protected facts, security payloads, live notes, screenshots,
  contact details, or public-claim-upgrade requests;
- outputs into controlled archive surfaces.

## Boundary

This is still not real evidence. It is a local firebreak that keeps terminal
window observations from laundering themselves into a post-readout dispatch,
public phrase, service-record edit, lifecycle state, or closure. `FT-0181`
remains live until the full real owner packet, import acceptance, readout,
dispatch, closeout, signoff, and closure checklist path is satisfied.
